# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
# Based on fman by Michael Herrmann (MIT); see LICENSES/fman-MIT.txt.
"""Local build commands. No vendor credentials, servers, or fbs required."""
import argparse
import os
from pathlib import Path
import subprocess
from shutil import copytree, ignore_patterns, rmtree
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'src/main/python'
CORE = ROOT / 'src/main/resources/base/Plugins/Core'


def environment():
	env = os.environ.copy()
	paths = [SOURCE, CORE, ROOT / 'src/unittest/python',
		ROOT / 'src/integrationtest/python']
	env['PYTHONPATH'] = os.pathsep.join(map(str, paths))
	return env


def run(paths):
	return subprocess.call([sys.executable, '-m', 'fman.main', *paths],
		cwd=ROOT, env=environment())


def test():
	# Separate processes prevent incompatible QApplication lifecycles colliding.
	with tempfile.TemporaryDirectory(prefix='fman-clean-tests-') as data:
		env = environment()
		env['FMAN_DATA_DIRECTORY'] = data
		result = 0
		for directory in ('src/unittest/python', str(CORE)):
			code = subprocess.call([sys.executable, '-m', 'unittest',
				'discover', '-s', directory, '-v'], cwd=ROOT, env=env)
			result = result or code
		code = subprocess.call([sys.executable, 'tests/integration.py'],
			cwd=ROOT, env=env)
		result = result or code
	return result


def freeze():
	if sys.platform != 'win32' or sys.maxsize <= 2**32:
		raise SystemExit('Standalone builds currently target Windows x64 only.')
	resources = ROOT / 'target/resources'
	if resources.exists():
		rmtree(resources)
	copytree(ROOT / 'src/main/resources', resources,
		ignore=ignore_patterns('__pycache__', '*.pyc', 'tests'))
	notices = ROOT / 'target/dependency-notices'
	if notices.exists():
		rmtree(notices)
	subprocess.check_call([sys.executable, str(ROOT / 'tools/collect_licenses.py'), str(notices)], cwd=ROOT)
	args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
		'--name', 'fman-clean', '--onedir', '--windowed',
		'--paths', str(SOURCE), '--distpath', str(ROOT / 'target'),
		'--workpath', str(ROOT / 'target/build'),
		'--specpath', str(ROOT / 'target'),
		'--add-data', str(resources) + os.pathsep + 'resources',
		'--add-data', str(ROOT / 'LICENSE') + os.pathsep + '.',
		'--add-data', str(ROOT / 'THIRD_PARTY.md') + os.pathsep + '.',
		'--add-data', str(ROOT / 'README.md') + os.pathsep + '.',
		'--add-data', str(ROOT / 'NOTICE') + os.pathsep + '.',
		'--add-data', str(ROOT / 'docs') + os.pathsep + 'docs',
		'--add-data', str(notices) + os.pathsep + 'dependency-notices',
		'--add-data', str(ROOT / 'LICENSES') + os.pathsep + 'LICENSES',
		'--hidden-import', 'tinycss', '--hidden-import', 'requests',
		'--collect-submodules', 'send2trash']
	args += ['--icon', str(ROOT / 'src/main/icons/Icon.ico'),
		'--collect-all', 'winpty']
	for module in ('win32com.shell.shell', 'win32com.shell.shellcon',
		'win32gui', 'win32wnet', 'pythoncom', 'pywintypes'):
		args += ['--hidden-import', module]
	args.append(str(SOURCE / 'fman/main.py'))
	return subprocess.call(args, cwd=ROOT)


def main():
	parser = argparse.ArgumentParser(description=__doc__)
	sub = parser.add_subparsers(dest='command', required=True)
	runner = sub.add_parser('run', help='Run from source')
	runner.add_argument('paths', nargs='*', help='Initial left/right paths')
	sub.add_parser('test', help='Run unit, Core, and integration tests')
	sub.add_parser('freeze', help='Build a local standalone folder')
	args = parser.parse_args()
	if args.command == 'run':
		return run(args.paths)
	if args.command == 'test':
		return test()
	return freeze()


if __name__ == '__main__':
	raise SystemExit(main())
