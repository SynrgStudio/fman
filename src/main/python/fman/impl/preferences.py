# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""Validated, atomic Windows preferences, independent of plugin JSON state."""
import json
import os
from pathlib import Path
import tempfile

DEFAULTS = {
	'font_family': 'Segoe UI', 'font_size': 10, 'show_hidden_files': False,
	'show_parent_entry': True, 'everything_enabled': True, 'everything_dll': '',
	'editor_exe': '', 'terminal_exe': '',
}


def validate(values):
	result = dict(DEFAULTS)
	for key, default in DEFAULTS.items():
		value = values.get(key, default)
		if isinstance(default, bool):
			if type(value) is bool:
				result[key] = value
		elif key == 'font_size':
			if type(value) is int and 8 <= value <= 32:
				result[key] = value
		elif isinstance(value, str) and len(value) <= 32768 and not any(c in value for c in ('\x00', '\n', '\r')):
			result[key] = value
	return result


class Preferences:
	def __init__(self, directory):
		self.path = Path(directory) / 'Local' / 'Preferences.json'
		try:
			data = json.loads(self.path.read_text(encoding='utf-8'))
		except (OSError, ValueError):
			data = {}
		self.values = validate(data if isinstance(data, dict) else {})

	def save(self, updates):
		values = validate({**self.values, **updates})
		self.path.parent.mkdir(parents=True, exist_ok=True)
		fd, temporary = tempfile.mkstemp(dir=self.path.parent, suffix='.tmp')
		try:
			with os.fdopen(fd, 'w', encoding='utf-8') as stream:
				json.dump(values, stream, indent=2, ensure_ascii=False)
				stream.write('\n')
			os.replace(temporary, self.path)
		finally:
			if os.path.exists(temporary):
				os.unlink(temporary)
		self.values = values
