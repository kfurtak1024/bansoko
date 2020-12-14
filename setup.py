#!/usr/bin/env python
import os

from setuptools import setup, find_packages

import bansoko

setup(
    name="bansoko",
    version=bansoko.__version__,
    author="Krzysztof Furtak",
    author_email="contact@krzysztoffurtak.dev",
    url="https://github.com/kfurtak1024/bansoko",
    description="Bansoko is a reimagined, space-themed clone of MS-DOS Soko-Ban from 1984 created "
                "in Python using Pyxel",
    long_description=open(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md")
    ).read(),
    long_description_content_type="text/markdown",
    platforms="any",
    keywords="game puzzle sokoban 8-bit retro",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Games/Entertainment :: Puzzle Games"
    ],
    install_requires=["setuptools", "pyxel", "docopt", "jsonschema"],
    packages=find_packages(exclude=["resbuilder", "resbuilder.*"]),
    package_data={
        "bansoko": ["gamedata/main.pyxres", "gamedata/main.meta"]
    },
    entry_points={"console_scripts": ["bansoko = bansoko.__main__:main"]}
)
