# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
# Create an unambiguous per-user launcher for this repository's compiled build.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$executable = Join-Path $root 'target\fman-clean\fman-clean.exe'
if (-not (Test-Path $executable)) { throw 'Build first: python build.py freeze' }
$desktop = [Environment]::GetFolderPath('Desktop')
if (-not (Test-Path $desktop)) { throw 'No writable desktop directory found.' }
$destination = Join-Path $desktop 'fman Clean (Windows).lnk'
$shell = New-Object -ComObject WScript.Shell
$link = $shell.CreateShortcut($destination)
if ((Test-Path $destination) -and $link.TargetPath -ne $executable) {
    throw 'A shortcut with this name already points elsewhere. Rename it explicitly before replacing it.'
}
$link.TargetPath = $executable
$link.WorkingDirectory = Split-Path $executable -Parent
$link.IconLocation = "$executable,0"
$link.Description = 'SynrgStudio fman Clean - current Windows build'
$link.Save()
Write-Host 'Created desktop shortcut: fman Clean (Windows)'
