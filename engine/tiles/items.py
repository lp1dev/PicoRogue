import pygame
from engine.tiles.tile import Tile
from os.path import join
from random import randrange
import importlib

class Item(Tile):
    def __init__(self, x, y, res=None):
        self.name = "Generic Item"
        self.res = pygame.image.load(join("resources", "textures", "item.png")).convert_alpha() if not res else res
        Tile.__init__(self, x, y, 0, self.res, True)

    def collide_player(self, player, map):
        return

class Item1(Item):
    def __init__(self, x, y):
        self.name = "Bullets++"
        self.res = pygame.image.load(join("resources", "textures", "item1.png")).convert_alpha()
        Item.__init__(self, x, y, self.res)

    def collide_player(self, player, map):
        player.bullets_delay -= 10
        self.destroyed = True

class Item2(Item):
    def __init__(self, x, y):
        self.name = "Damage++"
        self.res = pygame.image.load(join("resources", "textures", "item2.png")).convert_alpha()
        Item.__init__(self, x, y, self.res)

    def collide_player(self, player, map):
        player.damage += 1.5
        self.destroyed = True

class Item3(Item):
    def __init__(self, x, y):
        self.name = "Health++"
        self.res = pygame.image.load(join("resources", "textures", "item3.png")).convert_alpha()
        Item.__init__(self, x, y, self.res)

    def collide_player(self, player, map):
        player.max_lives += 1
        player.lives += 1
        self.destroyed = True

def pick_item(x, y):
    chosen = randrange(1, 4)
    ItemClass = getattr(importlib.import_module("engine.tiles.items"), "Item%s" %chosen)
    return ItemClass(x, y)