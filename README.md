<h3 align="center">pyavatar</h3>
<p align="center">Create default user avatars from a given string</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/smallwat3r/pyavatar/master/ext/1.png" />
  <img src="https://raw.githubusercontent.com/smallwat3r/pyavatar/master/ext/2.png" />
  <img src="https://raw.githubusercontent.com/smallwat3r/pyavatar/master/ext/3.png" />
  <img src="https://raw.githubusercontent.com/smallwat3r/pyavatar/master/ext/4.png" />
</p>

<p align="center">
  <a href="https://travis-ci.com/smallwat3r/pyavatar" rel="nofollow"><img src="https://travis-ci.com/smallwat3r/pyavatar.svg?branch=master" style="max-width:100%;"></a>
  <a href="https://codecov.io/gh/smallwat3r/pyavatar" rel="nofollow"><img src="https://codecov.io/gh/smallwat3r/pyavatar/branch/master/graph/badge.svg" style="max-width:100%;"></a>
</p>

This package allows the creation of simple user avatars that can be 
used in web-applications.  
Avatars are generated from the first letter of a given string input.  

### Installation  

Pyavatar is on PyPI so all you need is:
```sh
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
>>> avatar = PyAvatar("smallwat3r", font="/Users/me/fonts/myfont.ttf")  # use a specific font
```

Change the avatar color
```python
>>> avatar.color
(191, 91, 81)
>>> avatar.change_color()  # random color
>>> avatar.color
(203, 22, 126) 
>>> avatar.change_color("#28b0c8")  # using an hex color
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
<img src={{ image }} alt="my avatar" />
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
