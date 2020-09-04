<h3 align="center">pyavatar</h3>
<p align="center">Create default user avatars from a given string</p>

<p align="center">
  <a href="https://travis-ci.com/smallwat3r/pyavatar" rel="nofollow"><img src="https://travis-ci.com/smallwat3r/pyavatar.svg?branch=master" style="max-width:100%;"></a>
  <a href="https://codecov.io/gh/smallwat3r/pyavatar" rel="nofollow"><img src="https://codecov.io/gh/smallwat3r/pyavatar/branch/master/graph/badge.svg" style="max-width:100%;"></a>
</p>

<p align="center">
  <img src="https://github.com/smallwat3r/pyavatar/blob/master/ext/1.png" />
  <img src="https://github.com/smallwat3r/pyavatar/blob/master/ext/2.png" />
  <img src="https://github.com/smallwat3r/pyavatar/blob/master/ext/3.png" />
</p>

```python
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
```
