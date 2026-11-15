import os
import re
import sys
import tempfile
from typing import Any
from xml.etree import ElementTree

import pytest

from pyavatar import (FontExtensionNotSupportedError,
                      FontLoadError,
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
                                      "png, jpeg, ico, svg.")


def test_stream_avatar() -> None:
    avatar = PyAvatar("smallwat3r")
    stream = avatar.stream()
    assert isinstance(stream, bytes)

    with pytest.raises(ImageExtensionNotSupportedError) as excinfo:
        avatar.stream("unknown")

    assert str(excinfo.value) == ("unknown -> Image extension not "
                                  "supported. Supported formats: "
                                  "png, jpeg, ico, svg.")


@pytest.mark.parametrize("format", tuple(SupportedImageFmt))
def test_save_avatar_as_base64(format: str):
    avatar = PyAvatar("smallwat3r")
    image = avatar.base64_image(format)
    assert isinstance(image, str)
    assert format in image[:20]


@pytest.mark.parametrize("name,mime,magic", (
    ("png", "image/png", b"\x89PNG"),
    ("JPEG", "image/jpeg", b"\xff\xd8"),
    ("jpg", "image/jpeg", b"\xff\xd8"),
    ("ico", "image/x-icon", b"\x00\x00\x01\x00"),
    ("svg", "image/svg+xml", b"<svg "),
))
def test_formats_accept_plain_strings(name: str, mime: str,
                                      magic: bytes) -> None:
    avatar = PyAvatar("smallwat3r")
    assert avatar.stream(name).startswith(magic)
    assert avatar.base64_image(name).startswith(f"data:{mime};base64,")


@pytest.mark.parametrize("filename", (
    "a.jpg", "a.PNG", "a.Jpeg", "a.ico", "a.svg",
))
def test_save_extension_aliases_and_case(filename: str) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = os.path.join(temp_dir, filename)
        PyAvatar("smallwat3r").save(filepath)
        assert os.path.getsize(filepath) > 0


@pytest.mark.parametrize("value", ("", "   "))
def test_blank_text_falls_back_to_placeholder(value: str) -> None:
    assert PyAvatar(value).text == "?"


def test_leading_whitespace_is_ignored() -> None:
    assert PyAvatar("  bob").text == "B"


def test_default_color_is_stable_per_text() -> None:
    assert PyAvatar("smallwat3r").color == PyAvatar("smallwat3r").color
    assert PyAvatar("smallwat3r").color != PyAvatar("someone else").color


@pytest.mark.parametrize("background,letter", (
    ("#FFF", (0, 0, 0)),
    ((255, 255, 0), (0, 0, 0)),
    ("#000", (255, 255, 255)),
    ((0, 0, 139), (255, 255, 255)),
))
def test_letter_contrasts_with_background(background: Any,
                                          letter: tuple[int, int, int]
                                          ) -> None:
    avatar = PyAvatar("M", color=background)
    colors = {color for _, color in avatar.image.getcolors(maxcolors=65536)}
    assert letter in colors


def test_attribute_changes_redraw_the_image() -> None:
    avatar = PyAvatar("smallwat3r", color=(9, 9, 9))
    before = avatar.image.tobytes()

    avatar.size = 300
    assert avatar.image.size == (300, 300)

    avatar.size = 120
    avatar.text = "xavier"
    assert avatar.text == "X"
    assert avatar.image.tobytes() != before

    avatar.color = (200, 0, 0)
    assert avatar.image.getpixel((0, 0)) == (200, 0, 0)


def test_fontpath_must_be_a_file() -> None:
    with tempfile.TemporaryDirectory(suffix=".ttf") as temp_dir:
        with pytest.raises(FontpathError):
            PyAvatar("smallwat3r", fontpath=temp_dir)


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
    assert "Hex color must be in format" in str(excinfo.value)

    for invalid in ("#FF", "#GGG", "#12345G", ""):
        with pytest.raises(InvalidColorError) as excinfo:
            PyAvatar("test", color=invalid)
        assert "Hex color must be in format" in str(excinfo.value)

    # Invalid RGB colors
    with pytest.raises(InvalidColorError) as excinfo:
        PyAvatar("test", color=(256, 0, 0))
    assert "RGB color must be a tuple of 3 integers" in str(excinfo.value)

    with pytest.raises(InvalidColorError) as excinfo:
        PyAvatar("test", color=(0, 0))
    assert "RGB color must be a tuple of 3 integers" in str(excinfo.value)

    # Invalid type
    with pytest.raises(InvalidColorError) as excinfo:
        PyAvatar("test", color=123)
    assert "Color must be a hex string or RGB tuple" in str(excinfo.value)


def test_corrupted_font_file() -> None:
    with tempfile.NamedTemporaryFile(suffix=".ttf", delete=False) as f:
        f.write(b"not a valid font file")
        temp_path = f.name

    try:
        with pytest.raises(FontLoadError) as excinfo:
            PyAvatar("test", fontpath=temp_path)
        assert "Failed to load font file" in str(excinfo.value)
    finally:
        os.unlink(temp_path)


SVG_NS = "{http://www.w3.org/2000/svg}"


def test_svg_output() -> None:
    avatar = PyAvatar("smallwat3r", size=200, color=(255, 128, 0))
    root = ElementTree.fromstring(avatar.svg())
    assert root.get("width") == root.get("height") == "200"
    assert root.get("aria-label") == "S"
    assert root.find(f"{SVG_NS}rect").get("fill") == "#ff8000"
    letter = root.find(f"{SVG_NS}path")
    assert letter.get("fill") == "black"
    assert letter.get("d").startswith("M")

    avatar.change_color("#123")
    assert 'fill="#123"' in avatar.svg()
    assert 'fill="white"' in avatar.svg()


def test_svg_draws_the_glyph_of_the_text() -> None:
    def outline(text: str) -> str:
        root = ElementTree.fromstring(PyAvatar(text).svg())
        return root.find(f"{SVG_NS}path").get("d")

    assert outline("a") == outline("abc")
    assert outline("a") != outline("b")
    # characters missing from the font share its 'missing glyph' box
    assert outline("\u7530") == outline("\u4e2d")


@pytest.mark.parametrize("text", ("H", "g", "j", "Q"))
def test_svg_letter_is_centred(text: str) -> None:
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.svgLib.path import parse_path

    root = ElementTree.fromstring(
        PyAvatar(text, size=200, capitalize=False).svg())
    letter = root.find(f"{SVG_NS}path")
    x, y, scale = map(float, re.fullmatch(
        r"translate\((\S+) (\S+)\) scale\((\S+) -\S+\)",
        letter.get("transform")).groups())
    pen = BoundsPen(None)
    parse_path(letter.get("d"), pen)
    x_min, y_min, x_max, y_max = pen.bounds
    assert x + scale * (x_min + x_max) / 2 == pytest.approx(100, abs=0.1)
    assert y - scale * (y_min + y_max) / 2 == pytest.approx(100, abs=0.1)


@pytest.mark.parametrize("text,expected", (
    ("<script>", "&lt;"),
    ("&co", "&amp;"),
    ('"quoted"', "&quot;"),
))
def test_svg_escapes_text(text: str, expected: str) -> None:
    svg = PyAvatar(text).svg()
    assert f'aria-label="{expected}"' in svg
    assert ElementTree.fromstring(svg) is not None


def test_svg_without_fonttools(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "fontTools.ttLib", None)
    avatar = PyAvatar("smallwat3r")
    with pytest.raises(ImportError) as excinfo:
        avatar.svg()
    assert "pip install pyavatar[svg]" in str(excinfo.value)
    assert avatar.stream("png")


def test_svg_with_corrupted_font() -> None:
    avatar = PyAvatar("smallwat3r")
    with tempfile.NamedTemporaryFile(suffix=".ttf") as f:
        f.write(b"not a valid font file")
        f.flush()
        avatar.fontpath = f.name
        with pytest.raises(FontLoadError):
            avatar.svg()


@pytest.mark.parametrize("text", ("\x00abc", "\x1b[0m", "\ud800"))
def test_unprintable_text_falls_back_to_placeholder(text: str) -> None:
    avatar = PyAvatar(text)
    assert avatar.text == "?"
    assert avatar.stream("svg").startswith(b"<svg ")
