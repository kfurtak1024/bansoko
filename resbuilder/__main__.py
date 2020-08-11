"""Resource builder for Bansoko.

Usage:
    resbuilder [-hvf] [--version] <file> [--outdir <dir>]

Options:
    -h, --help                  Show this screen.
    --version                   Show version.
    -v, --verbose               Turn on verbose mode.
    -f, --force                 Force overwrite files.
    -o <dir>, --outdir <dir>    Specify output directory [default: ./]
"""
import json
import logging
from pathlib import Path
from typing import NamedTuple

import pyxel
from docopt import docopt

from resources_processor import generate_levels, generate_level_themes


def configure_logger(verbose: bool):
    logging.basicConfig(
        format="%(levelname)s%(message)s",
        level=logging.INFO if verbose else logging.WARN)
    logging.addLevelName(logging.ERROR, "** ERROR: ")
    logging.addLevelName(logging.WARN, "WARN: ")
    logging.addLevelName(logging.INFO, "")


class FileNames(NamedTuple):
    input_file: str
    input_dir: str
    resource_file: str
    metadata_file: str


def generate_file_names(input_file: str, out_dir: str) -> FileNames:
    source_file = Path(input_file).resolve()
    source_dir = Path(source_file).parent
    base_name = Path(source_file).stem
    resource_file = Path(out_dir).joinpath(base_name + ".pyxres").resolve()
    resource_meta_file = Path(out_dir).joinpath(base_name + ".meta").resolve()
    return FileNames(source_file, source_dir, resource_file, resource_meta_file)


if __name__ == "__main__":
    arguments = docopt(__doc__, version="0.1")
    files = generate_file_names(arguments["<file>"], arguments["--outdir"])
    configure_logger(arguments["--verbose"])

    logging.info(f"Processing file '{files.input_file}'...")
    with open(files.input_file) as input_file, open(files.metadata_file, "w") as metadata_file:
        pyxel.init(256, 256)
        data = json.load(input_file)
        level_themes = generate_level_themes(data["level_themes"], files.input_dir)
        generate_levels(data["levels"], data["level_legend"], level_themes)
        logging.info(f"Writing resource file '{files.resource_file}'...")
        pyxel.save(files.resource_file)
        logging.info(f"Writing meta data file '{files.metadata_file}'...")
        json.dump({}, metadata_file)
