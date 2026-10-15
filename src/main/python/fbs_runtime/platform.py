# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""Platform helpers used by fman and its plugins."""
import os
import sys


def is_windows():
	return sys.platform == 'win32'


def is_mac():
	return sys.platform == 'darwin'


def is_linux():
	return sys.platform.startswith('linux')


def name():
	if is_windows():
		return 'Windows'
	if is_mac():
		return 'Mac'
	if is_linux():
		return 'Linux'
	raise RuntimeError('Unsupported platform: ' + sys.platform)


def is_kde_based():
	desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
	return is_linux() and ('kde' in desktop or bool(os.environ.get('KDE_FULL_SESSION')))


def is_gnome_based():
	return is_linux() and not is_kde_based()
