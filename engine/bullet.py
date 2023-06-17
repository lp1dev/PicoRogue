import pygame
from os.path import join
from random import randrange

class Bullet:
    def __init__(self, x, y, vec_x, vec_y, is_player=True, speed=12, damage=1, lifespan=60):
        self.id = "bullet_%s" %randrange(0, 10000)
        self.is_player = is_player
        self.speed = speed
        self.x = x
        self.y = y
        self.vec_x = vec_x
        self.vec_y = vec_y
        self.age = 0
        self.lifespan = lifespan
        self.damage = damage
        self.rect = None
        self.res = pygame.image.load(join("resources", "textures", "bullet.png")).convert_alpha()
        if not is_player:
            self.res = pygame.image.load(join("resources", "textures", "bullet_red.png")).convert_alpha()
        return