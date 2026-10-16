# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
# Interactive desktop test: real OS keys, only sent while our child owns focus.
param([string]$Executable)
$ErrorActionPreference='Stop'
$repo=Split-Path $PSScriptRoot -Parent
if (-not $Executable) { $Executable=Join-Path $repo 'target\fman-clean\fman-clean.exe' }
$versionText=[IO.File]::ReadAllText((Join-Path $repo 'src\main\python\fman\_version.py'))
$expectedVersion=[regex]::Match($versionText,"VERSION = '([^']+)'").Groups[1].Value
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class FmanWindowProbe {
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hwnd);
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
 [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
 [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool attach);
 [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hwnd);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hwnd, int mode);
 public static void Activate(IntPtr hwnd) {
  uint pid; uint current=GetCurrentThreadId();
  uint foreground=GetWindowThreadProcessId(GetForegroundWindow(),out pid);
  uint target=GetWindowThreadProcessId(hwnd,out pid);
  if(foreground!=0 && foreground!=current) AttachThreadInput(current,foreground,true);
  if(target!=current) AttachThreadInput(current,target,true);
  try { ShowWindow(hwnd,9); BringWindowToTop(hwnd); SetForegroundWindow(hwnd); }
  finally {
   if(target!=current) AttachThreadInput(current,target,false);
   if(foreground!=0 && foreground!=current) AttachThreadInput(current,foreground,false);
  }
 }
}
'@
$temp=Join-Path ([IO.Path]::GetTempPath()) ('fman-frozen-keys-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory $temp | Out-Null
$profile=Join-Path $temp 'profile'
$files=Join-Path $temp 'files'
New-Item -ItemType Directory $files | Out-Null
[IO.File]::WriteAllText((Join-Path $files 'example.txt'),'Frozen keyboard preview fixture')
$oldProfile=$env:FMAN_DATA_DIRECTORY
$env:FMAN_DATA_DIRECTORY=$profile
$previous=[FmanWindowProbe]::GetForegroundWindow()
$process=$null
try {
 $process=Start-Process -FilePath $Executable -ArgumentList ('"'+$files+'" "'+$files+'"') -PassThru
 for($i=0;$i -lt 100;$i++) {
  Start-Sleep -Milliseconds 100
  $process.Refresh()
  if($process.HasExited) {throw 'App exited during startup'}
  if($process.MainWindowHandle -ne [IntPtr]::Zero) {break}
 }
 $handle=$process.MainWindowHandle
 if($handle -eq [IntPtr]::Zero){throw 'No main window'}
 [FmanWindowProbe]::Activate($handle)
 Start-Sleep -Seconds 3
 [uint32]$foregroundOwner=0
 [FmanWindowProbe]::GetWindowThreadProcessId([FmanWindowProbe]::GetForegroundWindow(),[ref]$foregroundOwner) | Out-Null
 # Send-Key retries activation and verifies the owning PID before any input.
 $window=[System.Windows.Automation.AutomationElement]::FromHandle($handle)
 if(-not $window.Current.Name.EndsWith($expectedVersion)){throw 'Stale executable: title does not match source version'}
 function Find-Visible([string]$name) {
  $condition=New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty,$name)
  $items=$window.FindAll([System.Windows.Automation.TreeScope]::Descendants,$condition)
  foreach($item in $items){ if(-not $item.Current.IsOffscreen){return $item} }
  return $null
 }
 function Wait-Visible([string]$name) {
  for($i=0;$i -lt 100;$i++) {
   $item=Find-Visible $name
   if($null -ne $item){return $item}
   Start-Sleep -Milliseconds 100
  }
  $all=$window.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
  $all | Select-Object -First 50 | ForEach-Object {Write-Host ('UI: '+$_.Current.Name+' visible='+(-not $_.Current.IsOffscreen))}
  throw ('Control not visible: '+$name)
 }
 function Send-Key([string]$key) {
  [uint32]$owner=0
  for($attempt=0;$attempt -lt 5;$attempt++) {
   [FmanWindowProbe]::GetWindowThreadProcessId([FmanWindowProbe]::GetForegroundWindow(),[ref]$owner) | Out-Null
   if($owner -eq $process.Id){break}
   [FmanWindowProbe]::Activate($handle)
   Start-Sleep -Milliseconds 200
  }
  if($owner -ne $process.Id){throw 'Test window lost focus to another process; no keys sent'}
  [System.Windows.Forms.SendKeys]::SendWait($key)
 }
 Send-Key '^,'
 $null=Wait-Visible 'Save preferences'
 Write-Host 'PASS: frozen Ctrl+comma opens settings'
 Send-Key '{ESC}'
 Start-Sleep -Milliseconds 400
 Send-Key '{F3}'
 $null=Wait-Visible ('Preview '+[char]0xB7+' F3')
 $null=Wait-Visible ('Copy text '+[char]0xB7+' Ctrl+Shift+C')
 Write-Host 'PASS: frozen F3 opens preview with content-copy control'
} finally {
 if($null -ne $process -and -not $process.HasExited) {
  $process.CloseMainWindow() | Out-Null
  if(-not $process.WaitForExit(7000)){ $process.Kill(); $process.WaitForExit() }
 }
 $env:FMAN_DATA_DIRECTORY=$oldProfile
 [FmanWindowProbe]::SetForegroundWindow($previous) | Out-Null
 Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue
}
