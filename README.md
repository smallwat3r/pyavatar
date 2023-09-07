<h3 align="center">pyavatar</h3>
<p align="center">Create default user avatars from a given string</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/smallwat3r/pyavatar/master/ext/1.png" />
  <img src="https://raw.githubusercontent.com/smallwat3r/pyavatar/master/ext/2.png" />
  <img src="https://raw.githubusercontent.com/smallwat3r/pyavatar/master/ext/3.png" />
</p>

<p align="center">
  <a href="https://codecov.io/gh/smallwat3r/pyavatar" rel="nofollow"><img src="https://codecov.io/gh/smallwat3r/pyavatar/branch/master/graph/badge.svg" style="max-width:100%;"></a>
  <a href="https://pypi.org/project/pyavatar" rel="nofollow"><img src="https://img.shields.io/pypi/wheel/pyavatar.svg" style="max-width:100%;"></a>
  <a href="https://github.com/smallwat3r/pyavatar/blob/master/LICENSE" rel="nofollow"><img src="https://img.shields.io/badge/License-MIT-green.svg" style="max-width:100%;"></a>
</p>

This package creates simple user avatars that can be used in web-applications.  
Avatars are generated from the first letter of a given string input.  

### Installation

Pyavatar is on Pypi so all you need is:
```
pip install pyavatar
```

### Usage

Generate an avatar  
```python
>>> from pyavatar import PyAvatar
>>>
>>> avatar = PyAvatar("smallwat3r", size=250)  # use a specific size
>>> avatar = PyAvatar("smallwat3r", capitalize=False)  # without capitalization
>>> avatar = PyAvatar("smallwat3r", color=(40, 176, 200))  # use a specific color
>>> avatar = PyAvatar("smallwat3r", fontpath="/Users/me/fonts/myfont.ttf")  # use a specific font
```

Change the avatar color
```python
>>> avatar.color
(191, 91, 81)
>>> avatar.change_color()  # random color
>>> avatar.color
(203, 22, 126) 
>>> avatar.change_color("#28b0c8")  # using an hex color code
>>> avatar.color
'#28b0c8'
```

Save the avatar as a base64 image
```python
>>> image = avatar.base64_image("jpeg")
'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBg ...'
```

You can then render it in an html tag with Jinja or another template engine
```html
<img src="{{ image }}" alt="My avatar" />
```

Or save it as a bytes array
```python
>>> avatar.stream("png")
b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xfa\x00\x00 ...'
```

Or save it as a file locally
```python
>>> import os
>>> avatar.save(f"{os.getcwd()}/me.png")
```

### Development

#### Requirements

Make sure you're using a version of Python >= 3.10

- Create a virtual environment and install the dependencies
  ```
  make venv deps
  ```

#### Sanity checks

- Unit tests
  ```
  make tests
  ```

- Mypy 
  ```
  make mypy
  ```

- Ruff 
  ```
  make ruff
  ```

- Run all the above
  ```
  make ci
  ```

#### Code formatting

 We're using [YAPF](https://github.com/google/yapf) to format the code
```
make yapf
```

#### Release to Pypi

```
make release
```
