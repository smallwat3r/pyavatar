import os
import tempfile
from typing import Any

import pytest

from pyavatar import (FontExtensionNotSupportedError,
                      FontpathError,
                      ImageExtensionNotSupportedError,
                      InvalidColorError,
                      PyAvatar,
                      RenderingSizeError,
                      SupportedImageFmt,
                      SupportedPixelRange)


def test_avatar_attributes() -> None:
    avatar = PyAvatar("smallwat3r", size=200, color=(9, 9, 9))
    assert avatar.text == "S"
    assert avatar.size == 200
    assert avatar.color == (9, 9, 9)


def test_capitalise() -> None:
    avatar = PyAvatar("smallwat3r", capitalize=False)
    assert avatar.text == "s"


@pytest.mark.parametrize("value", (123, [], {}, b"hello"))
def test_raise_name_property_expect_string(value: Any) -> None:
    with pytest.raises(TypeError) as excinfo:
        PyAvatar(value)

    assert str(excinfo.value) == "Attribute `text` must be a string."

    with pytest.raises(TypeError) as excinfo:
        PyAvatar("smallwat3r", fontpath=value)

    assert str(excinfo.value) == "Attribute `fontpath` must be a string."


@pytest.mark.parametrize("value", ("hello", [], {}, b"hello"))
def test_raise_name_property_expect_integer(value: Any) -> None:
    with pytest.raises(TypeError) as excinfo:
        PyAvatar("smallwat3r", size=value)

    assert str(excinfo.value) == "Attribute `size` must be an integer."


def test_raise_size_property_validation() -> None:
    with pytest.raises(RenderingSizeError) as excinfo:
        PyAvatar("smallwat3r", size=SupportedPixelRange.MAX + 1)

    assert str(excinfo.value) == ("651 -> Size must fit within range "
                                  "min=50 max=650.")

    with pytest.raises(RenderingSizeError) as excinfo:
        PyAvatar("smallwat3r", size=SupportedPixelRange.MIN - 1)

    assert str(excinfo.value) == ("49 -> Size must fit within range "
                                  "min=50 max=650.")


def test_fontpath_property_validation() -> None:
    with pytest.raises(FontpathError) as excinfo:
        PyAvatar("smallwat3r", fontpath="idonotexist.ttf")

    assert str(excinfo.value) == ("idonotexist.ttf -> Cannot find a font "
                                  "file at this location.")

    with pytest.raises(FontExtensionNotSupportedError) as excinfo:
        PyAvatar("smallwar3r", fontpath=__file__)

    assert str(excinfo.value) == ("test_pyavatar.py -> Font file extension "
                                  "not supported. Supported extensions: "
                                  ".ttf, .otf.")


def test_avatar_change_color() -> None:
    avatar = PyAvatar("smallwat3r")
    original_color = avatar.color

    avatar.change_color()
    assert original_color != avatar.color

    avatar.change_color("#999")
    assert avatar.color == "#999"

    avatar.change_color((1, 1, 1))
    assert avatar.color == (1, 1, 1)


def test_save_avatar_locally() -> None:
    avatar = PyAvatar("smallwat3r")

    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = f"{temp_dir}/new/test.png"
        avatar.save(filepath)
        assert os.path.isfile(filepath)

        with pytest.raises(ImageExtensionNotSupportedError) as excinfo:
            avatar.save(f"{temp_dir}/test.nope")

        assert str(excinfo.value) == ("test.nope -> Image extension not "
                                      "supported. Supported formats: "
                                      "png, jpeg, ico.")


def test_stream_avatar() -> None:
    avatar = PyAvatar("smallwat3r")
    stream = avatar.stream()
    assert isinstance(stream, bytes)

    with pytest.raises(ImageExtensionNotSupportedError) as excinfo:
        avatar.stream("unknown")

    assert str(excinfo.value) == ("unknown -> Image extension not "
                                  "supported. Supported formats: "
                                  "png, jpeg, ico.")


@pytest.mark.parametrize("format", tuple(SupportedImageFmt))
def test_save_avatar_as_base64(format: str):
    avatar = PyAvatar("smallwat3r")
    image = avatar.base64_image(format)
    assert isinstance(image, str)
    assert format in image[:20]


def test_avatar_str_representation() -> None:
    avatar = PyAvatar("smallwat3r", size=120, color=(255, 128, 0))
    assert str(avatar) == "S 120x120 (255, 128, 0)"


def test_color_validation() -> None:
    # Valid hex colors
    avatar = PyAvatar("test", color="#FFF")
    assert avatar.color == "#FFF"

    avatar = PyAvatar("test", color="#FFFFFF")
    assert avatar.color == "#FFFFFF"

    # Valid RGB colors
    avatar = PyAvatar("test", color=(0, 0, 0))
    assert avatar.color == (0, 0, 0)

    avatar = PyAvatar("test", color=(255, 255, 255))
    assert avatar.color == (255, 255, 255)

    # Invalid hex colors
    with pytest.raises(InvalidColorError) as excinfo:
        PyAvatar("test", color="FFF")
    assert "Hex color must be in format '#RGB' or '#RRGGBB'" in str(excinfo.value)

    with pytest.raises(InvalidColorError) as excinfo:
        PyAvatar("test", color="#FF")
    assert "Hex color must be in format '#RGB' or '#RRGGBB'" in str(excinfo.value)

    # Invalid RGB colors
    with pytest.raises(InvalidColorError) as excinfo:
        PyAvatar("test", color=(256, 0, 0))
    assert "RGB color must be a tuple of 3 integers (0-255)" in str(excinfo.value)

    with pytest.raises(InvalidColorError) as excinfo:
        PyAvatar("test", color=(0, 0))
    assert "RGB color must be a tuple of 3 integers (0-255)" in str(excinfo.value)

    # Invalid type
    with pytest.raises(InvalidColorError) as excinfo:
        PyAvatar("test", color=123)
    assert "Color must be a hex string or RGB tuple" in str(excinfo.value)
