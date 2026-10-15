# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
# Based on fman by Michael Herrmann (MIT); see LICENSES/fman-MIT.txt.
"""Ephemeral event history for tutorial hints, not telemetry.

No identifiers, properties, files, background workers, or network requests.
The legacy Metrics name is kept internal to avoid changing plugin callbacks.
"""

class Metrics:
	MAX_EVENTS = 256

	def __init__(self):
		self.past_events = []

	def track(self, event, properties=None):
		self.past_events.append(event)
		del self.past_events[:-self.MAX_EVENTS]
