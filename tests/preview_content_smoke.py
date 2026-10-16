# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""Fit/copy UI regression. Default offscreen; --native also checks Windows formats.

Native mode temporarily uses the system clipboard and restores its previous
formats if this test still owns it. No clipboard content is logged or saved.
"""
import os
from pathlib import Path
import sys
import tempfile
from time import monotonic
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/main/python'))


def main():
	native = '--native' in sys.argv[1:]
	os.environ['QT_QPA_PLATFORM'] = 'windows' if native else 'offscreen'
	with tempfile.TemporaryDirectory(prefix='fman-preview-content-') as directory:
		root = Path(directory).resolve()
		left, right = root / 'left', root / 'right'
		left.mkdir()
		right.mkdir()
		text = 'Preview content, not a file\nUnicode: ñ ✓'
		(left / 'text.txt').write_text(text, encoding='utf-8')
		os.environ['FMAN_DATA_DIRECTORY'] = str(root / 'profile')
		sys.argv = [sys.argv[0], str(left), str(right)]
		from fman.impl.application_context import get_application_context
		from fman.impl.panels import FitImageView
		from fman.url import as_url
		from PyQt5.QtCore import Qt, QTimer, QMimeData
		from PyQt5.QtGui import QImage
		from PyQt5.QtTest import QTest
		context = get_application_context()
		app = context.app
		clipboard = app.clipboard()
		backup = QMimeData()
		if native:
			previous = clipboard.mimeData()
			if previous is not None:
				for format_ in previous.formats():
					backup.setData(format_, previous.data(format_))
				if previous.hasImage():
					backup.setImageData(previous.imageData())
		image = QImage(2400, 1200, QImage.Format_ARGB32)
		image.fill(0xCC336699)
		assert image.save(str(left / 'image.png'))
		result = [1]
		deadline = monotonic() + 45
		def step(function):
			def wrapped():
				try:
					assert monotonic() < deadline, 'Preview regression deadline exceeded'
					function()
				except Exception:
					traceback.print_exc()
					app.exit(1)
			return wrapped
		def wait(predicate, then):
			print('Waiting for:', then.__name__, flush=True)
			def check():
				if predicate():
					then()
				else:
					QTimer.singleShot(60, step(check))
			QTimer.singleShot(60, step(check))
		def pane():
			return context.window.get_panes()[0]
		def panel():
			return context.main_window.panel_manager.panel
		def first():
			if pane().get_path() != as_url(str(left)) or pane()._widget._model.rowCount() < 2:
				QTimer.singleShot(100, step(first))
				return
			context.main_window.showNormal()
			context.main_window.resize(1050, 650)
			app.setActiveWindow(context.main_window)
			pane().focus()
			pane().place_cursor_at(as_url(str(left / 'image.png')))
			QTest.keyClick(pane()._widget._file_view, Qt.Key_F3)
			wait(lambda: panel() is not None and panel().content.currentIndex() == 1, image_ready)
		def check_fit():
			view = panel().image
			assert isinstance(panel().content.currentWidget(), FitImageView)
			rect = view.display_rect()
			assert rect.width() > 0 and rect.height() > 0
			assert abs(rect.width() / rect.height() - 2) < 1e-6
			assert rect.x() >= -1e-6 and rect.y() >= -1e-6
			assert rect.right() <= view.width() + 1e-6
			assert rect.bottom() <= view.height() + 1e-6
			assert view.image().size() == image.size()
			assert rect.width() < image.width()
		def image_ready():
			check_fit()
			context.main_window.resize(850, 500)
			context.main_window._splitter.setSizes([550, 300])
			QTimer.singleShot(150, step(copy_image))
		def copy_image():
			check_fit()
			pane().focus()
			QTest.keyClick(pane()._widget._file_view, Qt.Key_C, Qt.ControlModifier | Qt.ShiftModifier)
			wait(lambda: 'Image copied' in panel().copy_status.text(), image_copied)
		def image_copied():
			mime = clipboard.mimeData()
			assert mime.hasImage() and not mime.hasUrls()
			copied = clipboard.image()
			assert copied.size() == image.size(), 'Clipboard must use original resolution'
			assert copied.pixelColor(0, 0) == image.pixelColor(0, 0)
			if native:
				import ctypes
				assert ctypes.windll.user32.IsClipboardFormatAvailable(8) or ctypes.windll.user32.IsClipboardFormatAvailable(17)
				assert not ctypes.windll.user32.IsClipboardFormatAvailable(15)
			QTest.keyClick(pane()._widget._file_view, Qt.Key_C, Qt.ControlModifier)
			wait(lambda: clipboard.mimeData() is not None and clipboard.mimeData().hasUrls(), file_copied)
		def file_copied():
			assert not clipboard.mimeData().hasImage()
			assert os.path.normcase(clipboard.mimeData().urls()[0].toLocalFile()) == os.path.normcase(str(left / 'image.png'))
			old_generation = panel()._generation
			clipboard.setText('Keep while loading')
			pane().place_cursor_at(as_url(str(left / 'text.txt')))
			assert panel()._generation > old_generation
			panel()._receive(old_generation, ('image', image))
			assert not panel().copy_content(), 'Do not copy the previous image during a new load'
			assert clipboard.text() == 'Keep while loading'
			wait(lambda: panel().text.toPlainText() == text and panel().copy_button.isEnabled(), copy_text)
		def copy_text():
			pane().focus()
			QTest.keyClick(pane()._widget._file_view, Qt.Key_C, Qt.ControlModifier | Qt.ShiftModifier)
			wait(lambda: clipboard.text() == text, text_copied)
		def text_copied():
			assert not clipboard.mimeData().hasUrls() and not clipboard.mimeData().hasImage()
			if native:
				import ctypes
				assert ctypes.windll.user32.IsClipboardFormatAvailable(13)
				assert not ctypes.windll.user32.IsClipboardFormatAvailable(15)
			clipboard.setText('Copy while preview text has focus')
			panel().text.setFocus()
			QTest.keyClick(panel().text, Qt.Key_C, Qt.ControlModifier | Qt.ShiftModifier)
			wait(lambda: clipboard.text() == text, button_copy)
		def button_copy():
			panel().copy_button.click()
			assert clipboard.text() == text
			QTest.keyClick(pane()._widget._file_view, Qt.Key_F3)
			wait(lambda: context.main_window.panel_manager.active is None, closed)
		def closed():
			clipboard.setText('No active preview')
			QTest.keyClick(pane()._widget._file_view, Qt.Key_C, Qt.ControlModifier | Qt.ShiftModifier)
			assert clipboard.text() == 'No active preview'
			print('PASS: proportional image fitting/resizing, original-resolution image clipboard, plain text clipboard, Ctrl+C files retained, stale/closed preview safe')
			result[0] = 0
			app.exit(0)
		QTimer.singleShot(250, step(first))
		QTimer.singleShot(50000, lambda: app.exit(1))
		try:
			code = context.run()
		finally:
			if native and clipboard.ownsClipboard():
				if backup.formats():
					clipboard.setMimeData(backup)
					import ctypes
					ctypes.windll.ole32.OleFlushClipboard()
				else:
					clipboard.clear()
		return code or result[0]


if __name__ == '__main__':
	raise SystemExit(main())
