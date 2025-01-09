import pygame as pg

class SpriteSheet:
    def __init__(self, filename, tile_size, gap=(0,0)):
        self.image = pg.image.load(filename).convert_alpha()
        self.tile_size = tile_size
        self.gap = gap
    def get_image(self, rect):
        surface = pg.Surface(rect.size, self.image.get_flags())
        surface.blit(self.image, (0, 0), rect)
        return surface
    def get_absolute_loc(self, pos):
        x, y = pos
        w, h = self.tile_size
        gap_w, gap_h = self.gap
        return (x*(w+gap_w), y*(h+gap_h))
    def get_sprite(self, pos):
        w, h = self.tile_size
        return self.get_image(pg.Rect(*self.get_absolute_loc(pos),w,h))
    def get_sprite_at(self, pos):
        return self.get_image(pg.Rect(*pos,*self.tile_size))

class Entity:
    def __init__(self, sprite, pos, size=None):
        if size is None:
            self.size = sprite.get_size()
            self.sprite = sprite
        else:
            self.size = size
            self.sprite = pg.transform.scale(sprite, self.size)
        self.pos = pos
        self.dir = 0
    def render(self, screen):
        screen.blit(pg.transform.rotate(self.sprite, self.dir), self.pos)