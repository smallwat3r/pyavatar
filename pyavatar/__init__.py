# pylint: disable=unsupported-membership-test
"""
Pyavatar Library
~~~~~~~~~~~~~~~~~

Pyavatar is a library, written in Python, to quickly generate simple default
user avatars to use in a web application or elsewhere.

:copyright: (c) 2020 by Matthieu Petiteau.
:license: MIT, see LICENSE for more details.
"""

import enum
import operator
import os
import random
from base64 import b64encode
from io import BytesIO
from typing import Tuple, Union

from PIL import Image, ImageDraw, ImageFont

from .version import __version__

__all__ = ("PyAvatar", "__version__")


class PyAvatarError(Exception):
    """Base class for pyavatar exceptions."""

    def __init__(self, value: str, message: str = None, info: str = ""):
        self.value = value
        self.message = message or self.__doc__
        self.info = info
        super().__init__(self.message)

    def __str__(self):
        return f"{self.value} -> {self.message} {self.info}"


class RenderingSizeError(PyAvatarError):
    """Error with the chosen rendering size."""


class FontpathError(PyAvatarError):
    """Cannot find a font file at this location."""


class FontExtensionNotSupportedError(PyAvatarError):
    """Font file extension not supported."""


class AvatarExtensionNotSupportedError(PyAvatarError):
    """Avatar extension not supported."""


class ClassPropertyDescriptor:
    """Add a property to a class."""

    def __init__(self, func):
        self._func = func

    def __get__(self, obj, owner):
        return self._func(owner)


def classproperty(func):
    """Decorator function to add a property to a class."""
    return ClassPropertyDescriptor(func)


class BaseValidators(enum.Enum):
    """Base enum class for validators."""

    @classproperty
    def list(cls):  # pylint: disable=no-self-argument
        """Build a list of values."""
        return [ext.value for ext in cls]

    @classproperty
    def csv(cls):  # pylint: disable=no-self-argument
        """Build a comma separated list of values."""
        return ", ".join(cls.list)


@enum.unique
class ValidImgFormats(BaseValidators):
    """Avatar supported formats."""

    PNG = "png"
    JPEG = "jpeg"
    ICO = "ico"


@enum.unique
class ValidFontFormats(BaseValidators):
    """Font supported formats."""

    TTF = ".ttf"
    OTF = ".otf"


@enum.unique
class ValidPixelRange(BaseValidators):
    """Avatar pixel size."""

    MIN = 50
    MAX = 650


class BaseConfig:
    """Base class constants."""

    DEFAULT_IMG_SIZE = 120
    DEFAULT_FILEPATH = f"{os.getcwd()}/avatar.png"
    DEFAULT_FONTPATH = os.path.join(os.path.dirname(__file__), "font/Lora.ttf")


class PyAvatar(BaseConfig):
    """Generate default avatars from a string input.

    :param text: Input text to use in the avatar.
    :param size: (optional) Size in pixel of the avatar.
    :param fontpath: (optional) Filepath to the font file to use.
    :param color: (optional) Background color (hex or rgb).

    Usage::
      >>> from pyavatar import PyAvatar
      >>> avatar = PyAvatar("smallwat3r", size=250)
      >>> avatar.color
      (191, 91, 81)
      >>> avatar.change_color()
      >>> avatar.color
      (203, 22, 126)
      >>> avatar.stream("png")
      b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xfa\x00\x00 ...
      >>> avatar.base64_image("jpeg")
      data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBg ...
      >>> import os
      >>> avatar.save(f"{os.getcwd()}/me.png")
    """

    def __init__(self,
                 text: str,
                 size: int = BaseConfig.DEFAULT_IMG_SIZE,
                 fontpath: str = BaseConfig.DEFAULT_FONTPATH,
                 color: Union[str, Tuple[int, int, int]] = None):
        self.text = text
        self.size = size
        self.fontpath = fontpath
        self.color = color or self._random_color()
        self.img = self.__generate()

    def __str__(self) -> str:
        return f"{self.text} {self.size}x{self.size} {self.color}"

    text = property(operator.attrgetter("_text"))

    @text.setter  # type: ignore
    def text(self, t):
        """Validate text attribute and isolate first letter used for avatar."""
        if not isinstance(t, str):
            raise TypeError("Attribute ``text`` needs to be an string.")
        self._text = t[0].upper()

    size = property(operator.attrgetter("_size"))

    @size.setter  # type: ignore
    def size(self, s):
        """Validate size attribute."""
        if not isinstance(s, int):
            raise TypeError("Attribute ``size`` needs to be an integer.")
        if s < ValidPixelRange.MIN.value or s > ValidPixelRange.MAX.value:
            raise RenderingSizeError(
                s, f"Rendering size must in range {ValidPixelRange.list}")
        self._size = s

    fontpath = property(operator.attrgetter("_fontpath"))

    @fontpath.setter  # type: ignore
    def fontpath(self, t):
        """Validate fontpath attribute."""
        if not isinstance(t, str):
            raise TypeError("Attribute ``fontpath`` needs to be a string.")
        if not os.path.exists(t):
            raise FontpathError(t)
        if (not t.lower().endswith(ValidFontFormats.TTF.value)
                and not t.lower().endswith(ValidFontFormats.OTF.value)):
            raise FontExtensionNotSupportedError(
                os.path.basename(t),
                info=f"Supported formats: {ValidFontFormats.csv}")
        self._fontpath = t

    @staticmethod
    def _random_color() -> Tuple[int, int, int]:
        """Generate avatar background color."""
        return (random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255))

    def __generate(self) -> Image:
        """Private function used to generate an avatar."""
        img = Image.new(mode="RGB",
                        size=(self.size, self.size),
                        color=self.color)
        font = ImageFont.truetype(self.fontpath, size=int(0.6 * self.size))
        draw = ImageDraw.Draw(img)
        w_txt, h_txt = draw.textsize(self.text, font)
        off_x, off_y = font.getoffset(self.text)
        position = ((self.size / 2 - (w_txt + off_x) / 2),
                    (self.size / 2 - (h_txt + off_y) / 2))
        draw.text(position, self.text, font=font)
        return img

    def change_color(self, color: Union[str, Tuple[int, int, int]] = None):
        """Redraw the avatar with a new color.

        :param color: (optional) Background color (hex or rgb).
        """
        self.color = color or self._random_color()
        self.img = self.__generate()

    def save(self, filepath: str = BaseConfig.DEFAULT_FILEPATH) -> None:
        """Save the avatar under a given output directory and name.

        :param filepath: (optional) Filepath where the avatar will be saved.
        """
        extension = os.path.splitext(filepath)[1].split(".")[1]
        if extension not in ValidImgFormats.list:
            raise AvatarExtensionNotSupportedError(
                os.path.basename(filepath),
                info=f"Supported formats: {ValidImgFormats.csv}")
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.img.save(filepath, optimize=True)

    def stream(self, filetype: str = ValidImgFormats.PNG.value) -> bytes:
        """Save the avatar in a bytes array.

        :param filetype: (optional) Avatar file format.
        :rtype: bytes
        """
        if filetype.lower() not in ValidImgFormats.list:
            raise AvatarExtensionNotSupportedError(
                filetype, info=f"Supported formats: {ValidImgFormats.csv}")
        stream = BytesIO()
        self.img.save(stream, format=filetype, optimize=True)
        return stream.getvalue()

    def base64_image(self, filetype: str = ValidImgFormats.PNG.value) -> str:
        """Save the avatar as a base64 image.

        :param filetype: (optional) Avatar file format.
        :rtype: str
        """
        encoded_image = b64encode(self.stream(filetype)).decode("utf-8")
        return f"data:image/{filetype};base64,{encoded_image}"
