# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""Collect installed-package notices and inventory for human review.

This is not a complete license-compliance checker or corresponding-source bundle.
"""
import argparse
from importlib.metadata import distributions
import json
from pathlib import Path, PurePosixPath
import platform
from shutil import copy2
import sys


def collect(output):
	output = Path(output)
	output.mkdir(parents=True, exist_ok=True)
	inventory = {'python': platform.python_version(), 'platform': sys.platform,
		'packages': [], 'warning': 'License files alone do not satisfy all source-distribution obligations.'}
	for distribution in sorted(distributions(), key=lambda item: item.metadata['Name'].lower()):
		name = distribution.metadata['Name']
		safe_name = ''.join(c if c.isalnum() or c in '-_.' else '_' for c in name)
		entry = {'name': name, 'version': distribution.version,
			'declared_license': distribution.metadata.get('License-Expression') or distribution.metadata.get('License'),
			'license_files': []}
		base = Path(distribution.locate_file('')).resolve()
		for file in distribution.files or []:
			relative = PurePosixPath(str(file).replace('\\', '/'))
			if relative.is_absolute() or '..' in relative.parts:
				continue
			if not any(word in relative.name.lower() for word in ('license', 'copying', 'notice', 'copyright')):
				continue
			source = Path(distribution.locate_file(file)).resolve()
			if not source.is_relative_to(base) or not source.is_file():
				continue
			destination = output / safe_name / Path(*relative.parts)
			destination.parent.mkdir(parents=True, exist_ok=True)
			copy2(source, destination)
			entry['license_files'].append(destination.relative_to(output).as_posix())
		if not entry['license_files']:
			entry['review_required'] = 'Package supplies no discoverable notice file; obtain applicable notices/source from its supplier.'
		inventory['packages'].append(entry)
	(output / 'inventory.json').write_text(json.dumps(inventory, indent=2) + '\n', encoding='utf-8')
	return inventory


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('output', type=Path)
	args = parser.parse_args()
	result = collect(args.output)
	print('Collected notices for %d installed packages; review inventory.json before distribution.' % len(result['packages']))
