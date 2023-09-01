import os

from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    install_requires = f.read().splitlines()

g = {}
with open(os.path.join("pyavatar", "_version.py"), "rt") as f:
    exec(f.read(), g)
    version = g["__version__"]

setup(name="pyavatar",
      version=version,
      author="Matthieu Petiteau",
      author_email="mpetiteau.pro@gmail.com",
      keywords="avatar",
      license="MIT",
      description="Generate simple user avatars from an input string.",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/smallwat3r/pyavatar",
      include_package_data=True,
      packages=find_packages(),
      install_requires=install_requires,
      classifiers=[
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      python_requires=">=3.10")
