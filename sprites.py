import pygame as pg
import pathlib

class SpriteSheet:
    def __init__(self, filename:pathlib.Path|str, tile_size:tuple[float,float], gap:tuple[float,float]=(0,0)):
        self.image = pg.image.load(filename).convert_alpha()
        self.tile_size = tile_size
        self.gap = gap
    def get_image(self, rect:pg.Rect):
        surface = pg.Surface(rect.size, self.image.get_flags())
        surface.blit(self.image, (0, 0), rect)
        return surface
    def get_absolute_loc(self, pos:tuple[float,float]):
        x, y = pos
        w, h = self.tile_size
        gap_w, gap_h = self.gap
        return (x*(w+gap_w), y*(h+gap_h))
    def get_sprite(self, pos:tuple[float,float]):
        w, h = self.tile_size
        return self.get_image(pg.Rect(*self.get_absolute_loc(pos),w,h))
    def get_sprite_at(self, pos:tuple[float,float]):
        return self.get_image(pg.Rect(*pos,*self.tile_size))

import math
class Entity:
    def __init__(self, sprite:pg.Surface, pos: tuple[float,float], size: pg.Rect|None=None):
        if size is None:
            self.size = sprite.get_size()
            self.sprite = sprite
        else:
            self.size = size
            self.sprite = pg.transform.scale(sprite, self.size)
        self.pos = pos
        self.old_vel = [0,0]
        self.vel = [0,0]
        self.dir = 0
        self.target_dir = 0
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        # 25 is arbitrary; we have to scale it down and 25 turned out to work well
        speed = math.sqrt(self.vel[0]**2+self.vel[1]**2)/25
        if speed > 0:
            if self.vel[0] != self.old_vel[0] or self.vel[1] != self.old_vel[1]:
                # flip sign of y because math expects up to be positive but the computer expects it to be negative
                self.target_dir = math.atan2(-self.vel[1], self.vel[0])
                # prevent it from rotating around the long way
                while abs(self.target_dir-self.dir) > math.pi:
                    if self.target_dir > self.dir:
                        self.target_dir -= math.pi*2
                    else:
                        self.target_dir += math.pi*2
            self.dir += (self.target_dir-self.dir)*speed
        self.old_vel = self.vel
        self.vel = [0,0]
    def render(self, screen):
        # Convert to degrees
        dir = self.dir*180/math.pi
        rotated = pg.transform.rotate(self.sprite, dir)
        # Resize and reposition to effectively rotate around the center of the image
        pos = rotated.get_rect(center = self.sprite.get_rect(topleft=self.pos).center)
        screen.blit(rotated, pos)