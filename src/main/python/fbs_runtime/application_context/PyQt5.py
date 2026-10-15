# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""Resource discovery and local exception handling for the Qt application."""
from pathlib import Path
import sys
import traceback

from . import is_frozen
from ..platform import name


class ApplicationContext:
	def get_resource(self, relative_path):
		if is_frozen():
			root = Path(sys._MEIPASS) / 'resources'
		else:
			root = Path(__file__).resolve().parents[3] / 'resources'
		for variant in (name().lower(), 'base'):
			base = (root / variant).resolve()
			candidate = (base / relative_path).resolve()
			if not candidate.is_relative_to(base):
				raise ValueError('Resource path must stay within the resource directory')
			if candidate.exists():
				return str(candidate)
		raise FileNotFoundError(relative_path)

	def install_exception_hook(self):
		def handle(exc_type, exc_value, tb):
			for handler in self.exception_handlers:
				try:
					if issubclass(exc_type, SystemExit):
						handler.handle_system_exit(exc_value.code)
						return
					if handler.handle(exc_type, exc_value, tb):
						return
				except Exception:
					traceback.print_exc()
			traceback.print_exception(exc_type, exc_value, tb)
		sys.excepthook = handle
