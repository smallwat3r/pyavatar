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
from base64 import b64encode
from enum import Enum, IntEnum
from io import BytesIO
from typing import TypeAlias

from PIL import Image, ImageDraw, ImageFont

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
           )


class PyAvatarError(Exception):
    """Base PyAvatar error."""

    def __init__(self, value: str, message: str = "", info: str = "") -> None:
        self.value = value
        self.message = message or self.__doc__
        self.info = info
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.value} -> {self.message} {self.info}".strip()


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


def csv(str_enum: type[Enum]) -> str:
    assert issubclass(str_enum, str) and issubclass(str_enum, Enum)
    return ", ".join(list(str_enum))


class SupportedImageFmt(str, Enum):
    PNG = "png"
    JPEG = "jpeg"
    ICO = "ico"


class SupportedFontExt(str, Enum):
    TTF = ".ttf"
    OTF = ".otf"


class SupportedPixelRange(IntEnum):
    MIN = 50
    MAX = 650


_DEFAULT_IMAGE_SIZE = 120
_DEFAULT_FONT_FILEPATH = os.path.join(os.path.dirname(__file__),
                                      "font/Lora.ttf")

_HexColor: TypeAlias = str
_RGBColor: TypeAlias = tuple[int, int, int]


class PyAvatar:
    """Generate a default avatar from a given string input.

    :param text: Input text to use in the avatar.
    :param size: (optional) Integer, size in pixel of the avatar.
    :param fontpath: (optional) Filepath to the font file to use.
    :param color: (optional) Background color as hex string ('#RGB' or
        '#RRGGBB') or RGB tuple (r, g, b) with values 0-255.
    :type color: str or tuple[int, int, int]
    :param capitalize: (optional) Boolean, capitalize the first letter.
    :type capitalize: bool

    Usage::
      >>> from pyavatar import PyAvatar
      >>> avatar = PyAvatar("smallwat3r", size=250)
      >>> avatar.color
      (191, 91, 81)
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
        self.text = text
        if capitalize:
            self.text = text.upper()
        self.size = size
        self.fontpath = fontpath
        self.color = color or self._random_color()
        self.image = self.__generate_avatar()

    def __str__(self) -> str:
        return f"{self.text} {self.size}x{self.size} {self.color}"

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Attribute `text` must be a string.")
        self._text = value[0]  # only care about the first character

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Attribute `size` must be an integer.")
        if value < SupportedPixelRange.MIN or value > SupportedPixelRange.MAX:
            raise RenderingSizeError(str(value),
                                     ("Size must fit within range "
                                      f"min={SupportedPixelRange.MIN} "
                                      f"max={SupportedPixelRange.MAX}."))
        self._size = value

    @property
    def fontpath(self) -> str:
        return self._fontpath

    @fontpath.setter
    def fontpath(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Attribute `fontpath` must be a string.")
        if not os.path.exists(value):
            raise FontpathError(value)
        if not value.lower().endswith(tuple(SupportedFontExt)):
            raise FontExtensionNotSupportedError(
                os.path.basename(value),
                info=f"Supported extensions: {csv(SupportedFontExt)}.")
        self._fontpath = value

    @property
    def color(self) -> _HexColor | _RGBColor:
        return self._color

    @color.setter
    def color(self, value: _HexColor | _RGBColor) -> None:
        if isinstance(value, str):
            if not value.startswith("#") or len(value) not in (4, 7):
                raise InvalidColorError(
                    value,
                    message="Hex color must be in format '#RGB' or '#RRGGBB'.")
        elif isinstance(value, tuple):
            if len(value) != 3 or not all(
                    isinstance(c, int) and 0 <= c <= 255 for c in value):
                raise InvalidColorError(
                    str(value),
                    message="RGB color must be a tuple of 3 integers (0-255).")
        else:
            raise InvalidColorError(
                str(value),
                message="Color must be a hex string or RGB tuple.")
        self._color = value

    @staticmethod
    def _random_color() -> _RGBColor:
        return (random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255))

    def __generate_avatar(self) -> Image.Image:
        image = Image.new(mode="RGB",
                          size=(self.size, self.size),
                          color=self.color)
        try:
            font = ImageFont.truetype(self.fontpath, size=int(0.6 * self.size))
        except OSError as e:
            raise FontLoadError(self.fontpath,
                                message="Failed to load font file.") from e
        draw = ImageDraw.Draw(image)
        _, _, w_txt, h_txt = draw.textbbox((0, 0), self.text, font)
        off_x, off_y, _, _ = font.getbbox(self.text)
        position = ((self.size / 2 - (w_txt + off_x) / 2),
                    (self.size / 2 - (h_txt + off_y) / 2))
        draw.text(position, self.text, font=font)
        return image

    def change_color(self, color: _HexColor | _RGBColor | None = None) -> None:
        """Redraw the avatar with a new background color.

        :param color: (optional) Background color as hex string ('#RGB' or
            '#RRGGBB') or RGB tuple (r, g, b) with values 0-255.
        :type color: str or tuple[int, int, int]
        """
        self.color = color or self._random_color()
        self.image = self.__generate_avatar()

    def save(self, filepath: str) -> None:
        """Save the avatar under a given file path.

        :param filepath: Filepath where the avatar will be saved.
        """
        extension = os.path.splitext(filepath)[1].lstrip(".")
        if extension not in set(SupportedImageFmt):
            raise ImageExtensionNotSupportedError(
                os.path.basename(filepath),
                info=f"Supported formats: {csv(SupportedImageFmt)}.")
        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        self.image.save(filepath, optimize=True)

    def stream(self,
               filetype: SupportedImageFmt = SupportedImageFmt.PNG) -> bytes:
        """Save the avatar in a bytes array.

        :param filetype: (optional) Avatar file format.
        :rtype: bytes
        """
        if filetype.lower() not in set(SupportedImageFmt):
            raise ImageExtensionNotSupportedError(
                filetype, info=f"Supported formats: {csv(SupportedImageFmt)}.")
        stream = BytesIO()
        self.image.save(stream, format=filetype.value, optimize=True)
        return stream.getvalue()

    def base64_image(self,
                     filetype: SupportedImageFmt = SupportedImageFmt.PNG
                     ) -> str:
        """Save the avatar as a base64 image.

        :param filetype: (optional) Avatar file format.
        :rtype: str
        """
        encoded_image = b64encode(self.stream(filetype)).decode("utf-8")
        return f"data:image/{filetype.value};base64,{encoded_image}"
