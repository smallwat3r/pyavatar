<h3 align="center">pyavatar</h3>
<p align="center">Create default user avatars from a given string</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/smallwat3r/pyavatar/master/ext/1.svg" width="36" alt="" />
  <img src="https://raw.githubusercontent.com/smallwat3r/pyavatar/master/ext/2.svg" width="36" alt="" />
  <img src="https://raw.githubusercontent.com/smallwat3r/pyavatar/master/ext/3.svg" width="36" alt="" />
  <img src="https://raw.githubusercontent.com/smallwat3r/pyavatar/master/ext/4.svg" width="36" alt="" />
  <img src="https://raw.githubusercontent.com/smallwat3r/pyavatar/master/ext/5.svg" width="36" alt="" />
  <img src="https://raw.githubusercontent.com/smallwat3r/pyavatar/master/ext/6.svg" width="36" alt="" />
  <img src="https://raw.githubusercontent.com/smallwat3r/pyavatar/master/ext/7.svg" width="36" alt="" />
  <img src="https://raw.githubusercontent.com/smallwat3r/pyavatar/master/ext/8.svg" width="36" alt="" />
</p>

<p align="center">
  <a href="https://pypi.org/project/pyavatar"><img src="https://img.shields.io/pypi/v/pyavatar.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/pyavatar"><img src="https://img.shields.io/pypi/pyversions/pyavatar.svg" alt="Supported Python versions"></a>
  <a href="https://github.com/smallwat3r/pyavatar/actions/workflows/ci.yml"><img src="https://github.com/smallwat3r/pyavatar/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
  <a href="https://codecov.io/gh/smallwat3r/pyavatar"><img src="https://codecov.io/gh/smallwat3r/pyavatar/branch/master/graph/badge.svg" alt="Coverage"></a>
  <a href="https://github.com/smallwat3r/pyavatar/blob/master/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT licence"></a>
</p>

Pyavatar generates the simple letter avatars that web applications show
until a user uploads a picture: a coloured square with the first letter of
their name.

- **Stable**, the background colour is derived from the input, so a given
  string always gets the same avatar, with no need to store it
- **Readable**, the letter is drawn in black or white, whichever contrasts
  best with the background
- **Flexible output**, as a file, raw bytes or a base64 data URI, in PNG,
  JPEG, ICO or SVG
- **Small**, one class, typed, with [Pillow](https://python-pillow.org) as
  the only required dependency

## Installation

```
pip install pyavatar
```

Requires Python 3.10 or newer. SVG output needs one extra dependency,
[fontTools](https://github.com/fonttools/fonttools), installed with:

```
pip install "pyavatar[svg]"
```

## Quick start

```python
>>> from pyavatar import PyAvatar
>>>
>>> avatar = PyAvatar("smallwat3r")
>>> avatar.save("me.png")
```

## Usage

### Creating an avatar

```python
>>> avatar = PyAvatar("smallwat3r", size=250)  # use a specific size
>>> avatar = PyAvatar("smallwat3r", capitalize=False)  # keep the letter as typed
>>> avatar = PyAvatar("smallwat3r", color=(40, 176, 200))  # use a specific colour
>>> avatar = PyAvatar("smallwat3r", fontpath="/Users/me/fonts/myfont.ttf")  # use a specific font
```

| Parameter    | Default            | Description                                                      |
|--------------|--------------------|------------------------------------------------------------------|
| `text`       | required           | Input string, only its first character is drawn                  |
| `size`       | `120`              | Width and height in pixels, from 50 to 650                       |
| `fontpath`   | bundled Lora font  | Path to a `.ttf` or `.otf` font file                             |
| `color`      | derived from text  | Background as `'#RGB'`, `'#RRGGBB'` or an `(r, g, b)` tuple      |
| `capitalize` | `True`             | Draw the letter in upper case                                    |

Leading whitespace is ignored, and a blank string gives a `?` avatar.

Any `.ttf` or `.otf` font works, the tiles at the top of this page each use a
different one, saved as SVG.

### Colours

```python
>>> avatar = PyAvatar("smallwat3r")
>>> avatar.color  # always the same for a given string
(91, 45, 210)
>>> avatar.change_color()  # random colour
>>> avatar.color
(203, 22, 126)
>>> avatar.change_color("#28b0c8")  # using a hex colour code
>>> avatar.color
'#28b0c8'
```

### Getting the image

As a base64 data URI
```python
>>> image = avatar.base64_image("jpeg")
>>> image
'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBg ...'
```

which can be rendered directly in an HTML tag, with Jinja or another template
engine
```html
<img src="{{ image }}" alt="My avatar" />
```

As bytes
```python
>>> avatar.stream("png")
b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xfa\x00\x00 ...'
```

As a file, the extension picks the format (`png`, `jpeg`, `jpg`, `ico` or
`svg`) and missing directories are created
```python
>>> avatar.save("avatars/me.png")
```

As SVG, smaller than the PNG and sharp at any size. The letter is embedded
as the outline of its glyph, so it looks the same on every device and
follows `fontpath` like the other formats (requires the `svg` extra)
```python
>>> avatar.svg()
'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" ...'
```

`"svg"` also works with `stream`, `base64_image` and `save`. Prefer it for
web pages, and keep PNG or JPEG where SVG is not supported, like emails.

As a [Pillow image](https://pillow.readthedocs.io/en/stable/reference/Image.html),
for anything else
```python
>>> avatar.image
<PIL.Image.Image image mode=RGB size=120x120>
```

### Serving avatars from a web application

Avatars are stable, so they can be generated on the fly and cached by the
browser. With Flask for example:

```python
from flask import Flask, Response
from pyavatar import PyAvatar

app = Flask(__name__)


@app.get("/avatar/<username>.png")
def avatar(username: str) -> Response:
    return Response(PyAvatar(username).stream("png"),
                    mimetype="image/png",
                    headers={"Cache-Control": "public, max-age=86400"})
```

### Updating an avatar

`text`, `size`, `color` and `fontpath` can be changed after creation, the
image is redrawn on the next access.

```python
>>> avatar.size = 300
>>> avatar.text = "bob"
>>> print(avatar)
B 300x300 #28b0c8
```

### Errors

Invalid values raise a subclass of `PyAvatarError` (`RenderingSizeError`,
`InvalidColorError`, `FontpathError`, `FontExtensionNotSupportedError`,
`FontLoadError`, `ImageExtensionNotSupportedError`), wrong argument types
raise a `TypeError`.

```python
>>> from pyavatar import PyAvatarError
>>> try:
...     PyAvatar("smallwat3r", size=10)
... except PyAvatarError as e:
...     print(e)
10 -> Size must fit within range min=50 max=650.
```

### Good to know

- The bundled Lora font covers Latin and Cyrillic scripts. For other scripts
  (CJK, Arabic etc.) pass a font that supports them with `fontpath`,
  otherwise the letter is drawn as an empty box.
- SVG letters are drawn in a single colour, so colour emoji fonts are not
  supported in SVG.
- ICO files cannot hold images larger than 256x256, bigger avatars are scaled
  down to that size when written as ICO.

## Development

Requires Python 3.10 or newer and `make`.

```
make venv deps  # create a virtual environment and install the dependencies
make tests      # run the unit tests
make ruff       # lint
make mypy       # type check
make ci         # run all of the above
make yapf       # format the code with YAPF
make release    # build and publish to PyPI
```

## Licence

[MIT](https://github.com/smallwat3r/pyavatar/blob/master/LICENSE)
