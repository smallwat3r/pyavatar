# pylint: disable=unsupported-membership-test,too-many-arguments
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
           )


class PyAvatarError(Exception):
    """Base PyAvatar error."""

    def __init__(self,
                 value: str,
                 message: str | None = None,
                 info: str = "") -> None:
        self.value = value
        self.message = message or self.__doc__
        self.info = info
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.value} -> {self.message} {self.info}"


class RenderingSizeError(PyAvatarError):
    """Error with the chosen rendering size."""


class FontpathError(PyAvatarError):
    """Cannot find a font file at this location."""


class FontExtensionNotSupportedError(PyAvatarError):
    """Font file extension not supported."""


class ImageExtensionNotSupportedError(PyAvatarError):
    """Image extension not supported."""


class _BaseEnumUtils:

    @classmethod
    def get_set(cls) -> set[str]:
        return {attribute.value for attribute in cls}  # type: ignore # pylint: disable=not-an-iterable

    @classmethod
    def get_csv(cls) -> str:
        return ", ".join(cls.get_set())


class SupportedImageFormat(_BaseEnumUtils, str, Enum):
    PNG = "png"
    JPEG = "jpeg"
    ICO = "ico"


class SupportedFontFormat(_BaseEnumUtils, str, Enum):
    TTF = ".ttf"
    OTF = ".otf"


class SupportedPixelRange(_BaseEnumUtils, IntEnum):
    MIN = 50
    MAX = 650


_DEFAULT_IMAGE_SIZE = 120
_DEFAULT_FILEPATH = f"{os.getcwd()}/avatar.png"
_DEFAULT_FONT_FILEPATH = os.path.join(os.path.dirname(__file__),
                                      "font/Lora.ttf")

_HexColor: TypeAlias = str
_RGBColor: TypeAlias = tuple[int, int, int]


class PyAvatar:
    """Generate a default avatar from a given string input.

    :param text: Input text to use in the avatar.
    :param size: (optional) Integer, size in pixel of the avatar.
    :param fontpath: (optional) Filepath to the font file to use.
    :param color: (optional) hex or rgb color code for the background.
    :type color: string or tuple
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
        self._text = value[0]  # keep the first letter

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("Attribute `size` must be an integer.")
        if value < SupportedPixelRange.MIN or value > SupportedPixelRange.MAX:
            raise RenderingSizeError(
                str(value),
                f"Size must fit in range {SupportedPixelRange.get_set()}.")
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
        if not value.lower().endswith(
            (SupportedFontFormat.TTF, SupportedFontFormat.OTF)):
            raise FontExtensionNotSupportedError(
                os.path.basename(value),
                info=f"Supported formats: {SupportedFontFormat.get_csv()}.")
        self._fontpath = value

    @staticmethod
    def _random_color() -> _RGBColor:
        return (random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255))

    def __generate_avatar(self) -> Image:
        image = Image.new(mode="RGB",
                          size=(self.size, self.size),
                          color=self.color)
        font = ImageFont.truetype(self.fontpath, size=int(0.6 * self.size))
        draw = ImageDraw.Draw(image)
        w_txt, h_txt = draw.textsize(self.text, font)
        off_x, off_y = font.getoffset(self.text)
        position = ((self.size / 2 - (w_txt + off_x) / 2),
                    (self.size / 2 - (h_txt + off_y) / 2))
        draw.text(position, self.text, font=font)
        return image

    def change_color(self, color: _HexColor | _RGBColor | None = None) -> None:
        """Redraw the avatar with a new background color.

        :param color: (optional) hex or rgb color code for the background.
        :type color: string or tuple
        """
        self.color = color or self._random_color()
        self.image = self.__generate_avatar()

    def save(self, filepath: str = _DEFAULT_FILEPATH) -> None:
        """Save the avatar under a given file path.

        :param filepath: (optional) Filepath where the avatar will be saved.
        """
        extension = os.path.splitext(filepath)[1].split(".")[1]
        if extension not in SupportedImageFormat.get_set():
            raise ImageExtensionNotSupportedError(
                os.path.basename(filepath),
                info=f"Supported formats: {SupportedImageFormat.get_csv()}.")
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.image.save(filepath, optimize=True)

    def stream(
            self,
            filetype: SupportedImageFormat = SupportedImageFormat.PNG
    ) -> bytes:
        """Save the avatar in a bytes array.

        :param filetype: (optional) Avatar file format.
        :rtype: bytes
        """
        if filetype.lower() not in SupportedImageFormat.get_set():
            raise ImageExtensionNotSupportedError(
                filetype,
                info=f"Supported formats: {SupportedImageFormat.get_csv()}.")
        stream = BytesIO()
        self.image.save(stream, format=filetype, optimize=True)
        return stream.getvalue()

    def base64_image(
            self,
            filetype: SupportedImageFormat = SupportedImageFormat.PNG) -> str:
        """Save the avatar as a base64 image.

        :param filetype: (optional) Avatar file format.
        :rtype: str
        """
        encoded_image = b64encode(self.stream(filetype)).decode("utf-8")
        return f"data:image/{filetype};base64,{encoded_image}"
