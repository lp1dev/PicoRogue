import pygame
from engine.tiles.tile import Tile
from engine.tiles.consumables import pick_consumable
from random import randrange
from os.path import join

class Flame(Tile):
    def __init__(self, x, y, damage=1, res=None, collide=True):
        self.lives = 3
        Tile.__init__(self, x, y, damage, res, collide)

    def hit(self, damage=1):
        if self.lives > 1:
            self.lives -= 1
            self.res = pygame.image.load(join("resources", "textures", "fire%s.png" %self.lives)).convert_alpha()
        else:
            self.destroyed = True

    def after_destroyed(self, pygame_handler):
        if randrange(0, 6) == 1:
            pygame_handler.tiles.append(pick_consumable(self.x, self.y))
        return