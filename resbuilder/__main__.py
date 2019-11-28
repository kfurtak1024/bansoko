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

from resources_processor import generate_levels, generate_tileset


def configure_logger(verbose: bool):
    logging.basicConfig(
        format="%(levelname)s%(message)s",
        level=logging.INFO if verbose else logging.WARN)
    logging.addLevelName(logging.ERROR, "** ERROR: ")
    logging.addLevelName(logging.WARN, "WARN: ")
    logging.addLevelName(logging.INFO, "")


class FileNames(NamedTuple):
    source_file: str
    source_dir: str
    resource_file: str
    resource_meta_file: str


def generate_file_names(input_file: str, out_dir: str) -> FileNames:
    source_file = Path(input_file).resolve()
    source_dir = Path(source_file).parent
    base_name = Path(source_file).stem
    resource_file = Path(out_dir).joinpath(base_name + ".pyxres").resolve()
    resource_meta_file = Path(out_dir).joinpath(base_name + ".res").resolve()
    return FileNames(source_file, source_dir, resource_file, resource_meta_file)


if __name__ == "__main__":
    arguments = docopt(__doc__, version="0.1")
    files = generate_file_names(arguments["<file>"], arguments["--outdir"])
    configure_logger(arguments["--verbose"])

    logging.info(f"Processing file '{files.source_file}'...")
    with open(files.source_file) as json_file:
        pyxel.init(256, 256)
        data = json.load(json_file)
        generate_levels(data["levels"], data["level_legend"], data["level_thumbnail"])
        generate_tileset(data["level_tile_set"], files.source_dir)
        logging.info(f"Writing resource file '{files.resource_file}'...")
        pyxel.save(files.resource_file)
