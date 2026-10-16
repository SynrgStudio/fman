# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
from pathlib import Path
import json
import subprocess
import tempfile
import unittest
from unittest.mock import patch, Mock
from types import SimpleNamespace
from fman.impl.application_context import DevelopmentApplicationContext
from threading import Event
from fman.impl.latest_worker import LatestWorker

from fman.impl.preferences import Preferences, validate, DEFAULTS
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from fman.impl.palette import path_items, matches
from fman.impl.everything import search, helper
from fman.impl.panels import load_preview


class LatestWorkerTest(unittest.TestCase):
	def test_only_latest_pending_task_runs(self):
		started, release, completed = Event(), Event(), Event()
		calls = []
		def function(value):
			calls.append(value)
			if value == 'first':
				started.set()
				release.wait(3)
			if value == 'third':
				completed.set()
			return value
		worker = LatestWorker(function)
		try:
			worker.submit(1, 'first')
			self.assertTrue(started.wait(2))
			worker.submit(2, 'second')
			worker.submit(3, 'third')
			release.set()
			self.assertTrue(completed.wait(2))
			self.assertEqual(['first', 'third'], calls)
		finally:
			release.set()
			worker.close()
			worker._thread.join(2)

	def test_close_discards_pending_task(self):
		started, release = Event(), Event()
		calls = []
		def function(value):
			calls.append(value)
			started.set()
			release.wait(3)
		worker = LatestWorker(function)
		try:
			worker.submit(1, 'first')
			self.assertTrue(started.wait(2))
			worker.submit(2, 'second')
			worker.close()
		finally:
			release.set()
			worker._thread.join(2)
		self.assertEqual(['first'], calls)


class PreferencesTest(unittest.TestCase):
	def test_existing_external_tool_arguments_are_preserved(self):
		settings = {'editor': {'args': [r'C:\Custom\Editor.exe', '--special', '{file}']},
			'terminal': {'args': [r'C:\Custom\Terminal.exe', '--profile', 'custom'], 'cwd': '{curr_dir}'}}
		context = SimpleNamespace(preferences=SimpleNamespace(values=dict(DEFAULTS)), app=Mock(), theme=Mock(), window=Mock())
		context.window.get_panes.return_value = []
		with patch('fman.load_json', return_value=settings), patch('fman.save_json'):
			DevelopmentApplicationContext.apply_preferences.__wrapped__(context)
		self.assertEqual('--special', settings['editor']['args'][1])
		self.assertEqual('custom', settings['terminal']['args'][-1])

	def test_explicit_tool_reset_restores_system_default(self):
		settings = {'editor': {'args': [r'C:\Custom\Editor.exe', '--special', '{file}']}}
		context = SimpleNamespace(preferences=SimpleNamespace(values=dict(DEFAULTS)), app=Mock(), theme=Mock(), window=Mock())
		context.window.get_panes.return_value = []
		with patch('fman.load_json', return_value=settings), patch('fman.save_json'):
			DevelopmentApplicationContext.apply_preferences.__wrapped__(context, {'editor_exe'})
		self.assertTrue(settings['editor']['args'][0].endswith('notepad.exe'))
		self.assertFalse(settings['editor']['shell'])

	def test_invalid_types_and_unknown_keys(self):
		values = validate({'font_size': True, 'show_hidden_files': 'yes', 'unknown': 2})
		self.assertEqual(DEFAULTS, values)

	def test_size_bounds_and_control_characters(self):
		values = validate({'font_size': 999, 'font_family': 'bad\nfont'})
		self.assertEqual(10, values['font_size'])
		self.assertEqual('Segoe UI', values['font_family'])

	def test_save_and_reload(self):
		with tempfile.TemporaryDirectory() as directory:
			preferences = Preferences(directory)
			preferences.save({'font_size': 14, 'show_hidden_files': True})
			self.assertEqual(14, Preferences(directory).values['font_size'])
			self.assertTrue(Preferences(directory).values['show_hidden_files'])

	def test_corrupt_json(self):
		with tempfile.TemporaryDirectory() as directory:
			p = Path(directory) / 'Local'
			p.mkdir()
			(p / 'Preferences.json').write_text('[]', encoding='utf-8')
			self.assertEqual(DEFAULTS, Preferences(directory).values)

	def test_atomic_failure_keeps_old_file(self):
		with tempfile.TemporaryDirectory() as directory:
			preferences = Preferences(directory)
			preferences.save({'font_size': 12})
			with patch('fman.impl.preferences.os.replace', side_effect=OSError('blocked')):
				with self.assertRaises(OSError):
					preferences.save({'font_size': 16})
			self.assertEqual(12, Preferences(directory).values['font_size'])
			self.assertFalse(list(Path(directory).rglob('*.tmp')))


class PaletteTest(unittest.TestCase):
	def test_windows_shortcuts_keep_both_file_operation_styles(self):
		context = ApplicationContext()
		with open(context.get_resource('Plugins/Core/Key Bindings (Windows).json'), encoding='utf-8') as stream:
			bindings = {entry['keys'][0]: entry['command'] for entry in json.load(stream)}
		self.assertEqual('copy_to_clipboard', bindings['Ctrl+C'])
		self.assertEqual('cut', bindings['Ctrl+X'])
		self.assertEqual('paste', bindings['Ctrl+V'])
		self.assertEqual('unified_palette', bindings['Ctrl+P'])
		self.assertNotIn('Ctrl+Shift+P', bindings)
		with open(context.get_resource('Plugins/Core/Key Bindings.json'), encoding='utf-8') as stream:
			bindings = {entry['keys'][0]: entry['command'] for entry in json.load(stream)}
		self.assertEqual('copy', bindings['F5'])
		self.assertEqual('move', bindings['F6'])

	def test_fuzzy_match(self):
		self.assertTrue(matches('Open Settings', 'ost'))
		self.assertFalse(matches('Open Settings', 'zzz'))

	def test_command_prefix_never_queries_files(self):
		with patch('fman.impl.palette.everything_search') as backend:
			self.assertEqual([], path_items('> copy', {}, '', {}))
			backend.assert_not_called()

	def test_local_paths_and_duplicates(self):
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory) / 'Example.txt'
			path.write_text('test', encoding='utf-8')
			with patch('fman.impl.palette.everything_search', return_value=[(str(path), False)]):
				items = path_items('example', {}, directory, {})
			self.assertEqual(1, len(items))
			self.assertEqual('path', items[0].value.kind)
			self.assertFalse(items[0].value.folder)

	def test_direct_path_completion_in_current_directory(self):
		with tempfile.TemporaryDirectory() as directory:
			(Path(directory) / 'Child').mkdir()
			with patch('fman.impl.palette.everything_search', return_value=[]):
				items = path_items(directory + '/', {}, directory, {})
			self.assertIn(str(Path(directory) / 'Child'), [item.value.target for item in items])


class EverythingTest(unittest.TestCase):
	def test_disabled(self):
		with patch('fman.impl.everything.subprocess.run') as run:
			self.assertEqual([], search('example', {'everything_enabled': False}))
			run.assert_not_called()

	def test_content_queries_are_not_delegated(self):
		with patch('fman.impl.everything.subprocess.run') as run:
			self.assertEqual([], search('content:private', {'everything_enabled': True}))
			run.assert_not_called()

	def test_missing_connector_is_silent(self):
		with patch('fman.impl.everything.subprocess.run') as run:
			self.assertEqual([], search('example', {'everything_dll': 'missing.dll'}))
			run.assert_not_called()

	def test_timeout_is_silent(self):
		with tempfile.TemporaryDirectory() as directory:
			dll = Path(directory) / 'test.dll'
			dll.write_bytes(b'test')
			with patch('fman.impl.everything.subprocess.run', side_effect=subprocess.TimeoutExpired('helper', 4)):
				self.assertEqual([], search('example', {'everything_dll': str(dll)}))

	def test_helper_with_missing_dll(self):
		with tempfile.TemporaryDirectory() as directory:
			output = Path(directory) / 'results.json'
			helper(str(Path(directory) / 'missing.dll'), 'test', 5, output)
			self.assertEqual([], json.loads(output.read_text(encoding='utf-8')))


class PreviewTest(unittest.TestCase):
	def test_text_is_read_only(self):
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory) / 'example.txt'
			path.write_text('<script>not HTML</script>', encoding='utf-8')
			self.assertEqual(('text', '<script>not HTML</script>'), load_preview(path))
			self.assertEqual('<script>not HTML</script>', path.read_text(encoding='utf-8'))

	def test_text_limit(self):
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory) / 'example.txt'
			path.write_bytes(b'x' * (220 * 1024))
			self.assertIn('truncated', load_preview(path)[1])

	def test_binary_and_executable_are_never_launched(self):
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory) / 'example.bin'
			path.write_bytes(b'abc\x00xyz')
			self.assertIn('Binary', load_preview(path)[1])
			path = Path(directory) / 'example.exe'
			path.write_bytes(b'not really executable')
			self.assertIn('not supported', load_preview(path)[1])

	def test_directory_stats_are_not_recursive(self):
		with tempfile.TemporaryDirectory() as directory:
			(Path(directory) / 'child').mkdir()
			(Path(directory) / 'child/deep.txt').write_text('deep', encoding='utf-8')
			(Path(directory) / 'file.txt').write_text('top', encoding='utf-8')
			text = load_preview(directory)[1]
			self.assertIn('Files: 1', text)
			self.assertIn('Folders: 1', text)

	def test_missing_file_is_nonfatal(self):
		self.assertIn('No regular file', load_preview('not-a-real-preview-file')[1])
