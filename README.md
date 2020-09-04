<h3 align="center">⚠️ Currently under development ⚠️</h3>

<h3 align="center">pyavatar</h3>
<p align="center">Create default user avatars from a given string</p>

![](images/1.png "")
![](images/2.png "")
![](images/3.png "")
![](images/4.png "")
![](images/5.png "")
![](images/6.png "")
![](images/7.png "")
![](images/8.png "")  

```python
from pyavatar import PyAvatar

# Generate an avatar
avatar = PyAvatar("smallwat3r", size=250)
print(avatar.color)
# (191, 91, 81)

# Change the color background
avatar.change_color()
print(avatar.color)
# (203, 22, 126)

# Load avatar with a specific color
avatar = PyAvatar("matt", color="#76a69a")      # hex
avatar = PyAvatar("pat", color=(104, 232, 93))  # rgb

# Save avatar in bytes array png image
avatar.stream("png")
# b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xfa\x00\x00 (...)

# Save avatar as a base64 jpeg image
avatar.base64_image("jpeg")
# data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBg (...)

# Save avatar locally
import os
avatar.save(f"{os.getcwd()}/me.png")
```
