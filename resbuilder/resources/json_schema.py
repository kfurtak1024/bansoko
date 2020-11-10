"""Module exposing JSON schema for Bansoko's game resources."""
from resbuilder.resources.tiles import Tile

# TODO: Rename *_name to *_ref
# TODO: Review this schema!

RESOURCES_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Bansoko game resources",
    "description": "Bansoko pre-processed game resources",
    "type": "object",
    "definitions": {
        "file_path": {
            "description": "Path to a resource file.",
            "type": "string"
        },
        "color": {
            "type": "string",
            "description": "One of 16 available colors. A single character with HEX value (0..F)",
            "pattern": "^([A-Fa-f0-9]{1})$"
        },
        "position": {
            "type": "array",
            "description": "A point representing a location in (x, y) screen space.",
            "items": {
                "type": "integer"
            },
            "minItems": 2,
            "maxItems": 2
        }
    },
    "properties": {
        "sprites": {
            "description": "Collection of all sprites that are going to be packed in image bank.",
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "image_bank": {
                        "description": "Image bank the sprite should be packed to.",
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 2
                    },
                    "image": {
                        "description": "Path to the PNG file representing the sprite.",
                        "type": "string"
                    },
                    "num_frames": {
                        "description": "Number of animation frames in the sprite.",
                        "type": "integer",
                        "minimum": 1
                    },
                    "multilayer": {
                        "description": "Is sprite multilayered. Multilayered sprites can be drawn "
                                       "as pseudo 3D objects.",
                        "type": "boolean"
                    },
                    "directional": {
                        "description": "Is sprite directional. Directional sprites has variants "
                                       "for all 4 directions (Left, Right, Up and Down).",
                        "type": "boolean"
                    },
                    "transparent": {
                        "description": "Is sprite transparent. Transparent sprites are drawn with "
                                       "transparency color 0. (pixels with color 0 are not drawn)",
                        "type": "boolean"
                    }
                },
                "required": ["image_bank", "image"]
            }
        },
        "backgrounds": {
            "description": "Collection of backgrounds for game screens.",
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "background_color": {
                        "description": "The color the background is cleared with.",
                        "$ref": "#/definitions/color"
                    },
                    "background_tilemap": {
                        "description": "The tilemap the background is drawn with.",
                        "type": "object",
                        "properties": {
                            "tilemap_generator": {
                                "description": "Generator the tilemap will be generated with.",
                                "type": "object",
                                "properties": {
                                    "generator_name": {
                                        "description": "Reference to tilemap generator.",
                                        "type": "string"
                                    },
                                    "seed": {
                                        "description": "Seed used during tilemap generation.",
                                        "type": "integer",
                                        "minimum": 0
                                    }
                                },
                                "required": ["generator_name"]
                            }
                        },
                    },
                    "elements": {
                        "description": "Collection of drawable, backgrounds elements.",
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "sprite": {
                                    "description": "Reference to sprite representing the "
                                                   "background element.",
                                    "type": "string"
                                },
                                "position": {
                                    "description": "The position of background element.",
                                    "$ref": "#/definitions/position"
                                }
                            },
                            "required": ["sprite", "position"]
                        }
                    }
                }
            }
        },
        "levels": {
            "description": "Collection of levels.",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "seed": {
                        "description": "The seed used for the generation of background tilemap.",
                        "type": "integer",
                        "minimum": 0
                    },
                    "data": {
                        "description": "Level in text (human readable) format.",
                        "type": "array",
                        "items": {
                            "type": "string",
                            # TODO: Add regex for tiles
                            "minLength": 1,
                            "maxLength": 32
                        },
                        "minItems": 1,
                        "maxItems": 32
                    }
                },
                "required": ["data"]
            },
            "minItems": 1
        },
        "tilemap_generators": {
            "description": "Collection of tilemap generators.",
            "type": "object",
            "additionalProperties": {
                "description": "Collection of tile to possibility mappings.",
                "type": "object",
                "additionalProperties": {
                    "description": "Relative weight (possibility) of the tile.",
                    "type": "integer",
                    "minimum": 0
                }
            }
        },
        "level_themes": {
            "description": "Collection of level themes.",
            "type": "array",
            "items": {
                "description": "Theme controlling the look&feel of the level.",
                "type": "object",
                "properties": {
                    "background_generator": {
                        "description": "Reference to generator the background tilemap will be "
                                       "generated with.",
                        "type": "string"
                    },
                    "tiles": {
                        "type": "object",
                        "properties": {
                            "layers": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        tile.tile_name: {
                                            "$ref": "#/definitions/file_path"
                                        } for tile in list(Tile)
                                    }
                                },
                                "minItems": 1
                            }
                        }

                    },
                    "sprite_packs": {
                        "description": "Collection of sprite packs.",
                        "type": "object",
                        "properties": {
                            "robot": {
                                "type": "string"
                            },
                            "crate": {
                                "type": "string"
                            }
                        },
                        "additionalProperties": {
                            "type": "string"
                        },
                        "required": ["robot", "crate"]
                    },
                    "thumbnail_colors": {
                        "description": "Colors for all tile types used in level thumbnails.",
                        "type": "object",
                        "properties": {
                            tile.tile_name: {
                                "$ref": "#/definitions/color"
                            } for tile in list(Tile)
                        },
                        "required": [tile.tile_name for tile in list(Tile)]
                    }
                },
                "required": ["tiles", "sprite_packs", "thumbnail_colors"]
            },
            "minItems": 1
        }
    }
}
