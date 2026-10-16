# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""One palette: commands, recent/direct paths and optional Everything results."""
from dataclasses import dataclass
import os
from pathlib import Path
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from fman import QuicksearchItem
from fman.impl.quicksearch import Quicksearch
from fman.impl.latest_worker import LatestWorker
from fman.impl.everything import search as everything_search


@dataclass(frozen=True)
class Entry:
	kind: str
	target: object
	folder: bool = True


def matches(text, query):
	text, query = text.casefold(), query.casefold().strip()
	if query in text:
		return True
	iterator = iter(text)
	return all(any(letter == character for letter in iterator) for character in query)


def path_items(query, visited, current, preferences, include_everything=True):
	"""Worker-only filesystem/index access; no Qt widgets or command callbacks."""
	query = query.strip()
	if query.startswith('>'):
		return []
	candidates = [(path, True) for path in sorted(visited, key=visited.get, reverse=True)
		if matches(path, query)][:20]
	if current and matches(current, query):
		candidates.insert(0, (current, True))
	if query:
		expanded = os.path.expandvars(os.path.expanduser(query))
		try:
			if os.path.isabs(expanded) and os.path.exists(expanded):
				candidates.insert(0, (os.path.normpath(expanded), os.path.isdir(expanded)))
			parent = os.path.dirname(expanded) if ('\\' in expanded or '/' in expanded) else current
			needle = os.path.basename(expanded) if ('\\' in expanded or '/' in expanded) else query
			if parent:
				with os.scandir(parent) as children:
					for count, child in enumerate(children):
						if count >= 500:
							break
						if matches(child.name, needle):
							candidates.append((child.path, child.is_dir(follow_symlinks=False)))
		except (OSError, ValueError):
			pass
		if include_everything:
			candidates.extend(everything_search(query, preferences))
	return make_path_items(candidates)


def make_path_items(candidates):
	seen, result = set(), []
	for path, folder in candidates:
		key = os.path.normcase(os.path.normpath(path))
		if key in seen:
			continue
		seen.add(key)
		result.append(QuicksearchItem(Entry('path', path, folder),
			os.path.basename(path.rstrip('\\/')) or path,
			hint='Folder' if folder else 'File · reveal in folder', description=path))
		if len(result) >= 50:
			break
	return result


class UnifiedPalette(Quicksearch):
	def __init__(self, parent, app, css, commands, visited, current, preferences, query=''):
		self._commands = commands
		self._visited = {path: count for path, count in visited.items()
			if isinstance(path, str) and type(count) is int and count >= 0} if isinstance(visited, dict) else {}
		self._current = current
		self._preferences = dict(preferences)
		self._generation = 0
		self._closed = False
		self._command_items = []
		self._selection_moved = False
		super().__init__(parent, app, css, lambda _: [], self._complete, query)
		self.setWindowTitle('Search files, folders and commands')
		self._query.setPlaceholderText('Search · > commands only · type a path to navigate')
		self._worker = LatestWorker(self._search, self)
		self._worker.finished.connect(self._receive, Qt.QueuedConnection)
		self._debounce = QTimer(self)
		self._debounce.setSingleShot(True)
		self._debounce.setInterval(150)
		self._debounce.timeout.connect(self._submit)
		self.finished.connect(self._finish)

	def _update_items(self, query):
		self._generation += 1
		self._selection_moved = False
		command_query = query.lstrip('> ').strip() if query.lstrip().startswith('>') else query
		self._command_items = []
		for item in list(self._commands(command_query))[:15]:
			if item.value.name in ('unified_palette', 'go_to', 'command_palette'):
				continue
			self._command_items.append(QuicksearchItem(Entry('command', item.value),
				item.title, item.highlight, 'Command · ' + item.hint, item.description))
		self._replace(self._command_items)
		self._debounce.start()

	def _search(self, payload):
		query, generation = payload
		local = path_items(query, self._visited, self._current, self._preferences, include_everything=False)
		if self._closed:
			return []
		# Show local/recent results before waiting for the optional native index.
		self._worker.finished.emit(generation, local)
		indexed = [] if query.strip().startswith('>') else everything_search(query, self._preferences)
		candidates = [(item.value.target, item.value.folder) for item in local] + indexed
		return make_path_items(candidates)

	def _submit(self):
		self._worker.submit(self._generation, (self._query.text(), self._generation))

	def _on_key_pressed(self, event):
		if event.key() in (Qt.Key_Up, Qt.Key_Down, Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Home, Qt.Key_End):
			self._selection_moved = True
		return super()._on_key_pressed(event)

	@pyqtSlot(int, object)
	def _receive(self, generation, items):
		if self._closed or generation != self._generation or isinstance(items, Exception):
			return
		# Paths lead for normal input; > is a command-only view of the same palette.
		index = self._items.currentIndex()
		selected = self._curr_items[index.row()].value if self._selection_moved and index.isValid() else None
		self._replace(list(items) + self._command_items)
		if selected is not None:
			for row, item in enumerate(self._curr_items):
				if item.value == selected:
					self._place_cursor_at_item(row)
					break

	def _replace(self, items):
		self._curr_items = list(items)
		self._items.model().clear()
		self._items.model().extend(self._curr_items)
		self._adjust_item_list_ize()
		self._place_cursor_at_item(0)

	def _complete(self, query, item):
		if item and isinstance(item.value, Entry) and item.value.kind == 'path':
			return item.value.target.rstrip('\\/') + (os.sep if item.value.folder else '')

	def _finish(self, _):
		self._closed = True
		self._generation += 1
		self._debounce.stop()
		self._worker.close()
