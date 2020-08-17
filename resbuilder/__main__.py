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

from processors.background_processor import process_backgrounds
from processors.level_processor import process_levels
from processors.level_theme_processor import generate_level_themes
from processors.sprite_processor import process_sprites


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
        input_data = json.load(input_file)
        metadata = {}
        level_themes = generate_level_themes(files.input_dir, input_data["level_themes"])
        logging.info(f"Processing levels...")
        metadata["levels"] = process_levels(input_data["levels"], level_themes)
        logging.info(f"Processing sprites...")
        metadata["sprites"] = process_sprites(input_data["sprites"])
        logging.info(f"Processing backgrounds...")
        metadata["backgrounds"] = process_backgrounds(input_data["backgrounds"])
        logging.info(f"Writing resource file '{files.resource_file}'...")
        pyxel.save(files.resource_file)
        logging.info(f"Writing meta data file '{files.metadata_file}'...")
        json.dump(metadata, metadata_file, indent=2)
