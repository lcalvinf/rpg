import pytmx

from settings import *
from sprites import Entity, Wall 

class Layout:
    def __init__(self, filepath):
        import sys
        from pathlib import Path
        dir = Path(sys.argv[0]).parent
        self.filepath = Path.joinpath(dir, filepath)
        self.loaded = False
    def load(self):
        if self.loaded:
            return
        self.loaded = True
        self.tilemap = pytmx.util_pygame.load_pygame(self.filepath)
        self.width = self.tilemap.width
        self.height = self.tilemap.height
        self.full_width = self.width*TILE_W
        self.full_height = self.height*TILE_H
    def tiles(self, flags=None):
        visible_layers = list(self.tilemap.visible_layers)
        background = pg.Surface((self.full_width, self.full_height), flags)
        foreground = pg.Surface((self.full_width, self.full_height), flags)
        background_entity = Entity(background, [0,0])
        foreground_entity = Entity(foreground, [0,0])
        foreground_entity.layer = 4
        tiles = [background_entity, foreground_entity]
        colliders = []
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
                if "cover" in layer.properties and layer.properties["cover"]:
                    foreground.blit(tile.image, tile.pos)
                    continue
                elif not layer.properties["solid"]:
                    background.blit(tile.image, tile.pos)
                    continue

                for collider in colliders:
                    if collider.world_rect.top == tile.world_rect.top and collider.world_rect.bottom == tile.world_rect.bottom:
                        if collider.world_rect.left == tile.world_rect.right or collider.world_rect.right == tile.world_rect.left:
                            collider.size[0] += TILE_W
                            new_image = pg.Surface(collider.size, flags)
                            if collider.world_rect.left < tile.world_rect.left:
                                new_image.blit(collider.image, (0,0))
                                new_image.blit(tile.image, (collider.world_rect.width-TILE_W, 0))
                            else:
                                collider.pos[0] -= TILE_W
                                new_image.blit(collider.image, (TILE_W, 0))
                                new_image.blit(tile.image, (0, 0))
                            collider.image = new_image
                            collider.sprite = new_image
                            break
                    if collider.world_rect.left == tile.world_rect.left and collider.world_rect.right == tile.world_rect.right:
                        if collider.world_rect.top == tile.world_rect.bottom or collider.world_rect.bottom == tile.world_rect.top:
                            collider.size[1] += TILE_H
                            new_image = pg.Surface(collider.world_rect.size, flags)
                            if collider.world_rect.top < tile.world_rect.top:
                                new_image.blit(collider.image, (0,0))
                                new_image.blit(tile.image, (0, collider.world_rect.height-TILE_H))
                            else:
                                collider.pos[1] -= TILE_H
                                new_image.blit(collider.image, (0, TILE_H))
                                new_image.blit(tile.image, (0, 0))
                            collider.image = new_image
                            collider.sprite = new_image
                            break
                else:
                    colliders.append(tile)
        return [*tiles, *self.merge_colliders(colliders)]
    def merge_colliders(self, colliders):
        new = []
        for collider in colliders:
            rect = collider.world_rect
            for merge in new:
                merge_rect = merge.world_rect
                if rect.bottom == merge_rect.bottom and rect.top == merge_rect.top and (merge_rect.left == rect.right or merge_rect.right == rect.left):
                    merge.size[0] += rect.size[0]
                    merge_rect = merge.world_rect
                    new_image = pg.Surface(merge.size, merge.image.get_flags())
                    if merge_rect.left < rect.left:
                        new_image.blit(merge.image, (0,0))
                        new_image.blit(collider.image, (merge_rect.width-rect.width, 0))
                    else:
                        merge.pos[0] -= rect.width
                        new_image.blit(merge.image, (rect.width,0))
                        new_image.blit(collider.image, (0, 0))
                    merge.image = new_image
                    merge.sprite = new_image
                    break
                if rect.right == merge_rect.right and rect.left == merge_rect.left and (merge_rect.top == rect.bottom or merge_rect.bottom == rect.top):
                    merge.size[1] += rect.size[1]
                    merge_rect = merge.world_rect
                    new_image = pg.Surface(merge.size, merge.image.get_flags())
                    if merge_rect.top < rect.top:
                        new_image.blit(merge.image, (0,0))
                        new_image.blit(collider.image, (0, merge_rect.height-rect.height))
                    else:
                        merge.pos[1] -= rect.height
                        new_image.blit(merge.image, (0, rect.height))
                        new_image.blit(collider.image, (0, 0))
                    merge.image = new_image
                    merge.sprite = new_image
                    break
            else:
                new.append(collider)
        return new

