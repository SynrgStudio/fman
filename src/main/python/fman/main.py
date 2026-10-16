# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
# Based on fman by Michael Herrmann (MIT); see LICENSES/fman-MIT.txt.
import sys

def main():
	if len(sys.argv) == 6 and sys.argv[1] == '--everything-worker':
		from fman.impl.everything import helper
		try:
			helper(*sys.argv[2:])
		except Exception:
			pass  # An unavailable optional provider must not open a native error dialog.
		return
	if sys.platform != 'win32' or sys.maxsize <= 2**32:
		raise SystemExit('fman Clean currently targets Windows x64 only.')
	from fman.impl.application_context import get_application_context
	appctxt = get_application_context()
	exit_code = appctxt.run()
	sys.exit(exit_code)

def profile_main():
	# Import late to only incur the .0n sec time cost when necessary:
	import cProfile
	from fbs_runtime.application_context import is_frozen
	filename = 'fman.profile' if is_frozen() else None
	cProfile.run('main()', sort='cumtime', filename=filename)

if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == '--profile':
		sys.argv.pop(1)
		profile_main()
	else:
		main()