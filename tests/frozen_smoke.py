# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""Windows standalone startup/clean-exit check in a temporary profile."""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


def main():
	root = Path(__file__).resolve().parents[1]
	executable = root / 'target/fman-clean/fman-clean.exe'
	payload = executable.parent / '_internal'
	for notice in ('LICENSE', 'NOTICE', 'THIRD_PARTY.md', 'LICENSES/fman-MIT.txt',
		'dependency-notices/inventory.json'):
		assert (payload / notice).is_file(), 'Missing packaged notice: ' + notice
	user32 = ctypes.WinDLL('user32', use_last_error=True)
	callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
	user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
	user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
	user32.IsWindowVisible.argtypes = [wintypes.HWND]
	user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
	user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
	with tempfile.TemporaryDirectory(prefix='fman-clean-frozen-') as directory:
		env = os.environ.copy()
		env['FMAN_DATA_DIRECTORY'] = str(Path(directory) / 'profile')
		folder = Path(directory) / 'files'
		folder.mkdir()
		(folder / 'example.txt').write_text('standalone smoke', encoding='utf-8')
		process = subprocess.Popen([str(executable), str(folder), str(folder)], env=env)
		try:
			time.sleep(5)
			assert process.poll() is None, 'Executable exited before UI verification'
			windows = []
			@callback_type
			def collect(hwnd, _):
				pid = wintypes.DWORD()
				user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
				if pid.value == process.pid and user32.IsWindowVisible(hwnd):
					text = ctypes.create_unicode_buffer(512)
					user32.GetWindowTextW(hwnd, text, len(text))
					windows.append((hwnd, text.value))
				return True
			user32.EnumWindows(collect, 0)
			assert len(windows) == 1 and windows[0][1] == 'fman Clean', windows
			user32.PostMessageW(windows[0][0], 0x0010, 0, 0)
			assert process.wait(timeout=10) == 0, 'Unclean executable exit'
			print('PASS: standalone main window, no extra visible dialog, clean exit')
		finally:
			if process.poll() is None:
				process.kill()
				process.wait()


if __name__ == '__main__':
	main()
