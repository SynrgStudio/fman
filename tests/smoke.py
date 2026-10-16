# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""Launch the real UI in a temporary profile, with socket connects forbidden."""
import os
from pathlib import Path
import socket
import sys
import tempfile
import traceback
from time import monotonic
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/main/python'))


def main():
	with tempfile.TemporaryDirectory(prefix='fman-clean-smoke-') as directory:
		root = Path(directory)
		os.environ['FMAN_DATA_DIRECTORY'] = str(root / 'profile')
		for name in ('left', 'right'):
			(root / name).mkdir()
			(root / name / 'example.txt').write_text('smoke test', encoding='utf-8')
		sys.argv = [sys.argv[0], str(root / 'left'), str(root / 'right')]
		attempts = []
		def deny_connect(*args, **kwargs):
			attempts.append(repr(args[1:]))
			raise AssertionError('Network access during startup')
		with patch.object(socket.socket, 'connect', deny_connect), \
			 patch.object(socket.socket, 'connect_ex', deny_connect):
			from fman.impl.application_context import get_application_context
			from PyQt5.QtCore import QTimer
			from PyQt5.QtWidgets import QApplication
			context = get_application_context()
			errors = []
			original_hook = context.install_exception_hook
			def install_hook():
				original_hook()
				previous = sys.excepthook
				def record(*args):
					errors.append(str(args[1]))
					previous(*args)
				sys.excepthook = record
			context.install_exception_hook = install_hook
			deadline = monotonic() + 30
			def verify():
				try:
					ready = len(context.window.get_panes()) == 2 and all(
						context.mother_fs.exists(p.get_path() + '/example.txt')
						for p in context.window.get_panes())
					if not ready and monotonic() < deadline:
						QTimer.singleShot(100, verify)
						return
					assert context.main_window.windowTitle() == 'fman Clean'
					panes = context.window.get_panes()
					assert len(panes) == 2
					for pane in panes:
						assert context.mother_fs.exists(pane.get_path() + '/example.txt')
					assert not context.plugin_error_handler._pending_error_messages
					assert QApplication.activeModalWidget() is None
					assert not attempts, attempts
					assert not errors, errors
					sys.path.insert(0, context.get_resource('Plugins/Core'))
					import core.commands as commands
					assert not hasattr(commands, 'InstallLicenseKey')
					assert not hasattr(commands, 'LicenseKeyOpenListener')
					assert context.mother_fs.exists(panes[0].get_path() + '/example.txt')
					print('PASS: two panes, local filesystem, no registration, no modal, no socket connects')
				except Exception:
					traceback.print_exc()
					errors.append('UI verification failed')
				context.app.exit(1 if errors else 0)
			_ = context.app
			QTimer.singleShot(2500, verify)
			code = context.run()
			print('Source smoke shutdown:', code, 'recorded errors:', errors)
			assert not list((root / 'profile').rglob('Metrics*'))
			return code or (1 if errors else 0)


if __name__ == '__main__':
	raise SystemExit(main())
