
import pygame
from os.path import join
from random import choice, randrange
from math import sqrt
from engine.tiles.monsters.monster import Monster
from engine.tools import move_towards
from engine.bullet import Bullet
from engine.tiles.items import pick_item

class Boss(Monster):
    def __init__(self, x, y, lives=4, damage=1, res=None, collide=True):
        Monster.__init__(self, x, y, damage, res, collide, lives)

    def after_destroyed(self, pygame_handler):
        pygame_handler.tiles.append(pick_item(self.x, self.y))

class EyeBoss(Boss):
    def __init__(self, x, y, level):
        self.res = pygame.image.load(join("resources", "textures", "boss1.png")).convert_alpha()

        self.bullets_delay = 180 - (level * 2)
        self.last_bullet = 0
        self.bullet_speed = 4

        self.speed = 2
        self.lives = 40 + (5 * level)
        self.phase = 0
        self.last_phase_shift = 0
        self.bullet_phase = 0
        self.shift_time = (6 + randrange(1,5)) * 60 # 6 sec + 1,5 sec


        Boss.__init__(self, x, y, self.lives, damage=1, res=self.res)

    def play(self, pygame_handler):
        print('Phase', self.phase)
        if self.last_phase_shift > self.shift_time:
            self.phase = 0 if self.phase == 1 else 1
            self.last_phase_shift = 0
        else:
            self.last_phase_shift += 1

        if self.phase == 1:
            self.speed = 3
            move_towards(self, pygame_handler.player.x, pygame_handler.player.y)
        else:
            self.speed = 0.5
            self.last_bullet += 1
            if self.last_bullet > self.bullets_delay:
                self.shoot(pygame_handler)
                self.last_bullet = 0
            move_towards(self, pygame_handler.player.x, pygame_handler.player.y)


    def shoot(self, pygame_handler):
        self.bullet_phase = 0 if self.bullet_phase == 1 else 1

        vectors1 = [
            (self.bullet_speed, 0),
            (0, self.bullet_speed),
            (-self.bullet_speed, 0),
            (0, -self.bullet_speed)
        ]

        vectors2 = [
            (self.bullet_speed, self.bullet_speed),
            (-self.bullet_speed, self.bullet_speed),
            (-self.bullet_speed, -self.bullet_speed),
            (self.bullet_speed, -self.bullet_speed)
        ]

        bullet_vectors = vectors1 if self.bullet_phase == 0 else vectors2

        for vector in bullet_vectors:
            bullet = Bullet(self.get_center_x(), self.get_center_y(), vector[0], vector[1], is_player=False, speed=self.bullet_speed, lifespan=200)
            pygame_handler.hostile_bullets.append(bullet)


def pick_boss(x, y, level, pool="all"):
    bosses = [ EyeBoss ]
    Chosen = choice(bosses)
    return Chosen(x, y, level)
