# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
"""Explicitly install the official optional SDK DLL outside this repository.

Everything itself must be separately installed and running. No auto-download
occurs at app startup; the DLL is never bundled by our build.
"""
import hashlib
from io import BytesIO
import os
from pathlib import Path
import sys
from urllib.request import urlopen
from zipfile import ZipFile

URL = 'https://www.voidtools.com/Everything-SDK.zip'
SHA256 = 'f5716d9513cce6b462b5170a0a2e7e081e191d9bcac6774f5decc061497df443'


def main():
	if sys.platform != 'win32' or sys.maxsize <= 2**32:
		raise SystemExit('The connector currently targets Windows x64 only.')
	with urlopen(URL, timeout=30) as response:
		data = response.read(8 * 1024 * 1024 + 1)
	if len(data) > 8 * 1024 * 1024 or hashlib.sha256(data).hexdigest() != SHA256:
		raise SystemExit('SDK checksum/size mismatch. Review an upstream update; nothing was installed.')
	destination = Path(os.environ['LOCALAPPDATA']) / 'fman-clean/tools/everything/Everything64.dll'
	with ZipFile(BytesIO(data)) as archive:
		dll = archive.read('dll/Everything64.dll')
	destination.parent.mkdir(parents=True, exist_ok=True)
	if destination.exists() and destination.read_bytes() != dll:
		raise SystemExit('A different connector already exists; remove it explicitly before replacing.')
	destination.write_bytes(dll)
	license_file = Path(__file__).resolve().parents[1] / 'LICENSES/Everything-SDK-MIT.txt'
	(destination.parent / 'LICENSE.txt').write_bytes(license_file.read_bytes())
	print('Official Everything SDK connector installed locally. No DLL is added to the repository.')


if __name__ == '__main__':
	main()
