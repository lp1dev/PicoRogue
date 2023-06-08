import pygame
from os.path import join
from math import sqrt, hypot
from engine.tools import move_towards
from engine.bullet import Bullet
from engine.tools import distance
from engine.tiles.monsters.monster import Monster
from engine.animation import Animation

class Eye(Monster):
    def __init__(self, x, y, damage=1, res=None, collide=True, level=1):
        self.bullets_delay = 70 - (level * 2)
        self.last_bullet = 0
        self.bullet_speed = 5
        self.lives = level * 2
        self.area = 450 # in pixels
        Monster.__init__(self, x, y, damage, None, collide, self.lives)

    def play(self, pygame_handler):
        if distance(pygame_handler.player, self) > self.area:
            return
        self.last_bullet += 1
        if self.last_bullet > self.bullets_delay:
            self.shoot(pygame_handler)
            self.last_bullet = 0

    def shoot(self, pygame_handler):
        vector_x, vector_y = pygame_handler.player.x - self.x, pygame_handler.player.y - self.y
        distance = sqrt(vector_x ** 2 + vector_y **2)
        direc_x, direc_y = (self.bullet_speed * vector_x/distance, self.bullet_speed * vector_y/distance)
        bullet = Bullet(self.x, self.y, direc_x, direc_y, is_player=False, speed=self.bullet_speed, lifespan=100)
        pygame_handler.hostile_bullets.append(bullet)



class Eye2(Monster):
    def __init__(self, x, y, damage=1, res=None, collide=True, level=1):
        self.bullets_delay = 200 - (level * 2)
        self.last_bullet = 0
        self.bullet_speed = 4
        self.res = pygame.image.load(join("resources", "textures", "eye2.png")).convert_alpha()
        self.animation = Animation("eye2_tileset.png", 3, fps=60, tile_length=64, selected_frame=0, width=None, height=None, duration=0.20)
        self.speed = level * 1.5
        self.lives = level * 2
        self.area = 450 # in pixels
        Monster.__init__(self, x, y, damage, self.res, collide, self.lives)

    def play(self, pygame_handler):
        if distance(pygame_handler.player, self) > self.area:
            return
        self.res = self.animation.get_next_frame()
        self.last_bullet += 1
        if self.last_bullet > self.bullets_delay:
            self.shoot(pygame_handler)
            self.last_bullet = 0

        move_towards(self, pygame_handler.player.x, pygame_handler.player.y)

    def shoot(self, pygame_handler):
        vector_x, vector_y = pygame_handler.player.x - self.x, pygame_handler.player.y - self.y
        distance = sqrt(vector_x ** 2 + vector_y **2)
        direc_x, direc_y = (self.bullet_speed * vector_x/distance, self.bullet_speed * vector_y/distance)
        bullet = Bullet(self.x, self.y, direc_x, direc_y, is_player=False, speed=self.bullet_speed, lifespan=100)
        pygame_handler.hostile_bullets.append(bullet)