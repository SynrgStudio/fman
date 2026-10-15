# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""Local-only error handlers. Nothing is uploaded."""
import traceback


class ExceptionHandler:
	def handle(self, exc_type, exc_value, tb):
		return False

	def handle_system_exit(self, code=0):
		raise SystemExit(code)


class StderrExceptionHandler(ExceptionHandler):
	def handle(self, exc_type, exc_value, tb):
		traceback.print_exception(exc_type, exc_value, tb)
		return True
