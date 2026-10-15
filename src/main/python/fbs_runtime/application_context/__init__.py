# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""Application singleton and packaging detection, without fbs."""
from functools import cached_property
import sys

_context = None


def is_frozen():
	return bool(getattr(sys, 'frozen', False))


def get_application_context(development_cls, frozen_cls):
	global _context
	if _context is None:
		_context = (frozen_cls if is_frozen() else development_cls)()
	return _context
