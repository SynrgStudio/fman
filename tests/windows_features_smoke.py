# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""Real Windows UI: unified palette, settings, preview, parent row and F5."""
import os
from pathlib import Path
import sys
import tempfile
from time import monotonic
import traceback
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/main/python'))


def main():
	with tempfile.TemporaryDirectory(prefix='fman-windows-ui-') as directory:
		root = Path(directory).resolve()
		left, right = root / 'left', root / 'right'
		left.mkdir()
		right.mkdir()
		(left / 'example.txt').write_text('Preview fixture content', encoding='utf-8')
		os.environ['FMAN_DATA_DIRECTORY'] = str(root / 'profile')
		sys.argv = [sys.argv[0], str(left), str(right)]
		from fman.impl.application_context import get_application_context
		from fman.impl.palette import Entry
		from fman import QuicksearchItem
		from fman.url import as_url
		from PyQt5.QtCore import Qt, QTimer
		from PyQt5.QtTest import QTest
		from PyQt5.QtGui import QImage
		from PyQt5.QtWidgets import QApplication
		context = get_application_context()
		app = context.app
		image = QImage(8, 8, QImage.Format_RGB32)
		image.fill(Qt.red)
		assert image.save(str(left / 'sample.png'))
		result = [1]
		deadline = monotonic() + 75
		def fail(error):
			print('FAIL:', error)
			traceback.print_exc()
			app.exit(1)
		def step(function):
			def wrapped():
				try:
					assert monotonic() < deadline, 'UI check deadline exceeded'
					function()
				except Exception as error:
					fail(error)
			return wrapped
		def wait(predicate, then):
			def check():
				if predicate():
					then()
				else:
					QTimer.singleShot(70, step(check))
			QTimer.singleShot(70, step(check))
		def first():
			panes = context.window.get_panes()
			assert len(panes) == 2
			if panes[0].get_path() != as_url(str(left)) or panes[0]._widget._model.rowCount() < 1:
				QTimer.singleShot(100, step(first))
				return
			pane = panes[0]
			pane.place_cursor_at(as_url(str(left / 'example.txt')))
			context.main_window.activateWindow()
			app.setActiveWindow(context.main_window)
			pane.focus()
			QTest.keyClick(pane._widget._file_view, Qt.Key_F3)
			wait(lambda: context.main_window.panel_manager.active == 'preview', preview)
		def preview():
			panel = context.main_window.panel_manager.panel
			if 'Preview fixture content' not in panel.text.toPlainText():
				QTimer.singleShot(100, step(preview))
				return
			assert len(context.window.get_panes()) == 2
			context.window.get_panes()[0].place_cursor_at(as_url(str(left / 'sample.png')))
			wait(lambda: context.main_window.panel_manager.panel.content.currentIndex() == 1, image_ready)
		def image_ready():
			panel = context.main_window.panel_manager.panel
			assert panel.image.pixmap() is not None and not panel.image.pixmap().isNull()
			QTest.keyClick(context.window.get_panes()[0]._widget._file_view, Qt.Key_Comma, Qt.ControlModifier)
			wait(lambda: context.main_window.panel_manager.active == 'settings', settings)
		def settings():
			panel = context.main_window.panel_manager.panel
			panel.font_size.setValue(13)
			panel.fields['show_hidden_files'].setChecked(True)
			panel.fields['show_parent_entry'].setChecked(False)
			panel.save()
			assert context.preferences.values['font_size'] == 13
			assert all(p._widget._parent_button.isHidden() for p in context.window.get_panes())
			panel.fields['show_parent_entry'].setChecked(True)
			panel.save()
			assert context.preferences.path.is_file()
			QTest.keyClick(panel.font_family, Qt.Key_Escape)
			wait(lambda: context.main_window.panel_manager.active is None, filter_check)
		def filter_check():
			pane = context.window.get_panes()[0]
			filter_ = lambda _: False
			pane._add_filter(filter_)
			assert not pane._widget._parent_button.isHidden()
			pane._remove_filter(filter_)
			pane._remove_filter(filter_)
			pane.focus()
			QTest.keyClick(pane._widget._file_view, Qt.Key_F3)
			wait(lambda: context.main_window.panel_manager.active == 'preview', switch_from_preview)
		def switch_from_preview():
			QTest.keyClick(context.window.get_panes()[0]._widget._file_view, Qt.Key_Tab)
			wait(lambda: context.main_window.panel_manager.active is None, open_palette)
		def open_palette():
			pane = context.window.get_panes()[0]
			assert all(slot.currentIndex() == 0 for slot in context.main_window.panel_manager.slots)
			assert context.main_window._last_source_pane is context.window.get_panes()[1]._widget
			view = next(action.menu() for action in context.main_window.menuBar().actions() if action.text() == '&View')
			assert any(action.text().startswith('Settings') for action in view.actions())
			assert any(action.text().startswith('Preview') for action in view.actions())
			pane.focus()
			QTest.keyClick(pane._widget._file_view, Qt.Key_P, Qt.ControlModifier)
			wait(lambda: context.main_window._dialog is not None, palette)
		def palette():
			dialog = context.main_window._dialog
			assert dialog.windowTitle() == 'Search files, folders and commands'
			dialog._query.setText('> settings')
			wait(lambda: bool(dialog._curr_items), lambda: command_results(dialog))
		def command_results(dialog):
			assert all(item.value.kind == 'command' for item in dialog._curr_items)
			assert any('Settings' in item.title for item in dialog._curr_items)
			dialog._query.setText('example')
			wait(lambda: any(item.value.kind == 'path' for item in dialog._curr_items), lambda: path_results(dialog))
		def path_results(dialog):
			assert any(item.value.target == str(left / 'example.txt') for item in dialog._curr_items)
			before = list(dialog._curr_items)
			# A late response must never overwrite newer query results.
			dialog._receive(dialog._generation - 1, [QuicksearchItem(Entry('path', 'stale'))])
			assert dialog._curr_items == before
			QTest.keyClick(dialog._query, Qt.Key_Escape)
			wait(lambda: context.main_window._dialog is None, copy_with_f5)
		def copy_with_f5():
			pane = context.window.get_panes()[0]
			pane.place_cursor_at(as_url(str(left / 'example.txt')))
			pane.focus()
			QTest.keyClick(pane._widget._file_view, Qt.Key_F3)
			wait(lambda: context.main_window.panel_manager.active == 'preview', start_copy)
		def start_copy():
			QTest.keyClick(context.window.get_panes()[0]._widget._file_view, Qt.Key_F5)
			wait(lambda: context.main_window._dialog is not None, confirm_copy)
		def confirm_copy():
			dialog = context.main_window._dialog
			QTest.keyClick(dialog, Qt.Key_Return)
			wait(lambda: (right / 'example.txt').exists(), done)
		def done():
			assert (right / 'example.txt').read_text(encoding='utf-8') == 'Preview fixture content'
			assert context.main_window.panel_manager.active == 'preview'
			assert not context.plugin_error_handler._pending_error_messages
			assert QApplication.activeModalWidget() is None
			print('PASS: real Ctrl+P, commands/paths, stale-result rejection, settings save, exclusive panels, live preview, safe parent row, F5 copy')
			result[0] = 0
			app.exit(0)
		with patch('fman.impl.palette.everything_search', return_value=[]):
			QTimer.singleShot(250, step(first))
			QTimer.singleShot(80000, lambda: app.exit(1))
			code = context.run()
		return code or result[0]


if __name__ == '__main__':
	raise SystemExit(main())
