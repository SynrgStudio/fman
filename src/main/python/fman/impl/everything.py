# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""Optional Everything SDK connector. No database reads, HTTP, or elevation.

Native calls run in a timeout-bounded helper process so even a hung IPC server
or a faulty user-selected SDK DLL cannot freeze the UI.
"""
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile


def default_dll_path():
	return Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'fman-clean/tools/everything/Everything64.dll'


def search(query, preferences, limit=40, timeout=4):
	if sys.platform != 'win32' or not preferences.get('everything_enabled', True) or len(query.strip()) < 2:
		return []
	# This provider is deliberately name/path-only, not a disk content scanner.
	if re.search(r'\b[a-z0-9_]*content\s*:', query, flags=re.IGNORECASE):
		return []
	dll = Path(preferences.get('everything_dll') or default_dll_path())
	if not dll.is_absolute() or not dll.is_file():
		return []
	limit = max(1, min(int(limit), 100))
	with tempfile.TemporaryDirectory(prefix='fman-everything-') as directory:
		output = Path(directory) / 'results.json'
		command = [sys.executable]
		environment = os.environ.copy()
		if not getattr(sys, 'frozen', False):
			command += ['-m', 'fman.main']
			environment['PYTHONPATH'] = str(Path(__file__).resolve().parents[2]) + os.pathsep + environment.get('PYTHONPATH', '')
		command += ['--everything-worker', str(dll), query, str(limit), str(output)]
		try:
			subprocess.run(command, timeout=timeout, check=True, stdin=subprocess.DEVNULL,
				stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
				creationflags=subprocess.CREATE_NO_WINDOW, env=environment)
			if output.stat().st_size > 8 * 1024 * 1024:
				return []
			data = json.loads(output.read_text(encoding='utf-8'))
		except (OSError, ValueError, subprocess.SubprocessError):
			return []
		if not isinstance(data, list):
			return []
		return [(item['path'], item['folder']) for item in data[:limit]
			if isinstance(item, dict) and isinstance(item.get('path'), str)
			and type(item.get('folder')) is bool and os.path.isabs(item['path'])]


def helper(dll_path, query, limit, output):
	"""Child-only entry point. The DLL must be explicitly installed/trusted."""
	import ctypes
	from ctypes import wintypes
	from threading import Timer
	# Bound orphan helpers too if the GUI exits while native IPC is stuck.
	watchdog = Timer(6, lambda: os._exit(0))
	watchdog.daemon = True
	watchdog.start()
	data = []
	try:
		dll_path = str(Path(dll_path).resolve(strict=True))
		dll = ctypes.WinDLL(dll_path)
		functions = {
			'Everything_Reset': ([], None),
			'Everything_SetSearchW': ([wintypes.LPCWSTR], None),
			'Everything_SetMax': ([wintypes.DWORD], None),
			'Everything_SetRequestFlags': ([wintypes.DWORD], None),
			'Everything_QueryW': ([wintypes.BOOL], wintypes.BOOL),
			'Everything_GetNumResults': ([], wintypes.DWORD),
			'Everything_GetResultFullPathNameW': ([wintypes.DWORD, wintypes.LPWSTR, wintypes.DWORD], wintypes.DWORD),
			'Everything_IsFolderResult': ([wintypes.DWORD], wintypes.BOOL),
		}
		for name, (arguments, result) in functions.items():
			getattr(dll, name).argtypes = arguments
			getattr(dll, name).restype = result
		dll.Everything_Reset()
		dll.Everything_SetSearchW(query)
		dll.Everything_SetMax(max(1, min(int(limit), 100)))
		dll.Everything_SetRequestFlags(3)  # filename and path, not file contents
		if dll.Everything_QueryW(True):
			for index in range(min(dll.Everything_GetNumResults(), 100)):
				buffer = ctypes.create_unicode_buffer(32768)
				length = dll.Everything_GetResultFullPathNameW(index, buffer, len(buffer))
				if 0 < length < len(buffer):
					data.append({'path': buffer.value, 'folder': bool(dll.Everything_IsFolderResult(index))})
	except (OSError, ValueError, AttributeError):
		pass
	try:
		Path(output).write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
	except OSError:
		pass  # The parent may already have removed its temporary directory.
	finally:
		watchdog.cancel()
