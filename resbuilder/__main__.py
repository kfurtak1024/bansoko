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
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

import pyxel
from docopt import docopt
from jsonschema import validate

from bansoko import TILESET_IMAGE_BANK
from resbuilder import ResourceError
from resbuilder.resources.background_tilemaps import process_tilemap_generators, \
    process_window_tilesets
from resbuilder.resources.screens import process_screens
from resbuilder.resources.json_schema import RESOURCES_JSON_SCHEMA
from resbuilder.resources.level_themes import generate_level_themes
from resbuilder.resources.levels import process_levels
from resbuilder.resources.sprite_packs import process_sprite_packs
from resbuilder.resources.sprites import process_sprites
from resbuilder.resources.tiles import TilePacker


def configure_logger(verbose: bool) -> None:
    """Sets up a logger for Resource Builder according to value of verbose flag."""
    logging.basicConfig(
        format="%(levelname)s%(message)s",
        level=logging.INFO if verbose else logging.WARN)
    logging.addLevelName(logging.ERROR, "** ERROR: ")
    logging.addLevelName(logging.WARN, "WARN: ")
    logging.addLevelName(logging.INFO, "")


@dataclass(frozen=True)
class FileNames:
    """Container for directories and file names used by Resource Builder."""
    input_filename: str
    input_dir: Path
    resource_filename: str
    metadata_filename: str


def generate_file_names(input_filename: str, out_dir: str) -> FileNames:
    """Generate all file paths used by resbuilder basing on input file name and output directory.

    :param input_filename: file name of the resources input file
    :param out_dir: destination directory (all generated artifacts will be put there)
    :return: instance of FileNames
    """
    source_file_path = Path(input_filename).resolve()
    source_dir = source_file_path.parent
    base_name = source_file_path.stem
    resource_file_path = Path(out_dir).joinpath(base_name + ".pyxres").resolve()
    metadata_file_path = Path(out_dir).joinpath(base_name + ".meta").resolve()
    return FileNames(str(source_file_path), source_dir, str(resource_file_path),
                     str(metadata_file_path))


def create_metadata(input_dir: Path, input_data: Any) -> Dict[str, Any]:
    """Crate resources metadata file along with Pyxel's resource file.

    :param input_dir: input directory where all resource files are located in
    :param input_data: resource input data file (parsed from JSON file)
    :return: resources metadata (ready to be serialized to JSON)
    """
    metadata = {}

    logging.info("Processing sprites...")
    sprites = process_sprites(input_data["sprites"], input_dir)
    metadata["sprites"] = sprites
    logging.info("Processing sprite packs...")
    sprite_packs = process_sprite_packs(input_data["sprite_packs"], sprites)
    metadata["sprite_packs"] = sprite_packs
    tile_packer = TilePacker(TILESET_IMAGE_BANK, input_dir)
    logging.info("Generating level themes...")
    level_themes = generate_level_themes(input_data["level_themes"], tile_packer, sprite_packs)
    logging.info("Processing tilemap generators...")
    generators = process_tilemap_generators(input_data["tilemap_generators"], tile_packer)
    logging.info("Processing window tilesets...")
    window_tilesets = process_window_tilesets(input_data["window_tilesets"], tile_packer)
    logging.info("Processing screens...")
    metadata["screens"] = process_screens(
        input_data["screens"], sprites, generators, window_tilesets)
    logging.info("Processing levels...")
    metadata["levels"] = process_levels(input_data["levels"], level_themes, generators)

    return metadata


def main() -> None:
    """Main entry point."""
    arguments = docopt(__doc__, version="0.1")
    files = generate_file_names(arguments["<file>"], arguments["--outdir"])
    configure_logger(arguments["--verbose"])

    # TODO: --force command line argument is not used!

    logging.info("Processing file '%s'...", files.input_filename)
    try:
        with open(files.input_filename) as input_file,\
             open(files.metadata_filename, "w") as metadata_file:
            pyxel.init(256, 256)
            input_data = json.load(input_file)
            validate(input_data, RESOURCES_JSON_SCHEMA)
            metadata = create_metadata(files.input_dir, input_data)
            logging.info("Writing resource file '%s'...", files.resource_filename)
            pyxel.save(files.resource_filename)
            logging.info("Writing metadata file '%s'...", files.metadata_filename)
            json.dump(metadata, metadata_file, indent=2)
    except ResourceError as error:
        logging.exception(error)


if __name__ == "__main__":
    main()
