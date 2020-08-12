#!/usr/bin/env python
import os

from setuptools import setup, find_packages

from bansoko import VERSION

setup(
    name="bansoko",
    version=VERSION,
    author="Krzysztof Furtak",
    author_email="contact@krzysztoffurtak.dev",
    description="Space-themed Sokoban clone created in Python using Pyxel.",
    long_description=open(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md")
    ).read(),
    long_description_content_type="text/markdown",
    platforms="any",
    keywords="pyxel games",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Games/Entertainment :: Puzzle Games"
    ],
    install_requires=["setuptools", "pyxel"],
    packages=find_packages(exclude=["resbuilder"]),
    package_data={
        "bansoko": ["gamedata/main.pyxres", "gamedata/main.meta"]
    },
    entry_points={"console_scripts": ["bansoko = bansoko.__main__:main"]}
)
