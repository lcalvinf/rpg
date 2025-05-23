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
    def collide(self, wall):
        wall: Entity = wall
        clip = self.world_rect.clip(wall.world_rect)
        self.pos = sub_vectors(self.pos,scale_vector(self.vel, CHARACTER_SCALE))
        if clip.height == self.world_rect.height:
            self.vel[0] *= -1
        elif clip.width == self.world_rect.width:
            self.vel[1] *= -1
        elif clip.width > clip.height:
            self.vel[1] *= -1
        elif clip.height > clip.width:
            self.vel[0] *= -1
        else:
            self.vel[0] *= -1
            self.vel[1] *= -1

        self.pos = add_vectors(self.pos, self.vel)
        self.on_bounce(wall)
    def update(self, game):
        self.pos = add_vectors(self.pos, scale_vector(self.vel, CHARACTER_SCALE))
        for wall in pg.sprite.spritecollide(self, game.walls, False, lambda a, b: a.world_rect.colliderect(b.world_rect)):
            self.collide(wall)
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
    def debug_render(self, screen, game):
        pass

class Wall(Entity):
    def __init__(self, *args):
        super().__init__(*args)

class Goal(Wall):
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
        self.game = game
        self.vel = set_mag((self.old_vel),BULLET_SPEED)
        if len(pg.sprite.spritecollide(self, game.enemies, True)) > 0:
            game.play_sound("kill")
            self.kills += 1
            score = self.kills
            if self.bounces > 0:
                score += 1
                game.spawn_text_particle(random.choice(CALLOUTS["bank"]), self.pos)

            game.spawn_text_particle(f"+{score}", self.pos)

            if self.kills > 1:
                game.spawn_text_particle(random.choice(CALLOUTS["combo"]), self.pos)
            
            ammo_odds = (1-(game.player.ammo+1)/MAX_AMMO)**2
            for i in range(random.randint(1,3)):
                particle_type = AmmoParticle if random.random() < ammo_odds else HealthParticle 
                game.spawn_particle(particle_type(game, add_vectors(self.pos, (random.random()*30-15, random.random()*30-15))))

            game.score += score
            self.vel = rotate_vector(self.vel, random.random()*math.pi/4-math.pi/2)
            self.target_dir = math.atan2(-self.vel[1], self.vel[0])
            self.dir = self.target_dir
            self.old_vel = self.vel

            if self.bounces+self.kills > BULLET_BOUNCES:
                self.kill()
        if game.camera.is_rect_off_screen(self.world_rect):
            self.kill()
        super().update(game)
    def on_bounce(self, _):
        self.bounces += 1
        self.game.play_sound("collide")
        if self.bounces+self.kills > BULLET_BOUNCES:
            self.kill()

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

class Particle(Entity):
    def __init__(self, sprite, pos, lifetime_min, lifetime_max):
        super().__init__(sprite, pos, sprite.get_size())
        self.lifetime = random.random()*(lifetime_max-lifetime_min)+lifetime_min
        self.initial_lifetime = self.lifetime
    def update(self, game):
        self.lifetime -= game.clock.get_time()
        if self.lifetime < 0:
            self.kill()

        if pg.sprite.collide_circle(self, game.player):
            self.collide_player(game)
            self.kill()
        
        super().update(game)

        life = self.lifetime/self.initial_lifetime
        if life > 0.99:
            scale = (1-life)/0.01
            self.rect = self.rect.scale_by(scale)
            self.image = pg.transform.scale_by(self.image, scale)
        elif life < 0.25:
            alpha = life*4
            self.image.set_alpha(alpha*255)
    def collide_player(self, game):
        pass
class AmmoParticle(Particle):
    def __init__(self, game, pos):
        sprite = pg.transform.rotate(game.ammo_sprite, random.random()*360)
        super().__init__(sprite, pos, 5000, 15000)
    def collide_player(self, game):
        if game.player.ammo < MAX_AMMO:
            game.player.ammo += 1
            game.spawn_text_particle(random.choice(CALLOUTS["ammo"]), self.pos)
            game.play_sound("pickup")

class HealthParticle(Particle):
    def __init__(self, game, pos):
        sprite = game.spritesheets["tilesheet"].get_sprite((9,7))
        super().__init__(sprite, pos, 5000, 1500)
    def collide_player(self, game):
        if game.player.health < MAX_HEALTH:
            game.player.health += 1
            game.spawn_text_particle(random.choice(CALLOUTS["health"]), self.pos)
        else:
            game.score += 1
            game.spawn_text_particle("+1", self.pos)
        game.play_sound("pickup")

class Zombie(Entity):
    def __init__(self, *args):
        super().__init__(*args)
        self.follow_mode = True
        self.target = None
        self.mode_timer = ZOMBIE_MODE_TIME+random.randint(-1000, 1000)
        self.game = None
    def update(self, game):
        if self.target is None:
            self.target = [*game.player.pos]

        if self.follow_mode and not game.camera.is_off_screen(self.pos):
            self.target = add_vectors(self.target, scale_vector(normalize_vector(sub_vectors(game.player.pos, self.target)), 2))
        randomize = 10 if self.follow_mode else self.mode_timer*100/ZOMBIE_MODE_TIME
        self.target = add_vectors(self.target, [random.random()*randomize-randomize/2, random.random()*randomize-randomize/2])
        self.vel = scale_vector(normalize_vector(sub_vectors(self.target, self.pos)), ZOMBIE_SPEED)

        if pg.sprite.collide_circle(self, game.player):
            game.player.hit(game)
        self.game = game

        self.mode_timer -= game.clock.get_time()
        if self.mode_timer <= 0:
            self.mode_timer = ZOMBIE_MODE_TIME
            self.follow_mode = not self.follow_mode

        super().update(game)
    def kill(self):
        super().kill()
        if self.game:
            self.game.spawn_zombie()
    def on_bounce(self, _):
        if not self.follow_mode or self.target is None:
            return
        self.follow_mode = False
        self.mode_timer = 500
        self.target = add_vectors(self.pos, scale_vector(self.vel, 100/ZOMBIE_SPEED))
    def debug_render(self, screen, game):
        pg.draw.circle(screen, RED, self.target, 2)
        pg.draw.line(screen, RED, self.pos, self.target, 2)

class Player(Entity):
    def __init__(self, *args):
        super().__init__(*args)
        self.game = None
        self.health = MAX_HEALTH
        self.ammo = MAX_AMMO
        self.safe = False
        self.hit_this_frame = False
    def on_bounce(self, wall):
        if type(wall) is Goal:
            self.game.next_level()
        else:
            self.game.play_sound("collide")
    def update(self, game):
        self.game = game
        self.safe = self.safe and self.hit_this_frame
        self.hit_this_frame = False

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
        if self.ammo <= 0:
            game.spawn_text_particle("Out of Ammo!", self.pos)
            return
        self.ammo -= 1
        bullet = Bullet(rotate_vector([BULLET_SPEED,0], self.dir), pg.transform.rotate(game.spritesheets["tilesheet"].get_sprite([11,9]), -45), list(self.pos))
        bullet.dir = self.dir
        bullet.target_dir = self.dir
        bullet.add(game.particles, game.all_sprites)
        game.all_sprites.change_layer(bullet, 1)
    def hit(self, game):
        self.hit_this_frame = True
        if self.safe:
            return
        self.safe = True
        self.health -= 1
        if self.health < 1:
            game.playing = False
            game.play_sound("death")
            return
        game.play_sound("hit")