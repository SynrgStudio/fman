# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""One running task and one replaceable pending task; never an unbounded queue."""
from queue import Queue, Empty, Full
from threading import Event, Thread
from PyQt5.QtCore import QObject, pyqtSignal


class LatestWorker(QObject):
	finished = pyqtSignal(int, object)

	def __init__(self, function, parent=None):
		super().__init__(parent)
		self._function = function
		self._queue = Queue(maxsize=1)
		self._stopped = Event()
		self._thread = Thread(target=self._run, daemon=True)
		self._thread.start()

	def submit(self, generation, value):
		if self._stopped.is_set():
			return
		try:
			self._queue.get_nowait()
		except Empty:
			pass
		try:
			self._queue.put_nowait((generation, value))
		except Full:
			pass

	def close(self):
		self._stopped.set()
		try:
			self._queue.get_nowait()
		except Empty:
			pass
		try:
			self._queue.put_nowait(None)
		except Full:
			pass

	def _run(self):
		while not self._stopped.is_set():
			task = self._queue.get()
			if task is None or self._stopped.is_set():
				return
			generation, value = task
			try:
				result = self._function(value)
			except Exception as error:
				result = error
			if not self._stopped.is_set():
				try:
					self.finished.emit(generation, result)
					del result  # Do not retain a full-resolution image while idle.
				except RuntimeError:
					return
