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

from processors.skin_pack_processor import process_skins
from resbuilder.processors.background_processor import process_backgrounds
from resbuilder.processors.level_processor import process_levels
from resbuilder.processors.level_theme_processor import generate_level_themes
from resbuilder.processors.sprite_processor import process_sprites


def configure_logger(verbose: bool) -> None:
    """Sets up a logger for Resource Builder according to value of verbose flag."""
    logging.basicConfig(
        format="%(levelname)s%(message)s",
        level=logging.INFO if verbose else logging.WARN)
    logging.addLevelName(logging.ERROR, "** ERROR: ")
    logging.addLevelName(logging.WARN, "WARN: ")
    logging.addLevelName(logging.INFO, "")


class FileNames(NamedTuple):
    """Container for directories and file names used by Resource Builder."""

    input_filename: str
    input_dir: str
    resource_filename: str
    metadata_filename: str


def generate_file_names(input_filename: str, out_dir: str) -> FileNames:
    source_file_path = Path(input_filename).resolve()
    source_dir = source_file_path.parent
    base_name = source_file_path.stem
    resource_file_path = Path(out_dir).joinpath(base_name + ".pyxres").resolve()
    metadata_file_path = Path(out_dir).joinpath(base_name + ".meta").resolve()
    return FileNames(str(source_file_path), str(source_dir), str(resource_file_path),
                     str(metadata_file_path))


if __name__ == "__main__":
    arguments = docopt(__doc__, version="0.1")
    files = generate_file_names(arguments["<file>"], arguments["--outdir"])
    configure_logger(arguments["--verbose"])

    logging.info("Processing file '%s'...", files.input_filename)
    with open(files.input_filename) as input_file,\
         open(files.metadata_filename, "w") as metadata_file:
        pyxel.init(256, 256)
        input_data = json.load(input_file)
        metadata = {}
        logging.info("Generating level themes...")
        level_themes = generate_level_themes(files.input_dir, input_data["level_themes"])
        logging.info("Processing levels...")
        metadata["levels"] = process_levels(input_data["levels"], level_themes)
        logging.info("Processing sprites...")
        metadata["sprites"] = process_sprites(files.input_dir, input_data["sprites"])
        logging.info("Processing backgrounds...")
        metadata["backgrounds"] = process_backgrounds(input_data["backgrounds"])
        logging.info("Processing skins...")
        metadata["skin_packs"] = process_skins(input_data["skin_packs"])
        logging.info("Writing resource file '%s'...", files.resource_filename)
        pyxel.save(files.resource_filename)
        logging.info("Writing metadata file '%s'...", files.metadata_filename)
        json.dump(metadata, metadata_file, indent=2)
