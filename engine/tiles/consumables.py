import pygame
from os.path import join
from engine.tiles.tile import Tile
from random import choice

class Consumable(Tile):
    def __init__(self, x, y, res):
        Tile.__init__(self, x, y, 0, res, collide=True, block_bullets=False)

    def collide_player(self, player, map):
        self.destroyed = True

class Battery(Consumable):
    def __init__(self, x, y):
        self.name = "Battery"
        self.res = pygame.image.load(join("resources", "textures", "battery.png")).convert_alpha()
        Consumable.__init__(self, x, y, self.res)

    def collide_player(self, player, map):
        if player.lives < player.max_lives:
            player.lives += 1
            self.destroyed = True

def pick_consumable(x, y):
    consumables = [ Battery ]
    Chosen = choice(consumables)
    return Chosen(x, y)

