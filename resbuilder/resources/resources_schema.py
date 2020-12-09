"""Module exposing JSON schema for Bansoko's game resources."""
from bansoko import LEVEL_WIDTH, LEVEL_HEIGHT
from resbuilder.resources.backgrounds import FrameSlice
from resbuilder.resources.tiles import Tile

RESOURCES_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Bansoko game resources",
    "description": "Bansoko pre-processed game resources",
    "type": "object",
    "definitions": {
        "resource_name": {
            "type": "string",
            "description": "Name of a game resource that can be referenced",
            "pattern": "^[A-Za-z_][A-Za-z0-9_]*$"
        },
        "file_path": {
            "description": "Path to a resource file",
            "type": "string"
        },
        "point": {
            "type": "array",
            "description": "A point representing a location on screen",
            "items": {
                "type": "integer"
            },
            "minItems": 2,
            "maxItems": 2
        },
        "rect": {
            "type": "array",
            "description": "A rectangle in screen space",
            "items": {
                "type": "integer"
            },
            "minItems": 4,
            "maxItems": 4
        },
        "color": {
            "type": "string",
            "description": "One of 16 available colors. A single character with HEX value [0..F]",
            "pattern": "^([A-Fa-f0-9]{1})$"
        },
        "tile": {
            "type": "string",
            "description": "",
            "pattern": "^([ X@\\.#&\\+]*)$"
        },
        "image_bank": {
            "type": "integer",
            "description": "The id of Pyxel's image bank",
            "minimum": 0,
            "maximum": 1
        }
    },
    "properties": {
        "sprites": {
            "description": "Collection of all sprites that are going to be packed in image bank",
            "type": "object",
            "propertyNames": {
                "$ref": "#/definitions/resource_name"
            },
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "image_bank": {
                        "description": "Image bank the sprite should be packed to",
                        "$ref": "#/definitions/image_bank"
                    },
                    "image": {
                        "description": "Path to the PNG file representing the sprite",
                        "$ref": "#/definitions/file_path"
                    },
                    "num_frames": {
                        "description": "Number of animation frames in the sprite",
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
                    "transparency_color": {
                        "description": "Transparency color of sprite",
                        "$ref": "#/definitions/color"
                    }
                },
                "required": ["image_bank", "image"]
            }
        },
        "sprite_packs": {
            "description": "Collection of sprite packs that can be used in level themes.",
            "type": "object",
            "propertyNames": {
                "$ref": "#/definitions/resource_name"
            },
            "additionalProperties": {
                "type": "array",
                "items": {
                    "description": "Reference to sprite representing the "
                                   "screen element",
                    "$ref": "#/definitions/resource_name"
                },
                "minItems": 1
            }
        },
        "frame_tilesets": {
            "description": "Collection of nine slicing, tile based frames.",
            "type": "object",
            "propertyNames": {
                "$ref": "#/definitions/resource_name"
            },
            "additionalProperties": {
                "type": "object",
                "properties": {
                    frame_slice.value: {
                        "$ref": "#/definitions/file_path"
                    } for frame_slice in list(FrameSlice)
                },
                "additionalProperties": False
            }
        },
        "screens": {
            "description": "Collection of game screens",
            "type": "object",
            "propertyNames": {
                "$ref": "#/definitions/resource_name"
            },
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "background": {
                        "description": "Screen background",
                        "type": "object",
                        "properties": {
                            "background_color": {
                                "description": "The color the background is cleared with",
                                "$ref": "#/definitions/color"
                            },
                            "tilemap_generator": {
                                "description": "Generator the tilemap will be generated with",
                                "type": "object",
                                "properties": {
                                    "generator_ref": {
                                        "description": "Reference to tilemap generator",
                                        "$ref": "#/definitions/resource_name"
                                    },
                                    "seed": {
                                        "description": "Seed used during tilemap generation",
                                        "type": "integer",
                                        "minimum": 0
                                    }
                                },
                                "additionalProperties": False,
                                "required": ["generator_ref"]
                            },
                            "frames": {
                                "description": "Collection of drawable, background frames",
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "tileset_ref": {
                                            "description": "",
                                            "$ref": "#/definitions/resource_name"
                                        },
                                        "rect": {
                                            "description": "",
                                            "$ref": "#/definitions/rect"
                                        }
                                    },
                                    "additionalProperties": False,
                                    "required": ["tileset_ref", "rect"]
                                }
                            }
                        },
                        "additionalProperties": False
                    },
                    "elements": {
                        "description": "Collection of drawable, screen elements",
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "sprite_ref": {
                                    "description": "Reference to sprite representing the "
                                                   "screen element",
                                    "$ref": "#/definitions/resource_name"
                                },
                                "text": {
                                    "description": "Text to be displayed as screen element",
                                    "type": "string"
                                },
                                "position": {
                                    "description": "The position of screen element",
                                    "$ref": "#/definitions/point"
                                }
                            },
                            "oneOf": [
                                {
                                    "required": ["position", "sprite_ref"]
                                },
                                {
                                    "required": ["position", "text"]
                                }
                            ],
                            "additionalProperties": False
                        }
                    },
                    "menu": {
                        "description": "Configuration of screen menu",
                        "type": "object",
                        "properties": {
                            "position": {
                                "description": "The position of menu on the screen",
                                "$ref": "#/definitions/point"
                            },
                            "scrollbar_rect": {
                                "description": "The rectangle describing optional menu scrollbar",
                                "$ref": "#/definitions/rect"
                            }
                        },
                        "additionalProperties": False
                    }
                },
                "additionalProperties": False
            }
        },
        "levels": {
            "description": "Collection of levels",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "seed": {
                        "description": "The seed used for the generation of background tilemap",
                        "type": "integer",
                        "minimum": 0
                    },
                    "data": {
                        "description": "Level in text (human readable) format",
                        "type": "array",
                        "items": {
                            "$ref": "#/definitions/tile",
                            "minLength": 1,
                            "maxLength": LEVEL_WIDTH
                        },
                        "minItems": 1,
                        "maxItems": LEVEL_HEIGHT
                    }
                },
                "additionalProperties": False,
                "required": ["data"]
            },
            "minItems": 1
        },
        "tilemap_generators": {
            "description": "Collection of tilemap generators",
            "type": "object",
            "propertyNames": {
                "$ref": "#/definitions/resource_name"
            },
            "additionalProperties": {
                "description": "Collection of tile to possibility mappings",
                "type": "object",
                "propertyNames": {
                    "$ref": "#/definitions/file_path"
                },
                "additionalProperties": {
                    "description": "Relative weight (possibility) of the tile",
                    "type": "integer",
                    "minimum": 0
                }
            }
        },
        "level_themes": {
            "description": "Collection of level themes",
            "type": "array",
            "items": {
                "description": "Theme controlling the look&feel of the level",
                "type": "object",
                "properties": {
                    "background_generator_ref": {
                        "description": "Reference to generator the background tilemap will be "
                                       "generated with",
                        "$ref": "#/definitions/resource_name"
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
                                    },
                                    "additionalProperties": False
                                },
                                "minItems": 1
                            }
                        },
                        "additionalProperties": False
                    },
                    "tilemap_offset": {
                        "description": "Draw offset of the level's tilemap.",
                        "$ref": "#/definitions/point"
                    },
                    "sprite_packs": {
                        "description": "Collection of sprite packs",
                        "type": "object",
                        "propertyNames": {
                            "$ref": "#/definitions/resource_name"
                        },
                        "properties": {
                            "robot_pack_ref": {
                                "$ref": "#/definitions/resource_name"
                            },
                            "crate_pack_ref": {
                                "$ref": "#/definitions/resource_name"
                            }
                        },
                        "additionalProperties": False,
                        "required": ["robot_pack_ref", "crate_pack_ref"]
                    },
                    "thumbnail_colors": {
                        "description": "Colors for all tile types used in level thumbnails",
                        "type": "object",
                        "properties": {
                            tile.tile_name: {
                                "$ref": "#/definitions/color"
                            } for tile in list(Tile)
                        },
                        "additionalProperties": False,
                        "required": [tile.tile_name for tile in list(Tile)]
                    }
                },
                "additionalProperties": False,
                "required": ["tiles", "sprite_packs", "thumbnail_colors"]
            },
            "minItems": 1
        }
    },
    "additionalProperties": False
}
