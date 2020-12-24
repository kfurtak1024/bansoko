<h1 align="center">
  <img src="https://github.com/kfurtak1024/bansoko/raw/master/docs/logo.png">
</h1>
<p align="center">
  <a href="https://github.com/kfurtak1024/bansoko/releases/latest">
    <img src="https://img.shields.io/github/v/release/kfurtak1024/bansoko">
  </a>
  <a>
    <img src="https://img.shields.io/github/pipenv/locked/python-version/kfurtak1024/bansoko">
  </a>
  <a href="https://pypi.org/project/bansoko/">
    <img src="https://img.shields.io/pypi/v/bansoko">
  </a>
  <a href="https://lgtm.com/projects/g/kfurtak1024/bansoko">
    <img src="https://img.shields.io/lgtm/grade/python/github/kfurtak1024/bansoko">
  </a>
  <a href="https://github.com/kfurtak1024/bansoko/workflows/CodeQL">
    <img src="https://github.com/kfurtak1024/bansoko/workflows/CodeQL/badge.svg">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg">
  </a>
</p>


**Bansoko** is a reimagined, space-themed clone of MS-DOS Soko-Ban from 1984 created in Python using [Pyxel](https://github.com/kitao/pyxel).

> *Welcome to Bansoko!*
> 
> *You are a scavenger. You collect cargos that people have left in abandoned ships in deep space.*
> *It's a dangerous job, that's why we're using robots.*
> 
> *Your goal is to use a remotely controlled robot to push all crates to cargo bays.*
> *Remember, you can only **push** them (you cannot **pull**)*
> *Fortunately, in case of mistake you can undo as many steps as you need.*
> 
> *Good luck!*

<p align="center">
  <img src="https://github.com/kfurtak1024/bansoko/raw/master/docs/screen_shot1.png">
  <img src="https://github.com/kfurtak1024/bansoko/raw/master/docs/screen_shot2.png">
  <img src="https://github.com/kfurtak1024/bansoko/raw/master/docs/screen_shot3.png">
</p>
<p align="center">
  <img src="https://github.com/kfurtak1024/bansoko/raw/master/docs/screen_shot4.png">
  <img src="https://github.com/kfurtak1024/bansoko/raw/master/docs/screen_shot5.png">
  <img src="https://github.com/kfurtak1024/bansoko/raw/master/docs/screen_shot6.png">
</p>

## Installation

#### Windows
Install [Python](python.org) (version 3.8 or higher) and make sure that python is added to PATH.

Install Bansoko by running:
```shell
pip install -U bansoko
```

Run the game:
```shell
bansoko
```

#### Linux
Install ```python3``` (version 3.8 or higher), ```python3-pip``` and required SDL2 libraries (```libsdl2-2.0-0``` and ```libsdl2-image-2.0-0```).

On Ubuntu, this can be done by running:

```shell
sudo apt install python3 python3-pip libsdl2-2.0-0 libsdl2-image-2.0-0 
```

Install Bansoko by running:
```shell
pip3 install -U bansoko
```
Run the game:
```shell
bansoko
```

## Development setup

### Install prerequisites

#### Windows
Install 32-bit [Python](python.org) (version 3.8 or higher) and make sure that python is added to PATH.

Additionally, install ```pipenv``` for managing virtual environments and project dependencies: 
```shell
pip install pipenv
```

#### Linux
Install ```python3``` (version 3.8 or higher), ```python3-pip```, ```pipenv``` and required SDL2 libraries (```libsdl2-2.0-0``` and ```libsdl2-image-2.0-0```).

On Ubuntu, this can be done by running:

```shell
sudo apt install python3 python3-pip pipenv libsdl2-2.0-0 libsdl2-image-2.0-0 
```

### Set up the project

Clone the repository:
```shell
git clone https://github.com/kfurtak1024/bansoko
```
Navigate to the directory Bansoko was cloned to.

Create virtual environment to isolate development:
```shell
pipenv shell
```

Install all dependencies needed for development:
```shell
pipenv install --dev
```

### Run the game

Run Bansoko from virtual environment created in the previous step:

#### Windows
```shell
python -m bansoko
```

#### Linux
```shell
python3 -m bansoko
```

## Modding
**Bansoko** is heavily modifiable thanks to included resource builder. More information on how to 'mod' it can be found on [Bansoko modding page](https://github.com/kfurtak1024/bansoko/wiki/Bansoko-modding).

## How to contribute

### Submitting an issue

Use the issue tracker to submit bug reports and feature/enhancement requests.
When submitting a report, please select the appropriate [template](https://github.com/kfurtak1024/bansoko/issues/new/choose).

### Submitting a 'mod'

If you have created a modification for Bansoko which you would like to publish then please contact me via <contact@krzysztoffurtak.dev>

## License
This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/kfurtak1024/bansoko/blob/master/LICENSE) file for details.
