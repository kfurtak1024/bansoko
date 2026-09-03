<h1 align="center">
  <img src="https://github.com/kfurtak1024/bansoko/raw/master/docs/images/logo.png">
</h1>
<p align="center">
  <a href="https://github.com/kfurtak1024/bansoko/releases/latest">
    <img src="https://img.shields.io/github/v/release/kfurtak1024/bansoko"/></a>
  <a href="https://github.com/kfurtak1024/bansoko/blob/master/pyproject.toml">
    <img src="https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fkfurtak1024%2Fbansoko%2Fmaster%2Fpyproject.toml"></a>
  <a href="https://pypi.org/project/bansoko/">
    <img src="https://img.shields.io/pypi/v/bansoko"></a>
  <a href="https://github.com/kfurtak1024/bansoko/actions/workflows/ci.yml">
    <img src="https://github.com/kfurtak1024/bansoko/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/kfurtak1024/bansoko/actions/workflows/codeql-analysis.yml">
    <img src="https://github.com/kfurtak1024/bansoko/actions/workflows/codeql-analysis.yml/badge.svg"></a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/github/license/kfurtak1024/bansoko"/></a>
  <a href="https://kfurtak1024.itch.io/bansoko">
    <img src="https://img.shields.io/badge/itch.io-download-black?logo=itchdotio&color=FA5C5C"></a>
</p>

**Bansoko** is a reimagined, space-themed 🚀 clone of MS-DOS Soko-Ban from 1984 created in Python using [Pyxel](https://github.com/kitao/pyxel).

You can download :package: for both Windows and Linux from the
[latest release](https://github.com/kfurtak1024/bansoko/releases/latest), or from:

<a href="https://kfurtak1024.itch.io/bansoko">
  <img src="https://static.itch.io/images/badge-color.svg" height="42">
</a>

## 📖 Introduction

>
> *Welcome to Bansoko!*
> 
> *You are a scavenger. You collect cargo that people have left in abandoned ships in deep space.*
> *It's a dangerous job, that's why we're using robots.*
> 
> *Your goal is to use a remotely controlled robot to push all crates to cargo bays.*
> *Remember, you can only **push** them (you cannot **pull**)*
> *Fortunately, in case of a mistake, you can undo as many steps as you need.*
> 
> *Good luck!*

<p align="center">
  <img src="https://github.com/kfurtak1024/bansoko/raw/master/docs/images/screen_shot1.png">
  <img src="https://github.com/kfurtak1024/bansoko/raw/master/docs/images/screen_shot2.png">
  <img src="https://github.com/kfurtak1024/bansoko/raw/master/docs/images/screen_shot3.png">
</p>
<p align="center">
  <img src="https://github.com/kfurtak1024/bansoko/raw/master/docs/images/screen_shot4.png">
  <img src="https://github.com/kfurtak1024/bansoko/raw/master/docs/images/screen_shot5.png">
  <img src="https://github.com/kfurtak1024/bansoko/raw/master/docs/images/screen_shot6.png">
</p>

## 🎮 Installation

### Download

The simplest way to play is to download a standalone build from the
[latest release](https://github.com/kfurtak1024/bansoko/releases/latest) or
from [itch.io](https://kfurtak1024.itch.io/bansoko). Nothing else is needed:
Python and every library the game uses are bundled.

### Windows
Install [Python](https://www.python.org) (version 3.11 or higher) and make sure that python is added to PATH.

Install Bansoko by running:
```shell
pip install -U bansoko
```

Run the game:
```shell
bansoko
```

### Linux
Install ```python3``` (version 3.11 or higher). No SDL2 packages are
required — Pyxel ships its own copy.

On Ubuntu:

```shell
sudo apt install python3 pipx
```

Install Bansoko by running:
```shell
pipx install bansoko
```

Run the game:
```shell
bansoko
```

## 💻 Development setup

### 1. Install prerequisites

[uv](https://docs.astral.sh/uv/) is the only prerequisite. It installs a
suitable Python itself, so one does not need to be present.

#### Windows
```shell
pip install uv
```

#### Linux
On Ubuntu:
```shell
sudo apt install git pipx
pipx install uv
```

### 2. Set up the project

Clone the repository:
```shell
git clone https://github.com/kfurtak1024/bansoko
```
Navigate to the directory Bansoko was cloned to.

Create the virtual environment and install all dependencies needed for
development:
```shell
uv sync
```

### 3. Run the game

Run Bansoko from the virtual environment created in the previous step:
```shell
uv run python -m bansoko
```

### 4. Run the checks

```shell
uv run pytest
uv run pylint bansoko resbuilder tests
uv run mypy bansoko resbuilder tests
```

Tests that need a display are skipped automatically when there is none. To
run them without a desktop session:
```shell
xvfb-run -a uv run pytest
```

### 5. Build a standalone binary

```shell
uv run pyinstaller bansoko.spec --noconfirm
```
This produces a single executable in ```dist/```. Release downloads are built
by the release workflow, which builds the Linux one inside a
```manylinux_2_28``` container so that it runs on older distributions too.

## 🧰 Modding
**Bansoko** is heavily modifiable thanks to included resource builder.
More information on how to 'mod' it can be found on the
[Bansoko modding page](https://github.com/kfurtak1024/bansoko/wiki/Bansoko-modding).

After changing anything under ```resources/```, rebuild the game data:
```shell
uv run python -m resbuilder resources/main.ressrc --outdir bansoko/gamedata --force
```
The generated files are checked in, and the test suite fails if they do not
match the assets they were built from.

## 📝 Changelog

Notable changes for each release are listed in
[CHANGELOG.md](https://github.com/kfurtak1024/bansoko/blob/master/CHANGELOG.md).

## 🤝 How to contribute

### Submitting an issue

Use the issue tracker to submit bug reports and feature/enhancement requests.
When submitting a report, please select the appropriate [template](https://github.com/kfurtak1024/bansoko/issues/new/choose).

### Submitting a 'mod'

If you have created a modification for Bansoko which you would like to publish then please contact me via <contact@krzysztoffurtak.dev>

## ⚖️ License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/kfurtak1024/bansoko/blob/master/LICENSE) file for details.

Copyright © 2020-2026 Krzysztof Furtak
