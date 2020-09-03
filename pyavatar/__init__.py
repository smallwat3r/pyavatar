import operator
import os
import random
from io import BytesIO
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from .version import __version__

__all__ = (
    "PyAvatar",
    "PyAvatarError",
    "RenderingSizeTooSmallError",
    "TypoPathError",
    "TypoExtensionNotSupported",
    "AvatarExtensionNotSupported",
    "__version__",
)


class PyAvatarError(Exception):
    """Base class for other exceptions"""

    def __init__(self, value, message):
        self.value = value
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.value} -> {self.message}"


class RenderingSizeTooSmallError(PyAvatarError):
    """The chosen rendering size is too small."""


class TypoPathError(PyAvatarError):
    """Cannot locate a file at this path."""


class TypoExtensionNotSupportedError(PyAvatarError):
    """Typo file extension not supported."""


class AvatarExtensionNotSupportedError(PyAvatarError):
    """The avatar extension format is not supported."""


class BaseConfig:
    """Base class constants."""

    MIN_IMG_SIZE = 380
    DEFAULT_OUTPUT_PATH = os.getcwd()
    DEFAULT_FILENAME = "avatar.png"
    AVAILABLE_FORMATS = ("jpeg", "png", "ico")
    DEFAULT_TYPO = os.path.join(os.path.dirname(__file__), "font/Lora.ttf")


class PyAvatar(BaseConfig):
    """Generate an avatar.

    Attributes:
        text (str): Input text of the avatar.
        size (int): Size in pixel of the avatar.
        typo (str): Path to a Truetype font file.
        color: Avatar background color (Hex or RGB)

    """

    def __init__(
        self,
        text,
        size=BaseConfig.MIN_IMG_SIZE,
        typo=BaseConfig.DEFAULT_TYPO,
        color=None,
    ):
        self.size = size
        self.typo = typo
        self.text = text
        self.color = self.__colorize() if not color else color
        self.img = self.__generate()

    def __str__(self) -> str:
        return f"{self.text} {self.size}x{self.size} {self.color}"

    text = property(operator.attrgetter("_text"))
    size = property(operator.attrgetter("_size"))
    typo = property(operator.attrgetter("_typo"))

    @text.setter  # type: ignore
    def text(self, t):
        """Validate text attribute and isolate first letter used for avatar."""
        if not isinstance(t, str):
            raise TypeError(f"Attribute ``text`` needs to be an string.")
        self._text = t[0].upper()

    @size.setter  # type: ignore
    def size(self, s):
        """Validate size attribute."""
        if not isinstance(s, int):
            raise TypeError(f"Attribute ``size`` needs to be an integer.")
        if s < self.MIN_IMG_SIZE:
            raise RenderingSizeTooSmallError(
                s, "Chosen rendering size too small."
            )
        self._size = s

    @typo.setter  # type: ignore
    def typo(self, t):
        """Validate typo attribute."""
        if not isinstance(t, str):
            raise TypeError(f"Attribute ``typo`` needs to be a string.")
        if not os.path.exists(t):
            raise TypoPathError(t, "Cannot locate font file.")
        if not t.lower().endswith(".ttf"):
            raise TypoExtensionNotSupportedError(
                t.split("/")[-1],
                "File extension not supported, needs a Truetype font (.ttf)",
            )
        self._typo = t

    @staticmethod
    def __colorize() -> Tuple[int, int, int]:
        """Generate avatar background color."""
        return (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

    def __generate(self) -> Image:
        """Private function used to generate an avatar."""
        img = Image.new(
            mode="RGB", size=(self.size, self.size), color=self.color
        )
        font = ImageFont.truetype(self.typo, size=int(0.7 * self.size))
        draw = ImageDraw.Draw(img)

        w_txt, h_txt = draw.textsize(self.text, font)
        off_x, off_y = font.getoffset(self.text)
        position = (
            (self.size / 2 - (w_txt + off_x) / 2),
            (self.size / 2 - (h_txt + off_y) / 2),
        )

        draw.text(position, self.text, font=font)
        return img

    def change_color(self) -> None:
        """Redraw the avatar with a new color."""
        self.color = self.__colorize()
        self.img = self.__generate()

    def show(self) -> None:
        """Show a preview of the avater in a local image viewer."""
        self.img.show()

    def save(
        self,
        path=BaseConfig.DEFAULT_OUTPUT_PATH,
        filename=BaseConfig.DEFAULT_FILENAME,
    ) -> None:
        """Save the avatar under a given output directory and name.

        Args:
            path (str): Directory where to save the file.
            filename(str): Name of file.

        """
        if filename.split(".")[-1].lower() not in self.AVAILABLE_FORMATS:
            raise AvatarExtensionNotSupportedError(
                filename,
                "Avatar extension not supported. Supported formats: "
                f"{self.AVAILABLE_FORMATS}",
            )
        if not os.path.exists(path):
            os.makedirs(path)
        self.img.save(f"{path}/{filename}", optimize=True)

    def stream(self, filetype="png"):
        """Save the avatar in bytes array.

        Args:
            filetype (str): Avatar file format.

        """
        if filetype.lower() not in self.AVAILABLE_FORMATS:
            raise AvatarExtensionNotSupportedError(
                filetype,
                "Avatar extension not supported. Supported formats: "
                f"{self.AVAILABLE_FORMATS}",
            )
        stream = BytesIO()
        self.img.save(stream, format=filetype, optimize=True)
        return stream.getvalue()
