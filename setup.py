import docoracle
import pathlib

from setuptools import setup

LOCAL = pathlib.Path(__file__).parent
README = (LOCAL / "README.md").read_text()

try:
    requirements = open("requirements.txt", "r").readlines()
except FileNotFoundError:
    requirements = []

try:
    dev_requirements = open("dev_requirements.txt", "r").readlines()
except FileNotFoundError:
    dev_requirements = []


setup(
    name=docoracle.__name__,
    version=docoracle.__version__,
    description=docoracle.__description__,
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/lissahyacinth/docoracle",
    license="MIT",
    packages=["docoracle"],
    requirements=requirements,
    extras_require={"dev": dev_requirements},
)
