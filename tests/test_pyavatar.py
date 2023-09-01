import os
import tempfile
import unittest

from pyavatar import (FontExtensionNotSupportedError,
                      FontpathError,
                      ImageExtensionNotSupportedError,
                      PyAvatar,
                      RenderingSizeError,
                      SupportedImageFormat,
                      SupportedPixelRange,
                      )


class TestPyAvatar(unittest.TestCase):
    """Pyavatar unittests."""

    name = "test"

    def test_avatar_creation(self):
        """Test avatar properties are correct."""
        avatar = PyAvatar(self.name, size=200, color=(9, 9, 9))
        self.assertEqual(avatar.text, "T")
        self.assertEqual(avatar.size, 200)
        self.assertEqual(avatar.color, (9, 9, 9))

    def test_avatar_text_capitalize(self):
        """Test capitalize text."""
        avatar = PyAvatar(self.name)
        self.assertEqual(avatar.text, self.name.upper()[0])
        avatar = PyAvatar(self.name, capitalize=False)
        self.assertEqual(avatar.text, self.name.lower()[0])

    def test_text_property_validation(self):
        """Test text property validation."""
        with self.assertRaises(TypeError):
            PyAvatar(123)
            PyAvatar(list())

    def test_size_property_validation(self):
        """Test size property validation."""
        with self.assertRaises(TypeError):
            PyAvatar(self.name, size="string")
            PyAvatar(self.name, size=list())
        with self.assertRaises(RenderingSizeError):
            PyAvatar(self.name, size=SupportedPixelRange.MAX + 1)
            PyAvatar(self.name, size=SupportedPixelRange.MIN - 1)

    def test_fontpath_property_validation(self):
        """Test fontpath property validation."""
        with self.assertRaises(TypeError):
            PyAvatar(self.name, fontpath=123)
            PyAvatar(self.name, fontpath=list())
        with self.assertRaises(FontpathError):
            PyAvatar(self.name, fontpath="idonotexist.ttf")
        with self.assertRaises(FontExtensionNotSupportedError):
            PyAvatar(self.name, fontpath=__file__)

    def test_change_color(self):
        """Test change avatar color."""
        avatar = PyAvatar(self.name)
        original_color = avatar.color
        avatar.change_color()
        self.assertNotEqual(original_color, avatar.color)

    def test_save_avatar(self):
        """Test save avatar locally."""
        avatar = PyAvatar(self.name)
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = f"{temp_dir}/new/test.png"
            avatar.save(filepath)
            self.assertTrue(os.path.isfile(filepath))
            with self.assertRaises(ImageExtensionNotSupportedError):
                filepath = f"{temp_dir}/test.nope"
                avatar.save(filepath)

    def test_stream_avatar(self):
        """Test save avatar in bytes array."""
        avatar = PyAvatar(self.name)
        stream = avatar.stream()
        self.assertIsInstance(stream, bytes)
        with self.assertRaises(ImageExtensionNotSupportedError):
            avatar.stream("unknown")

    def test_save_base64_avatar(self):
        """Test save avatar in base64."""
        avatar = PyAvatar(self.name)
        for format in SupportedImageFormat.get_set():
            image = avatar.base64_image(format)
            self.assertIsInstance(image, str)
            self.assertIn(format, image[:20])
