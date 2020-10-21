import os

from setuptools import find_packages, setup


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md")) as f:
    readme = f.read()

setup_args = {
    "name": "chatdb",
    "version": "0.1.0",
    "description": "ChatDB is a toolkit to easily store chat messages in DB.",
    "long_description": readme,
    "long_description_content_type": "text/markdown",
    "license": "MIT License",
    "author": "Aki",
    "author_email": "a03ki04@gmail.com",
    "url": "https://github.com/A03ki/chatdb",
    "python_requires": ">=3.6, <3.9",
    "install_requires": ["py2neo"],
    "packages": find_packages(),
    "include_package_data": True,
    "classifiers": [
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    "keywords": "DB Neo4j NLP"
}

setup(**setup_args)
