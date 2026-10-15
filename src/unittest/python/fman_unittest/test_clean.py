# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
from io import BytesIO
from pathlib import Path
import stat
import json
import unittest
from unittest.mock import patch, Mock
from urllib.error import URLError
from zipfile import ZipFile, ZipInfo

from core.commands import _validate_plugin_archive, About, EnterDirectory
from core.github import _read_limited
from core.fs.zip import ZipFileSystem
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from fman.impl.application_context import DevelopmentApplicationContext
from fman.impl.metrics import Metrics
from fman.impl.nonexistent_shortcut_handler import NonexistentShortcutHandler


class CleanForkTest(unittest.TestCase):
	def test_arrow_bindings(self):
		path = ApplicationContext().get_resource('Plugins/Core/Key Bindings.json')
		with open(path, encoding='utf-8') as file:
			bindings = {entry['keys'][0]: entry['command'] for entry in json.load(file)}
		self.assertEqual('go_up', bindings['Left'])
		self.assertEqual('enter_directory', bindings['Right'])
		self.assertEqual('move_cursor_up', bindings['Up'])
		self.assertEqual('move_cursor_down', bindings['Down'])

	def test_unknown_shortcut_never_prompts(self):
		event, pane = Mock(), Mock()
		self.assertFalse(NonexistentShortcutHandler()(event, pane))
		self.assertEqual([], pane.mock_calls)
		self.assertEqual([], event.mock_calls)

	def test_right_arrow_enters_directory(self):
		pane = Mock()
		pane.get_file_under_cursor.return_value = 'file:///C:/example'
		with patch('core.commands.is_dir', return_value=True):
			EnterDirectory(pane)()
		pane.run_command.assert_called_once_with('open_directory', {'url': 'file:///C:/example'})

	def test_right_arrow_never_launches_file(self):
		pane = Mock()
		pane.get_file_under_cursor.return_value = 'file:///C:/example.exe'
		with patch('core.commands.is_dir', return_value=False):
			EnterDirectory(pane)()
		pane.run_command.assert_not_called()

	def test_right_arrow_with_no_selection(self):
		pane = Mock()
		pane.get_file_under_cursor.return_value = None
		EnterDirectory(pane)()
		pane.run_command.assert_not_called()

	def test_title_without_registration(self):
		context = DevelopmentApplicationContext()
		self.assertEqual('fman Clean', context._get_main_window_title())
		self.assertFalse(hasattr(context, 'is_licensed'))
		self.assertFalse(hasattr(context, 'splash_screen'))

	def test_about_credits_not_registration(self):
		with patch('core.commands.show_alert') as alert:
			About(None)()
		message = alert.call_args.args[0]
		self.assertIn('Michael Herrmann', message)
		self.assertIn('MIT', message)
		self.assertNotIn('Not registered', message)

	def test_metrics_are_ephemeral_bounded_names_only(self):
		metrics = Metrics()
		for i in range(300):
			metrics.track(str(i), {'private': 'discarded'})
		self.assertEqual(256, len(metrics.past_events))
		self.assertEqual('299', metrics.past_events[-1])
		self.assertEqual({'past_events'}, set(vars(metrics)))

	def test_resource_lookup(self):
		context = ApplicationContext()
		self.assertTrue(Path(context.get_resource('Plugins/Core')).is_dir())
		with self.assertRaises(FileNotFoundError):
			context.get_resource('not-a-resource')
		with self.assertRaises(ValueError):
			context.get_resource('../../outside')

	def test_download_limit(self):
		self.assertEqual(b'abc', _read_limited(BytesIO(b'abc'), limit=3))
		with self.assertRaises(URLError):
			_read_limited(BytesIO(b'abcd'), limit=3)

	def test_modern_7zip_fractional_timestamps(self):
		filesystem = ZipFileSystem.__new__(ZipFileSystem)
		info = filesystem._read_file_info(iter([
			'Path = example.txt', 'Size = 1',
			'Modified = 2026-09-20 10:43:50.1234567', ''
		]))
		self.assertEqual(123456, info.mtime.microsecond)

	def test_valid_plugin_archive(self):
		_validate_plugin_archive('Example', self.archive('repo/main.py'))

	def test_unsafe_plugin_names(self):
		for name in ('', '..', '.', '../escape', 'C:escape', 'a\\b'):
			with self.subTest(name=name), self.assertRaises(ValueError):
				_validate_plugin_archive(name, self.archive('repo/main.py'))

	def test_unsafe_archive_paths(self):
		for path in ('../escape', '/absolute', 'C:/escape', 'repo/../escape',
			'repo\\..\\escape', '//server/share', 'repo//file'):
			with self.subTest(path=path), self.assertRaises(ValueError):
				_validate_plugin_archive('Example', self.archive(path))

	def test_plugin_symlinks_rejected(self):
		info = ZipInfo('repo/link')
		info.create_system = 3
		info.external_attr = (stat.S_IFLNK | 0o777) << 16
		with self.assertRaises(ValueError):
			_validate_plugin_archive('Example', self.archive(info))

	@staticmethod
	def archive(path):
		buffer = BytesIO()
		with ZipFile(buffer, 'w') as archive:
			archive.writestr(path, 'example')
		return buffer.getvalue()
