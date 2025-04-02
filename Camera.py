import pygame as pg
from utils import *
from settings import *

class Camera:
    def __init__(self, width, height):
        self.rect = pg.Rect(0,0,width,height)
    def update(self, game, target_pos):
        if square_dist(self.rect.center, target_pos) > CAMERA_LOCK_DIST**2 or vector_size(game.player.old_vel) == 0:
            target_pos = add_vectors(game.player.pos, set_mag(game.player.old_vel, 0))
            dpos = sub_vectors(target_pos, self.rect.center)
            scale = CAMERA_FOLLOW_RATE
            if vector_size(game.player.old_vel) == 0:
                scale = CAMERA_FOLLOW_RATE_STOPPED
            elif square_dist(self.rect.center, target_pos) < (CAMERA_LOCK_DIST*1.5)**2:
                scale /= 2
            dpos = scale_vector(dpos, scale)
            self.set_pos(add_vectors(self.rect.center, dpos))
    def set_pos(self, loc):
        FULL_WIDTH = TILEMAP.full_width
        FULL_HEIGHT = TILEMAP.full_height
        self.rect.center = loc
        self.rect.top = min(max(self.rect.top, 0), FULL_HEIGHT-HEIGHT)
        self.rect.left = min(max(self.rect.left, 0), FULL_WIDTH-WIDTH)
    def get_view(self, sprite):
        return sprite.rect.move(scale_vector(self.rect.topleft,-1))
    def to_screen_coords(self,pos):
        return sub_vectors(pos, self.rect.center)
    def is_off_screen(self, pos):
        screen_pos = self.to_screen_coords(pos)
        return screen_pos[0] < -WIDTH/2 or screen_pos[0] > WIDTH/2 or screen_pos[1] < -HEIGHT/2 or screen_pos[1] > HEIGHT/2
    def is_rect_off_screen(self, rect:pg.Rect):
        return self.is_off_screen(rect.topleft) and self.is_off_screen(rect.bottomright)