import pygame as pg
import pathlib

from settings import *
from utils import *

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
class Entity(pg.sprite.Sprite):
    def __init__(self, sprite:pg.Surface, pos: tuple[float,float], size: tuple[int,int]|None=None):
        super().__init__()
        if size is None:
            self.size = sprite.get_size()
            self.sprite = sprite
        else:
            self.size = size
            if sprite.get_size()[0] != size[0] or sprite.get_size()[1] != size[1]:
                self.sprite = pg.transform.scale(sprite, self.size)
            else:
                self.sprite = sprite
        self.pos = pos
        self.image = self.sprite
        # rect and radius are used by pg.sprite functions to know the size of the sprite
        self.rect = self.world_rect 
        self.radius = min(*self.size)/2
        self.old_vel = [0,0]
        self.vel = [0,0]
        self.dir = 0
        self.target_dir = 0
    @property
    def world_rect(self):
        return pg.Rect(*self.pos,*self.size)
    def update(self, game):
        self.pos = add_vectors(self.pos, self.vel)
        for wall in pg.sprite.spritecollide(self, game.walls, False, lambda a, b: a.world_rect.colliderect(b.world_rect)):
            self.pos = sub_vectors(self.pos,self.vel)
            self.vel = set_mag((sub_vectors(wall.pos,self.pos)),-2)
            self.pos = add_vectors(self.pos, self.vel)
            self.on_bounce(wall)
            break
        # we change self.rect to render the sprite properly, so we have to reset it here
        self.rect = self.world_rect 
        # 25 is arbitrary; we have to scale it down and 25 turned out to work well
        speed = vector_size(self.vel)/25
        if speed > 0:
            if not vectors_eq(self.vel, self.old_vel):
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
        self.render(game)
    def on_bounce(self, wall):
        pass
    def render(self, game):
        # Convert to degrees
        dir = self.dir*180/math.pi
        rotated = pg.transform.rotate(self.sprite, dir)
        # Resize and reposition to effectively rotate around the center of the image
        pos = rotated.get_rect(center = self.sprite.get_rect(topleft=self.pos).center)
        self.image = rotated
        if DEBUG:
            pg.draw.rect(self.image, GREEN, pg.Rect(0,0,*self.image.get_size()), 1)
        self.rect = pos
        self.rect = game.camera.get_view(self)

class Wall(Entity):
    def __init__(self, *args):
        super().__init__(*args)

class Bullet(Entity):
    def __init__(self, vel, *args):
        super().__init__(*args)
        self.vel = vel
        self.old_vel = vel
        self.bounces = 0
        self.kills = 0
    def update(self, game):
        self.vel = set_mag((self.old_vel),BULLET_SPEED)
        if len(pg.sprite.spritecollide(self, game.enemies, True)) > 0:
            self.kills += 1
            score = self.kills
            if self.bounces > 0:
                score += 1
                game.spawn_text_particle(random.choice(CALLOUTS["bank"]), self.pos)

            game.spawn_text_particle(f"+{score}", self.pos)

            if self.kills > 1:
                game.spawn_text_particle(random.choice(CALLOUTS["combo"]), self.pos)

            game.score += score
            self.vel = rotate_vector(self.vel, random.random()*math.pi/4-math.pi/2)
            self.target_dir = math.atan2(-self.vel[1], self.vel[0])
            self.dir = self.target_dir
            self.old_vel = self.vel
        if game.camera.is_rect_off_screen(self.world_rect):
            self.kill()
        super().update(game)
    def on_bounce(self, _):
        self.bounces += 1

import random
class TextParticle(Entity):
    def __init__(self, game, text, pos):
        angle = random.random()*90-45
        sprite = pg.transform.scale_by(pg.transform.rotate(game.font.render(text, True, BLACK),angle), random.random()*0.25+0.5)
        super().__init__(sprite, sub_vectors(add_vectors(pos, (random.randint(-50,50), random.randint(-50,50))),game.camera.rect.topleft), sprite.get_size())
        self.lifetime = random.random()*200+100
        self.initial_lifetime = self.lifetime
    def render(self, game):
        super().render(game)
        self.rect = self.rect.move(game.camera.rect.topleft)
    def update(self, game):
        self.lifetime -= game.clock.get_time()
        if self.lifetime < 0:
            self.kill()

        super().update(game)

        life = self.lifetime/self.initial_lifetime
        if life > 0.5:
            scale = (1-life)*2
            self.rect = self.rect.scale_by(scale)
            self.image = pg.transform.scale_by(self.image, scale)

        alpha = 1-abs(life-0.5)*2
        self.image.set_alpha(alpha*255)

class Zombie(Entity):
    def __init__(self, *args):
        super().__init__(*args)
        self.game = None
    def update(self, game):
        self.vel = scale_vector(normalize_vector(sub_vectors(game.player.pos, self.pos)), ZOMBIE_SPEED)
        if pg.sprite.collide_circle(self, game.player):
            game.playing = False
        self.game = game
        super().update(game)
    def kill(self):
        super().kill()
        if self.game:
            self.game.spawn_zombie()

class Player(Entity):
    def __init__(self, *args):
        super().__init__(*args)
    def update(self, game):
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            self.vel[1] = -SPEED
        elif keys[pg.K_DOWN]:
            self.vel[1] = SPEED
        if keys[pg.K_LEFT]:
            self.vel[0] = -SPEED
        elif keys[pg.K_RIGHT]:
            self.vel[0] = SPEED
        if self.vel[0] != 0 and self.vel[1] != 0:
            cur_speed = vector_size(self.vel)
            scale = SPEED/cur_speed
            self.vel = scale_vector(self.vel, scale)
        
        super().update(game)
    def fire_bullet(self, game):
        bullet = Bullet(rotate_vector([BULLET_SPEED,0], self.dir), pg.transform.rotate(game.spritesheets["tilesheet"].get_sprite([11,9]), -45), list(self.pos))
        bullet.dir = self.dir
        bullet.target_dir = self.dir
        bullet.add(game.particles, game.all_sprites)
        game.all_sprites.change_layer(bullet, 1)