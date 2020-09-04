<h3 align="center">pyavatar</h3>
<p align="center">Create default user avatars from a given string</p>

<h3 align="center">⚠️ Currently under development ⚠️</h3>

![](images/1.png "")
![](images/2.png "")
![](images/3.png "")
![](images/4.png "")
![](images/5.png "")
![](images/6.png "")
![](images/7.png "")
![](images/8.png "")  

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
