try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os.path

setup(
    version = "0.0.0",
    name = "airbag",
    author = "Jason Dixon",
    packages = ["airbag"],
    author_email = "jason.dixon.email@gmail.com",
    long_description_content_type = "text/markdown",
    url = "https://github.com/internetimagery/airbag",
    description = "WIP",
    long_description = open(os.path.join(os.path.dirname(__file__), "README.md")).read())
