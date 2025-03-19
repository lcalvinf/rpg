import pytmx

from settings import *
from sprites import Entity, Wall, Player

class Layout:
    def __init__(self, filepath):
        import sys
        from pathlib import Path
        dir = Path(sys.argv[0]).parent
        self.filepath = Path.joinpath(dir, filepath)
    def load(self):
        global FULL_WIDTH, FULL_HEIGHT
        self.tilemap = pytmx.util_pygame.load_pygame(self.filepath)
        self.width = self.tilemap.width
        self.height = self.tilemap.height
        self.full_width = self.width*TILE_W
        self.full_height = self.height*TILE_H
    def tiles(self):
        tiles = []
        visible_layers = list(self.tilemap.visible_layers)
        for i, layer in enumerate(visible_layers):
            if isinstance(layer, pytmx.pytmx.TiledObjectGroup):
                for object in layer:
                    tiles.append((object.name, object.x, object.y))
                continue

            if not isinstance(layer, pytmx.TiledTileLayer):
                continue

            entity = Wall if layer.properties["solid"] else Entity
            for x, y, image in layer.tiles():
                tile = entity(image, [x*TILE_W, y*TILE_H], [TILE_W,TILE_H])
                # make the top (i.e. last) layer appear on top of everything, including the player
                if i == len(visible_layers)-1:
                    tile.layer = 4
                tiles.append(tile)
        return tiles