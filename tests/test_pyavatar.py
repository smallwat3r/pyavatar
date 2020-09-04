import os
import tempfile
import unittest

from pyavatar import (
    AvatarExtensionNotSupportedError, FontExtensionNotSupportedError,
    FontpathError, PyAvatar, RenderingSizeError, ValidImgFormats,
    ValidPixelRange)


class TestPyAvatar(unittest.TestCase):
    """Pyavatar unittests."""

    name = "test"

    def test_avatar_creation(self):
        """Test avatar properties are correct."""
        a = PyAvatar(self.name, size=200, color=(9, 9, 9))
        self.assertEqual(a.text, "T")
        self.assertEqual(a.size, 200)
        self.assertEqual(a.color, (9, 9, 9))

    def test_avatar_text_capitalize(self):
        """Test capitalize text."""
        a = PyAvatar(self.name)
        self.assertEqual(a.text, self.name.upper()[0])
        a = PyAvatar(self.name, capitalize=False)
        self.assertEqual(a.text, self.name.lower()[0])

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
            PyAvatar(self.name, size=ValidPixelRange.MAX.value + 1)
            PyAvatar(self.name, size=ValidPixelRange.MIN.value - 1)

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
        a = PyAvatar(self.name)
        original_color = a.color
        a.change_color()
        self.assertNotEqual(original_color, a.color)

    def test_save_avatar(self):
        """Test save avatar locally."""
        a = PyAvatar(self.name)
        with tempfile.TemporaryDirectory() as d:
            filepath = f"{d}/new/test.png"
            a.save(filepath)
            self.assertTrue(os.path.isfile(filepath))
            with self.assertRaises(AvatarExtensionNotSupportedError):
                filepath = f"{d}/test.nope"
                a.save(filepath)

    def test_stream_avatar(self):
        """Test save avatar in bytes array."""
        a = PyAvatar(self.name)
        stream = a.stream()
        self.assertIsInstance(stream, bytes)
        with self.assertRaises(AvatarExtensionNotSupportedError):
            a.stream("unknown")

    def test_save_base64_avatar(self):
        """Test save avatar in base64."""
        a = PyAvatar(self.name)
        for f in ValidImgFormats.list:
            img = a.base64_image(f)
            self.assertIsInstance(img, str)
            self.assertIn(f, img[:20])
