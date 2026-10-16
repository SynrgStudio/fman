# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""Exercise real arrow key events against the running source UI."""
import os
from pathlib import Path
import sys
import tempfile
import traceback
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/main/python'))


def main():
	with tempfile.TemporaryDirectory(prefix='fman-arrows-') as directory:
		root = Path(directory)
		folder = root / 'files'
		(folder / 'child').mkdir(parents=True)
		(folder / 'example.txt').write_text('Do not launch this file', encoding='utf-8')
		os.environ['FMAN_DATA_DIRECTORY'] = str(root / 'profile')
		sys.argv = [sys.argv[0], str(folder), str(folder)]
		from fman.impl.application_context import get_application_context
		from fman.url import as_url
		from PyQt5.QtCore import Qt, QTimer
		from PyQt5.QtTest import QTest
		from PyQt5.QtWidgets import QApplication
		context = get_application_context()
		app = context.app
		result = [1]
		def step(function):
			def wrapped():
				try:
					assert QApplication.activeModalWidget() is None
					function()
				except Exception:
					traceback.print_exc()
					app.exit(1)
			return wrapped
		deadline = monotonic() + 30
		def enter():
			pane = context.window.get_panes()[0]
			if pane.get_path() != as_url(str(folder)) or pane._widget._model.rowCount() < 2:
				assert monotonic() < deadline, 'Initial directory did not load'
				QTimer.singleShot(100, step(enter))
				return
			pane.place_cursor_at(as_url(str(folder / 'child')))
			QTest.keyClick(pane._widget._file_view, Qt.Key_Right)
			QTimer.singleShot(500, step(go_up))
		def go_up():
			pane = context.window.get_panes()[0]
			assert pane.get_path() == as_url(str(folder / 'child')), pane.get_path()
			QTest.keyClick(pane._widget._file_view, Qt.Key_Left)
			QTimer.singleShot(500, step(file_stays_closed))
		def file_stays_closed():
			pane = context.window.get_panes()[0]
			assert pane.get_path() == as_url(str(folder)), pane.get_path()
			pane.place_cursor_at(as_url(str(folder / 'example.txt')))
			QTest.keyClick(pane._widget._file_view, Qt.Key_Right)
			assert pane.get_path() == as_url(str(folder))
			assert QApplication.activeModalWidget() is None
			print('PASS: real Right enters folder, Left goes up, Right on file does not launch, no dialog')
			result[0] = 0
			app.exit(0)
		QTimer.singleShot(2500, step(enter))
		QTimer.singleShot(45000, lambda: app.exit(1))
		code = context.run()
		return code or result[0]


if __name__ == '__main__':
	raise SystemExit(main())
