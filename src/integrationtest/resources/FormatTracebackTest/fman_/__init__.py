# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Michael Herrmann
def run_plugins():
	from plugin.module import run_plugin
	try:
		raise Exception()
	except Exception:
		run_plugin()

def raise_error():
	raise ValueError()