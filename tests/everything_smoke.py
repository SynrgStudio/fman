# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""Optional real-index test; requires running Everything and the explicit SDK setup."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/main/python'))
from fman.impl.everything import search, default_dll_path


def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('--frozen', action='store_true')
	parser.add_argument('--query', default='fman')
	args = parser.parse_args()
	assert default_dll_path().is_file(), 'Run tools/setup_everything.py first'
	if args.frozen:
		with tempfile.TemporaryDirectory(prefix='fman-real-index-') as directory:
			output = Path(directory) / 'results.json'
			command = [str(ROOT / 'target/fman-clean/fman-clean.exe'), '--everything-worker',
				str(default_dll_path()), args.query, '5', str(output)]
			subprocess.run(command, check=True, timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
			results = json.loads(output.read_text(encoding='utf-8'))
	else:
		results = search(args.query, {'everything_enabled': True}, limit=5)
	assert results, 'No results: Everything must be running and the query must match indexed names'
	assert len(results) <= 5
	print('PASS: live Everything IPC returned %d results (%s helper)' % (len(results), 'frozen' if args.frozen else 'source'))


if __name__ == '__main__':
	main()
