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
from typing import NamedTuple, Dict, Any

import pyxel
from docopt import docopt
from jsonschema import validate

from resbuilder.resources.backgrounds import process_backgrounds
from resbuilder.resources.level_themes import generate_level_themes
from resbuilder.resources.levels import process_levels
from resbuilder.resources.skin_packs import process_skin_packs
from resbuilder.resources.sprites import process_sprites
from resbuilder.resources.tilemap_generators import process_tilemap_generators
from resbuilder.resources.tiles import TilePacker
from resources.json_schema import RESOURCES_JSON_SCHEMA


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
    input_dir: Path
    resource_filename: str
    metadata_filename: str


def generate_file_names(input_filename: str, out_dir: str) -> FileNames:
    source_file_path = Path(input_filename).resolve()
    source_dir = source_file_path.parent
    base_name = source_file_path.stem
    resource_file_path = Path(out_dir).joinpath(base_name + ".pyxres").resolve()
    metadata_file_path = Path(out_dir).joinpath(base_name + ".meta").resolve()
    return FileNames(str(source_file_path), source_dir, str(resource_file_path),
                     str(metadata_file_path))


def create_metadata(input_dir: Path, input_data: Any) -> Dict[str, Any]:
    metadata = {}

    logging.info("Processing sprites...")
    sprites = process_sprites(input_dir, input_data["sprites"])
    metadata["sprites"] = sprites
    logging.info("Processing skins...")
    skin_packs = process_skin_packs(input_data["skin_packs"], sprites)
    metadata["skin_packs"] = skin_packs
    tile_packer = TilePacker(0, input_dir)
    logging.info("Generating level themes...")
    level_themes = generate_level_themes(input_data["level_themes"], tile_packer, skin_packs)
    logging.info("Processing tilemap generators...")
    generators = process_tilemap_generators(input_data["tilemap_generators"], tile_packer)
    logging.info("Processing backgrounds...")
    metadata["backgrounds"] = process_backgrounds(input_data["backgrounds"], sprites, generators)
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
    except Exception as error:
        logging.exception(error)


if __name__ == "__main__":
    main()
