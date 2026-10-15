# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
# Based on fman by Michael Herrmann (MIT); see LICENSES/fman-MIT.txt.
"""Unknown shortcuts are left to Qt, never turned into plugin adverts."""

class NonexistentShortcutHandler:
	def __call__(self, key_event, pane):
		return False
