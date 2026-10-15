# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""Run upstream integration tests with QApplication on the main thread.

Upstream starts Qt on a worker, which can crash during interpreter shutdown.
The tests execute on a worker while the GUI loop stays on the main thread.
"""
from pathlib import Path
import sys
from threading import Thread
import unittest

ROOT = Path(__file__).resolve().parents[1]
for directory in ('src/main/python', 'src/unittest/python',
	'src/integrationtest/python', 'src/main/resources/base/Plugins/Core'):
	sys.path.insert(0, str(ROOT / directory))

from PyQt5.QtCore import QMetaObject, Qt, QTimer
from PyQt5.QtWidgets import QApplication
from fman_integrationtest.test_qt import _QtApp


def main():
	app = QApplication([])
	_QtApp._app = app
	_QtApp.start = classmethod(lambda cls: None)
	_QtApp.shutdown = classmethod(lambda cls: None)
	result = []
	def run_tests():
		try:
			suite = unittest.defaultTestLoader.discover(
				str(ROOT / 'src/integrationtest/python'))
			result.append(unittest.TextTestRunner(verbosity=2).run(suite))
		finally:
			QMetaObject.invokeMethod(app, 'quit', Qt.QueuedConnection)
	worker = Thread(target=run_tests)
	QTimer.singleShot(0, worker.start)
	app.exec_()
	worker.join()
	return 0 if result and result[0].wasSuccessful() else 1


if __name__ == '__main__':
	raise SystemExit(main())
