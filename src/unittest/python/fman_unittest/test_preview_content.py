# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 SynrgStudio
from pathlib import Path
import tempfile
import unittest
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage
from fman.impl.panels import fit_image_rect, load_preview, preview_mime_data


class ImageFitTest(unittest.TestCase):
	def test_landscape_fits_without_cropping(self):
		rect = fit_image_rect(QSize(2400, 1200), QSize(600, 400))
		self.assertEqual((0, 50, 600, 300), rect.getRect())
		self.assertEqual(2, rect.width() / rect.height())

	def test_portrait_fits_without_cropping(self):
		rect = fit_image_rect(QSize(1200, 2400), QSize(600, 400))
		self.assertEqual((200, 0, 200, 400), rect.getRect())
		self.assertEqual(0.5, rect.width() / rect.height())

	def test_small_images_are_not_upscaled(self):
		rect = fit_image_rect(QSize(32, 16), QSize(600, 400))
		self.assertEqual((284, 192, 32, 16), rect.getRect())

	def test_zero_sizes_are_safe(self):
		self.assertTrue(fit_image_rect(QSize(0, 10), QSize(600, 400)).isEmpty())
		self.assertTrue(fit_image_rect(QSize(100, 10), QSize(0, 0)).isEmpty())


class PreviewContentTest(unittest.TestCase):
	def test_image_clipboard_payload_is_pixels_not_a_file(self):
		image = QImage(80, 40, QImage.Format_ARGB32)
		image.fill(0x7F336699)
		mime = preview_mime_data('image', image)
		self.assertTrue(mime.hasImage())
		self.assertFalse(mime.hasUrls())
		self.assertFalse(mime.hasText())
		copied = mime.imageData()
		self.assertEqual(image.size(), copied.size())
		self.assertEqual(image.pixelColor(0, 0), copied.pixelColor(0, 0))

	def test_text_clipboard_payload_is_text_not_a_file(self):
		text = 'Texto mostrado\nUnicode: ñ ✓'
		mime = preview_mime_data('text', text)
		self.assertEqual(text, mime.text())
		self.assertFalse(mime.hasUrls())
		self.assertFalse(mime.hasImage())

	def test_empty_or_unknown_payload_is_not_copyable(self):
		self.assertIsNone(preview_mime_data('image', QImage()))
		self.assertIsNone(preview_mime_data('unknown', 'anything'))

	def test_large_decoded_image_keeps_original_resolution(self):
		with tempfile.TemporaryDirectory() as directory:
			path = Path(directory) / 'large.png'
			image = QImage(2000, 1200, QImage.Format_ARGB32)
			image.fill(0xFF336699)
			self.assertTrue(image.save(str(path)))
			kind, decoded = load_preview(path)
			self.assertEqual('image', kind)
			self.assertEqual(image.size(), decoded.size())
			self.assertEqual(image.size(), preview_mime_data(kind, decoded).imageData().size())
