try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os.path

setup(
    version = "0.1.1",
    name = "generic-transaction",
    author = "Jason Dixon",
    packages = ["generic_transaction"],
    author_email = "jason.dixon.email@gmail.com",
    long_description_content_type = "text/markdown",
    url = "https://github.com/internetimagery/generic-transaction",
    description = "The everymans' generic transaction framework. Have a look.",
    long_description = open(os.path.join(os.path.dirname(__file__), "README.md")).read())
