"""Module exposing JSON schema for Bansoko's resources metadata file."""
from bansoko.game.screens.gui_consts import GuiSprite, GuiColor, GuiPosition

METADATA_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Bansoko resources metadata schema",
    "description": "Schema describing format of metadata for game resources",
    "type": "object",
    "definitions": {
        "resource_name": {
            "type": "string",
            "description": "Name of a game resource that can be referenced",
            "pattern": "^[A-Za-z_][A-Za-z0-9_]*$"
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
            "description": "A rectangle expressed as position and size",
            "items": {
                "type": "integer"
            },
            "minItems": 4,
            "maxItems": 4
        },
        "color": {
            "type": "integer",
            "description": "One of 16 available colors",
            "minimum": 0,
            "maximum": 15
        },
        "transparency_color": {
            "type": "integer",
            "description": "Transparency color is a color which is ignored during drawing."
                           "One of 16 available colors *OR* -1 for no transparency",
            "minimum": -1,
            "maximum": 15
        },
        "image_bank": {
            "type": "integer",
            "description": "The id of Pyxel's image bank",
            "minimum": 0,
            "maximum": 1
        },
        "tilemap_id": {
            "type": "integer",
            "description": "The id of Pyxel's tilemap",
            "minimum": 0,
            "maximum": 7
        },
    },
    "properties": {
        "sprites": {
            "description": "Collection of sprites that can be used in the game",
            "type": "object",
            "propertyNames": {
                "$ref": "#/definitions/resource_name"
            },
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "image_bank": {
                        "description": "Image bank the sprite is located in",
                        "$ref": "#/definitions/image_bank"
                    },
                    "directional": {
                        "description": "Is sprite directional. Directional sprites has variants "
                                       "for all 4 directions (Left, Right, Up and Down).",
                        "type": "boolean"
                    },
                    "transparency_color": {
                        "description": "Transparency color for the sprite",
                        "$ref": "#/definitions/transparency_color"
                    },
                    "num_frames": {
                        "description": "Number of animation frames in the sprite",
                        "type": "integer",
                        "minimum": 1
                    },
                    "num_layers": {
                        "description": "Number of layers of the sprite",
                        "type": "integer",
                        "minimum": 1
                    },
                    "uv_rect": {
                        "description": "The sprite coordinates in the image bank",
                        "$ref": "#/definitions/rect"
                    }
                },
                "required": ["image_bank", "directional", "transparency_color", "num_frames",
                             "num_layers", "uv_rect"]
            }
        },
        "sprite_packs": {
            "description": "Collection of sprite packs that can be used in the game",
            "type": "object",
            "propertyNames": {
                "$ref": "#/definitions/resource_name"
            },
            "additionalProperties": {
                "type": "array",
                "items": {
                    "$ref": "#/definitions/resource_name"
                },
                "minItems": 1
            }
        },
        "screens": {
            "description": "Collection of screens that can be used in the game",
            "type": "object",
            "propertyNames": {
                "$ref": "#/definitions/resource_name"
            },
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "background": {
                        "type": "object",
                        "description": "",
                        "properties": {
                            "background_color": {
                                "$ref": "#/definitions/color",
                                "description": "Background color screen is cleared with"
                            },
                            "background_tilemap": {
                                "type": "object",
                                "description": "Background tilemap drawn on the screen "
                                               "(it's drawn as first)",
                                "properties": {
                                    "tilemap_id": {
                                        "$ref": "#/definitions/tilemap_id",
                                        "description": "Pyxel's tilemap id for the background "
                                                       "tilemap"
                                    },
                                    "tilemap_uv": {
                                        "$ref": "#/definitions/rect",
                                        "description": "Rectangle representing a portion of "
                                                       "Pyxel's tilemap that is going to be drawn "
                                                       "on game screen"
                                    }
                                },
                                "required": ["tilemap_id", "tilemap_uv"]
                            }
                        },
                        "additionalProperties": False
                    },
                    "elements": {
                        "type": "array",
                        "description": "Collection of elements (images, texts) of the game screen",
                        "items": {
                            "type": "object",
                            "properties": {
                                "position": {
                                    "$ref": "#/definitions/point",
                                    "description": "Position of the element in screen space"
                                },
                                "sprite_ref": {
                                    "$ref": "#/definitions/resource_name",
                                    "description": "Sprite of the element, if element is sprite "
                                                   "based"
                                },
                                "text": {
                                    "type": "string",
                                    "description": "Text of the element, if element is text based"
                                }
                            },
                            "oneOf": [
                                {
                                    "required": ["position", "sprite_ref"]
                                },
                                {
                                    "required": ["position", "text"]
                                }
                            ]
                        }
                    },
                    "menu": {
                        "type": "object",
                        "description": "Configuration of the menu displayed on the game screen",
                        "properties": {
                            "position": {
                                "$ref": "#/definitions/point",
                                "description": "Position of the menu in screen space"
                            },
                            "scrollbar_rect": {
                                "$ref": "#/definitions/rect",
                                "description": "Rectangle describing the position and size of "
                                               "the menu scrollbar"
                            }
                        },
                        "additionalProperties": False
                    }
                }
            }
        },
        "gui_consts": {
            "description": "Collection of static, pre-defined GUI elements related configuration",
            "type": "object",
            "properties": {
                "positions": {
                    "description": "Collection of pre-defined GUI elements positions",
                    "type": "object",
                    "properties": {
                        position.resource_name: {
                            "$ref": "#/definitions/point"
                        } for position in list(GuiPosition)
                    },
                    "additionalProperties": False
                },
                "colors": {
                    "description": "Collection of pre-defined GUI elements colors",
                    "type": "object",
                    "properties": {
                        color.resource_name: {
                            "$ref": "#/definitions/color"
                        } for color in list(GuiColor)
                    },
                    "additionalProperties": False
                },
                "sprites": {
                    "description": "Collection of pre-defined GUI elements sprites",
                    "type": "object",
                    "properties": {
                        sprite.resource_name: {
                            "$ref": "#/definitions/resource_name"
                        } for sprite in list(GuiSprite)
                    },
                    "additionalProperties": False
                }
            },
            "additionalProperties": False,
            "required": ["positions", "colors", "sprites"]
        },
        "levels": {
            "type": "object",
            "properties": {
                "sha1": {
                    "type": "string",
                    "description": "SHA1 of the bundle metadata file describes. It's generated"
                                   "based on bundle name and levels.",
                    "pattern": "^[a-f0-9]{40}$"
                },
                "level_templates": {
                    "type": "array",
                    "description": "Collection of templates used when instantiating levels",
                    "items": {
                        "type": "object",
                        "properties": {
                            "tileset": {
                                "type": "integer",
                                "description": "The id of tileset level template uses",
                                "minimum": 0
                            },
                            "draw_offset": {
                                "$ref": "#/definitions/point",
                                "description": "The offset of the level's tilemap relative to "
                                               "screen"
                            },
                            "robot_sprite_pack_ref": {
                                "$ref": "#/definitions/resource_name",
                                "description": "Reference to sprite pack containing robot sprites"
                            },
                            "crate_sprite_pack_ref": {
                                "$ref": "#/definitions/resource_name",
                                "description": "Reference to sprite pack containing crate sprites"
                            }
                        }
                    }
                }
            }
        }
    },
    "additionalProperties": False
}
