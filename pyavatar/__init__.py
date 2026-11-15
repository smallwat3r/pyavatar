"""
Pyavatar Library
~~~~~~~~~~~~~~~~

Pyavatar is a library, written in Python, to generate simple default
user avatars to use in a web application or elsewhere.

:copyright: (c) 2020 by Matthieu Petiteau.
:license: MIT, see LICENSE for more details.
"""

import os
import random
import re
from base64 import b64encode
from colorsys import hls_to_rgb
from enum import Enum, IntEnum
from hashlib import sha256
from html import escape
from io import BytesIO
from typing import TypeAlias

from PIL import Image, ImageColor, ImageDraw, ImageFont

from ._version import __version__

__all__ = ("PyAvatar",
           "__version__",
           "PyAvatarError",
           "RenderingSizeError",
           "FontpathError",
           "FontExtensionNotSupportedError",
           "ImageExtensionNotSupportedError",
           "InvalidColorError",
           "FontLoadError",
           "SupportedImageFmt",
           "SupportedFontExt",
           "SupportedPixelRange",
           )


class PyAvatarError(Exception):
    """Base PyAvatar error.

    :param message: Human readable description of the error.
    :param value: (optional) The value that was rejected.
    """

    def __init__(self, message: str, value: object = None) -> None:
        self.message = message
        self.value = value
        super().__init__(message)


class RenderingSizeError(PyAvatarError):
    """Error with the chosen rendering size."""


class FontpathError(PyAvatarError):
    """Cannot find a font file at this location."""


class FontExtensionNotSupportedError(PyAvatarError):
    """Font file extension not supported."""


class ImageExtensionNotSupportedError(PyAvatarError):
    """Image extension not supported."""


class InvalidColorError(PyAvatarError):
    """Invalid color format."""


class FontLoadError(PyAvatarError):
    """Failed to load font file."""


class SupportedImageFmt(str, Enum):
    """Supported output formats.

    ICO files cannot hold images larger than 256x256, bigger avatars are
    scaled down to that size when written as ICO.

    SVG output needs the optional fonttools dependency, installed with
    `pip install pyavatar[svg]`.
    """

    PNG = "png"
    JPEG = "jpeg"
    ICO = "ico"
    SVG = "svg"


class SupportedFontExt(str, Enum):
    TTF = ".ttf"
    OTF = ".otf"


class SupportedPixelRange(IntEnum):
    MIN = 50
    MAX = 650


_DEFAULT_IMAGE_SIZE = 120
_DEFAULT_FONT_FILEPATH = os.path.join(os.path.dirname(__file__),
                                      "font/Lora.ttf")
_FALLBACK_TEXT = "?"
_DEFAULT_LIGHTNESS = 0.5
_DEFAULT_SATURATION = 0.65
_HEX_COLOR = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}")
_FORMAT_ALIASES = {"jpg": "jpeg"}
_MIME_TYPES = {SupportedImageFmt.ICO: "image/x-icon",
               SupportedImageFmt.SVG: "image/svg+xml"}
_FONT_SIZE_RATIO = 0.6
_SVG_TEMPLATE = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"'
    ' viewBox="0 0 {size} {size}" role="img" aria-label="{label}">'
    '<rect width="100%" height="100%" fill="{background}"/>'
    # the outline is in font units with the y axis pointing up, hence the flip
    '<path transform="translate({x:.2f} {y:.2f}) scale({scale:.5f} '
    '-{scale:.5f})" fill="{fill}" d="{outline}"/></svg>')
# Perceived brightness (0-255) above which the letter is drawn in black
# rather than white, roughly where white text drops under a 3:1 contrast.
_LIGHT_BACKGROUND_THRESHOLD = 150

_HexColor: TypeAlias = str
_RGBColor: TypeAlias = tuple[int, int, int]


def _image_format(value: str, label: str | None = None) -> SupportedImageFmt:
    """Resolve a format name or file extension, case insensitive."""
    name = value.lower() if isinstance(value, str) else ""
    try:
        return SupportedImageFmt(_FORMAT_ALIASES.get(name, name))
    except ValueError:
        raise ImageExtensionNotSupportedError(
            f"Unsupported image format {label or value!r}, expected one of: "
            f"{', '.join(SupportedImageFmt)}.", value) from None


def _glyph_outline(fontpath: str, char: str
                   ) -> tuple[str, tuple[float, float, float, float], int]:
    """Read the outline of a character from a font file.

    Returns the SVG path data and its bounding box (x_min, y_min, x_max,
    y_max), both in font units, and the number of font units per em.
    """
    try:
        from fontTools.pens.boundsPen import BoundsPen
        from fontTools.pens.svgPathPen import SVGPathPen
        from fontTools.ttLib import TTFont, TTLibError
    except ImportError as e:
        raise ImportError("SVG output requires fonttools, install it with "
                          "`pip install pyavatar[svg]`.") from e
    try:
        with TTFont(fontpath, lazy=True) as font:
            glyphs = font.getGlyphSet()
            # same as the raster output, unknown characters get the font's
            # 'missing glyph' box
            glyph = glyphs[font.getBestCmap().get(ord(char), ".notdef")]
            path_pen = SVGPathPen(glyphs, ntos="{:g}".format)
            glyph.draw(path_pen)
            bounds_pen = BoundsPen(glyphs)
            glyph.draw(bounds_pen)
            units_per_em = font["head"].unitsPerEm
    except (OSError, TTLibError, KeyError, AttributeError) as e:
        raise FontLoadError(f"Failed to load font file {fontpath!r}.",
                            fontpath) from e
    return (path_pen.getCommands(),
            bounds_pen.bounds or (0, 0, 0, 0),
            units_per_em)


class PyAvatar:
    """Generate a default avatar from a given string input.

    :param text: Input text to use in the avatar, only its first character
        is drawn. Falls back to '?' when the text is blank.
    :param size: (optional) Integer, size in pixel of the avatar.
    :param fontpath: (optional) Filepath to the font file to use.
    :param color: (optional) Background color as hex string ('#RGB' or
        '#RRGGBB') or RGB tuple (r, g, b) with values 0-255. Defaults to a
        color derived from the text, so a given text always gets the same
        avatar.
    :type color: str or tuple[int, int, int]
    :param capitalize: (optional) Boolean, capitalize the first letter.
    :type capitalize: bool

    Usage::
      >>> from pyavatar import PyAvatar
      >>> avatar = PyAvatar("smallwat3r", size=250)
      >>> avatar.color
      (91, 45, 210)
      >>> avatar.change_color()
      >>> avatar.color
      (203, 22, 126)
      >>> avatar.stream("png")
      b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xfa\x00\x00 ...'
      >>> avatar.base64_image("jpeg")
      'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBg ...'
      >>> import os
      >>> avatar.save(f"{os.getcwd()}/me.png")
    """

    def __init__(self,
                 text: str,
                 size: int = _DEFAULT_IMAGE_SIZE,
                 fontpath: str = _DEFAULT_FONT_FILEPATH,
                 color: _HexColor | _RGBColor | None = None,
                 capitalize: bool = True):
        self._image: Image.Image | None = None
        self._capitalize = capitalize
        self.text = text
        self.size = size
        self.fontpath = fontpath
        self.color = self._default_color(text) if color is None else color
        self._image = self._render()  # fail early on an unusable font

    def __str__(self) -> str:
        return f"{self.text} {self.size}x{self.size} {self.color}"

    @property
    def image(self) -> Image.Image:
        """The rendered avatar, redrawn after any attribute change."""
        if self._image is None:
            self._image = self._render()
        return self._image

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Attribute `text` must be a string.")
        # only care about the first visible character
        char = value.strip()[:1]
        # control characters cannot be drawn, and are not valid in SVG
        if not char.isprintable() or not char:
            char = _FALLBACK_TEXT
        # upper() can return several characters, 'ß' becomes 'SS'
        self._text = char.upper()[:1] if self._capitalize else char
        self._image = None

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Attribute `size` must be an integer.")
        if value < SupportedPixelRange.MIN or value > SupportedPixelRange.MAX:
            raise RenderingSizeError(
                f"Size must be between {SupportedPixelRange.MIN.value} and "
                f"{SupportedPixelRange.MAX.value} pixels, got {value}.", value)
        self._size = value
        self._image = None

    @property
    def fontpath(self) -> str:
        return self._fontpath

    @fontpath.setter
    def fontpath(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Attribute `fontpath` must be a string.")
        if not os.path.isfile(value):
            raise FontpathError(f"Cannot find a font file at {value!r}.",
                                value)
        if not value.lower().endswith(tuple(SupportedFontExt)):
            raise FontExtensionNotSupportedError(
                f"Unsupported font file {os.path.basename(value)!r}, "
                f"expected one of: {', '.join(SupportedFontExt)}.", value)
        self._fontpath = value
        self._image = None

    @property
    def color(self) -> _HexColor | _RGBColor:
        return self._color

    @color.setter
    def color(self, value: _HexColor | _RGBColor) -> None:
        if isinstance(value, str):
            if not _HEX_COLOR.fullmatch(value):
                raise InvalidColorError(
                    f"Invalid hex color {value!r}, expected '#RGB' or "
                    "'#RRGGBB'.", value)
        elif isinstance(value, tuple):
            if len(value) != 3 or not all(
                    isinstance(c, int) and 0 <= c <= 255 for c in value):
                raise InvalidColorError(
                    f"Invalid RGB color {value!r}, expected a tuple of 3 "
                    "integers between 0 and 255.", value)
        else:
            raise InvalidColorError(
                f"Invalid color {value!r}, expected a hex string or an RGB "
                "tuple.", value)
        self._color = value
        self._image = None

    @staticmethod
    def _random_color() -> _RGBColor:
        return (random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255))

    @staticmethod
    def _default_color(text: str) -> _RGBColor:
        # hashlib rather than hash(), which is salted per process. Only the
        # hue varies, so every text gets an equally vivid color.
        digest = sha256(text.encode("utf-8", "replace")).digest()
        hue = int.from_bytes(digest[:2], "big") / 0x10000
        r, g, b = hls_to_rgb(hue, _DEFAULT_LIGHTNESS, _DEFAULT_SATURATION)
        return round(r * 255), round(g * 255), round(b * 255)

    def _text_color(self) -> str:
        color = self.color
        r, g, b = (ImageColor.getrgb(color)[:3]
                   if isinstance(color, str) else color)
        brightness = (299 * r + 587 * g + 114 * b) / 1000
        return "black" if brightness > _LIGHT_BACKGROUND_THRESHOLD else "white"

    def _render(self) -> Image.Image:
        size = self.size
        image = Image.new(mode="RGB", size=(size, size), color=self.color)
        try:
            font = ImageFont.truetype(self.fontpath,
                                      size=int(_FONT_SIZE_RATIO * size))
        except OSError as e:
            raise FontLoadError(
                f"Failed to load font file {self.fontpath!r}.",
                self.fontpath) from e
        draw = ImageDraw.Draw(image)
        left, top, right, bottom = draw.textbbox((0, 0), self.text, font)
        position = ((size - left - right) / 2, (size - top - bottom) / 2)
        draw.text(position, self.text, font=font, fill=self._text_color())
        return image

    def change_color(self, color: _HexColor | _RGBColor | None = None) -> None:
        """Change the background color, picks a random one by default.

        :param color: (optional) Background color as hex string ('#RGB' or
            '#RRGGBB') or RGB tuple (r, g, b) with values 0-255.
        :type color: str or tuple[int, int, int]
        """
        self.color = self._random_color() if color is None else color

    def svg(self) -> str:
        """Render the avatar as an SVG document.

        The letter is embedded as the outline of its glyph in the font, so
        it looks the same on every device and stays sharp at any size.
        Requires fonttools, installed with `pip install pyavatar[svg]`.

        :rtype: str
        """
        size = self.size
        color = self.color
        background = (color if isinstance(color, str)
                      else "#{:02x}{:02x}{:02x}".format(*color))
        outline, bounds, units_per_em = _glyph_outline(self.fontpath,
                                                       self.text)
        x_min, y_min, x_max, y_max = bounds
        scale = int(_FONT_SIZE_RATIO * size) / units_per_em
        return _SVG_TEMPLATE.format(
            size=size,
            label=escape(self.text),
            background=background,
            # centre the bounding box of the letter in the square
            x=size / 2 - scale * (x_min + x_max) / 2,
            y=size / 2 + scale * (y_min + y_max) / 2,
            scale=scale,
            fill=self._text_color(),
            outline=outline)

    def save(self, filepath: str) -> None:
        """Save the avatar under a given file path.

        :param filepath: Filepath where the avatar will be saved, its
            extension picks the format (png, jpeg, jpg, ico or svg).
        """
        filename = os.path.basename(filepath)
        extension = os.path.splitext(filename)[1].lstrip(".")
        fmt = _image_format(extension, label=filename)
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(self.stream(fmt))

    def stream(self,
               filetype: SupportedImageFmt | str = SupportedImageFmt.PNG
               ) -> bytes:
        """Save the avatar in a bytes array.

        :param filetype: (optional) Avatar file format.
        :rtype: bytes
        """
        fmt = _image_format(filetype)
        if fmt is SupportedImageFmt.SVG:
            return self.svg().encode("utf-8")
        stream = BytesIO()
        self.image.save(stream, format=fmt.value, optimize=True)
        return stream.getvalue()

    def base64_image(self,
                     filetype: SupportedImageFmt | str = SupportedImageFmt.PNG
                     ) -> str:
        """Save the avatar as a base64 data URI.

        :param filetype: (optional) Avatar file format.
        :rtype: str
        """
        fmt = _image_format(filetype)
        mime_type = _MIME_TYPES.get(fmt, f"image/{fmt.value}")
        encoded_image = b64encode(self.stream(fmt)).decode("ascii")
        return f"data:{mime_type};base64,{encoded_image}"
