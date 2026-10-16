# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""One mutually exclusive panel in the opposite pane; source navigation stays live."""
import os
from pathlib import Path
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSlot
from PyQt5.QtGui import QFontDatabase, QImageReader, QPixmap
from PyQt5.QtWidgets import (QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout,
	QLabel, QPushButton, QPlainTextEdit, QScrollArea, QFormLayout, QComboBox,
	QSpinBox, QCheckBox, QLineEdit, QFileDialog)
from fman.impl.latest_worker import LatestWorker
from fman.url import splitscheme, as_human_readable


class PanelManager:
	def __init__(self, window, splitter):
		self.window = window
		self.splitter = splitter
		self.slots = []
		self.active = None
		self.source = None
		self.panel = None

	def add_pane(self, pane):
		slot = QStackedWidget(self.splitter)
		slot.addWidget(pane)
		self.splitter.addWidget(slot)
		self.slots.append(slot)

	def activate(self, name, panel, source):
		self.deactivate(focus=False)
		panes = self.window.get_panes()
		if source not in panes or len(panes) < 2:
			panel.deleteLater()
			return
		index = (panes.index(source) + 1) % len(panes)
		slot = self.slots[index]
		slot.addWidget(panel)
		slot.setCurrentWidget(panel)
		self.active, self.source, self.panel = name, source, panel
		panel.show()
		if name == 'preview':
			source.focus()
		else:
			panel.setFocus()

	def deactivate(self, focus=True):
		panel, source = self.panel, self.source
		if panel is not None:
			if hasattr(panel, 'dispose'):
				panel.dispose()
			for slot in self.slots:
				if slot.indexOf(panel) >= 0:
					slot.setCurrentIndex(0)
					slot.removeWidget(panel)
					break
			panel.hide()
			panel.deleteLater()
		self.active = self.source = self.panel = None
		if focus and source is not None:
			source.focus()


def header(widget, title, close):
	layout = QVBoxLayout(widget)
	bar = QHBoxLayout()
	label = QLabel(title)
	label.setTextFormat(Qt.PlainText)
	button = QPushButton('Close · Esc')
	button.clicked.connect(lambda: close())
	bar.addWidget(label, 1)
	bar.addWidget(button)
	layout.addLayout(bar)
	return layout


class SettingsPanel(QWidget):
	def __init__(self, context, parent=None):
		super().__init__(parent)
		self.context = context
		outer = header(self, 'Settings', context.main_window.panel_manager.deactivate)
		body = QWidget()
		layout = QVBoxLayout(body)
		scroll = QScrollArea()
		scroll.setWidgetResizable(True)
		scroll.setWidget(body)
		outer.addWidget(scroll, 1)
		form = QFormLayout()
		self.font_family = QComboBox()
		self.font_family.addItems(QFontDatabase().families())
		self.font_family.setCurrentText(context.preferences.values['font_family'])
		self.font_size = QSpinBox()
		self.font_size.setRange(8, 32)
		self.font_size.setValue(context.preferences.values['font_size'])
		form.addRow('Font', self.font_family)
		form.addRow('Size', self.font_size)
		self.fields = {}
		for key, label in (('show_hidden_files', 'Show hidden files'),
			('show_parent_entry', 'Show .. parent navigation row'),
			('everything_enabled', 'Use Everything when available')):
			field = QCheckBox(label)
			field.setChecked(context.preferences.values[key])
			self.fields[key] = field
			form.addRow(field)
		for key, label, filter_ in (('editor_exe', 'Editor', 'Programs (*.exe)'),
			('terminal_exe', 'Terminal', 'Programs (*.exe)'),
			('everything_dll', 'Everything SDK DLL', 'DLL (*.dll)')):
			row = QWidget()
			box = QHBoxLayout(row)
			box.setContentsMargins(0, 0, 0, 0)
			field = QLineEdit(context.preferences.values[key])
			field.setPlaceholderText('Existing/default configuration' if key != 'everything_dll' else 'Optional connector; see README')
			browse = QPushButton('Browse')
			browse.clicked.connect(lambda _, f=field, ft=filter_: self._browse(f, ft))
			box.addWidget(field, 1)
			box.addWidget(browse)
			self.fields[key] = field
			form.addRow(label, row)
		layout.addLayout(form)
		note = QLabel('Everything must be running. Its optional SDK connector is installed separately.\n'
			'Only select executables/DLLs you trust. No commands are run when saving.\n'
			'Existing advanced tool settings are preserved unless you choose a replacement.')
		note.setWordWrap(True)
		layout.addWidget(note)
		self.message = QLabel('')
		self.message.setTextFormat(Qt.PlainText)
		self.message.setWordWrap(True)
		layout.addWidget(self.message)
		button = QPushButton('Save preferences')
		button.clicked.connect(self.save)
		layout.addWidget(button)
		layout.addStretch(1)
		self.setFocusProxy(self.font_family)

	def _browse(self, field, filter_):
		path, _ = QFileDialog.getOpenFileName(self, 'Select trusted file', '', filter_)
		if path:
			field.setText(path)

	def save(self):
		updates = {'font_family': self.font_family.currentText(), 'font_size': self.font_size.value()}
		for key, field in self.fields.items():
			updates[key] = field.isChecked() if isinstance(field, QCheckBox) else field.text().strip()
		for key in ('editor_exe', 'terminal_exe', 'everything_dll'):
			path = updates[key]
			if path and (not os.path.isabs(path) or not os.path.isfile(path)):
				self.message.setText('Select an existing absolute file path for ' + key)
				return
		try:
			self.context.set_preferences(updates)
		except (OSError, ValueError) as error:
			self.message.setText('Could not save: ' + str(error))
		else:
			self.message.setText('Saved. Changes apply immediately.')


def load_preview(path):
	"""Bounded, read-only worker. No recursive traversal and no file execution."""
	path = Path(path)
	try:
		if path.is_dir():
			files = folders = size = count = 0
			with os.scandir(path) as entries:
				for entry in entries:
					if count >= 5000:
						break
					count += 1
					try:
						if entry.is_dir(follow_symlinks=False):
							folders += 1
						else:
							files += 1
							size += entry.stat(follow_symlinks=False).st_size
					except OSError:
						pass
			return ('text', 'Directory statistics (immediate children only)\n\n'
				f'Files: {files}\nFolders: {folders}\nFile bytes: {size:,}\n'
				+ ('Limited to the first 5,000 entries.' if count >= 5000 else ''))
		if not path.is_file():
			return ('text', 'No regular file selected.')
		if path.stat().st_size > 25 * 1024 * 1024:
			return ('text', 'Preview limited to files up to 25 MiB.')
		if path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.ico'):
			reader = QImageReader(str(path))
			size = reader.size()
			if size.width() <= 0 or size.height() <= 0 or size.width() * size.height() > 40_000_000:
				return ('text', 'Image dimensions are unsupported or exceed the 40 MP limit.')
			reader.setAutoTransform(True)
			reader.setScaledSize(size.scaled(QSize(1400, 1000), Qt.KeepAspectRatio))
			image = reader.read()
			return ('image', image) if not image.isNull() else ('text', 'Image decoder could not read this file.')
		if path.suffix.lower() in ('.pdf', '.exe', '.dll', '.zip', '.7z', '.tar', '.svg', '.avif'):
			return ('text', 'This format is not supported by the initial read-only preview.')
		with path.open('rb') as stream:
			data = stream.read(200 * 1024 + 1)
		if data.startswith((b'\xff\xfe', b'\xfe\xff')):
			text = data[:200 * 1024].decode('utf-16', errors='replace')
		elif b'\x00' in data:
			return ('text', 'Binary file; no text preview.')
		else:
			text = data[:200 * 1024].decode('utf-8-sig', errors='replace')
		if len(data) > 200 * 1024:
			text += '\n\n[Preview truncated at 200 KiB]'
		return ('text', text)
	except (OSError, ValueError) as error:
		return ('text', 'Cannot preview: ' + str(error))


class PreviewPanel(QWidget):
	def __init__(self, source, close, parent=None):
		super().__init__(parent)
		self.source = source
		self._closed = False
		self._generation = 0
		layout = header(self, 'Preview · F3', close)
		self.name = QLabel('')
		self.name.setTextFormat(Qt.PlainText)
		self.name.setWordWrap(True)
		layout.addWidget(self.name)
		self.text = QPlainTextEdit()
		self.text.setReadOnly(True)
		self.image = QLabel()
		self.image.setAlignment(Qt.AlignCenter)
		scroll = QScrollArea()
		scroll.setWidget(self.image)
		scroll.setWidgetResizable(True)
		self.content = QStackedWidget()
		self.content.addWidget(self.text)
		self.content.addWidget(scroll)
		layout.addWidget(self.content, 1)
		self._timer = QTimer(self)
		self._timer.setSingleShot(True)
		self._timer.setInterval(120)
		self._timer.timeout.connect(self._submit)
		self._worker = LatestWorker(load_preview, self)
		self._worker.finished.connect(self._receive, Qt.QueuedConnection)
		self.source._file_view.selectionModel().currentChanged.connect(self.schedule)
		self.source.location_changed.connect(self.schedule)
		self.source._model.location_loaded.connect(self.schedule)
		self.schedule()

	def schedule(self, *args):
		self._generation += 1
		self._timer.start()

	def _submit(self):
		url = self.source.get_file_under_cursor() or self.source.get_location()
		if not url or splitscheme(url)[0] != 'file://':
			self.text.setPlainText('Preview currently supports local Windows paths only.')
			self.content.setCurrentIndex(0)
			return
		path = as_human_readable(url)
		self.name.setText(path)
		self.text.setPlainText('Loading…')
		self.content.setCurrentIndex(0)
		self._worker.submit(self._generation, path)

	@pyqtSlot(int, object)
	def _receive(self, generation, result):
		if self._closed or generation != self._generation:
			return
		if isinstance(result, Exception):
			result = ('text', 'Preview unavailable.')
		kind, value = result
		if kind == 'image':
			self.image.setPixmap(QPixmap.fromImage(value))
			self.content.setCurrentIndex(1)
		else:
			self.text.setPlainText(value)
			self.content.setCurrentIndex(0)

	def dispose(self):
		self._closed = True
		self._generation += 1
		self._timer.stop()
		self._worker.close()
		for signal in (self.source._file_view.selectionModel().currentChanged,
			self.source.location_changed, self.source._model.location_loaded):
			try:
				signal.disconnect(self.schedule)
			except (TypeError, RuntimeError):
				pass
