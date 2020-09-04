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
print(avatar)
# S 250x250 (191, 91, 81)

# Change the color background
avatar.change_color()
print(avatar)
# S 250x250 (203, 22, 126)

# Load avatar with a specific color
avatar = PyAvatar("matt", color="#76a69a")      # hex
avatar = PyAvatar("pat", color=(104, 232, 93))  # rgb

# Get avatar in byte array
avatar.stream("png")
# b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xfa\x00\x00 (...)

# Save avatar locally
import os
avatar.save(f"{os.getcwd()}/me.png")
```
