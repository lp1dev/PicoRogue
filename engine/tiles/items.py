import pygame
from engine.tiles.tile import Tile
from os.path import join

class Item(Tile):
    def __init__(self, x, y):
        self.name = "Generic Item"
        self.res = pygame.image.load(join("resources", "textures", "item.png")).convert_alpha()
        Tile.__init__(self, x, y, 0, self.res, True)

    def collide_player(self, player, map):
        return

class Item1(Item):
    def __init__(self, x, y):
        self.name = "Bullets++"
        self.res = pygame.image.load(join("resources", "textures", "item1.png")).convert_alpha()
        Item.__init__(self, x, y)

    def collide_player(self, player, map):
        print("TOUCHED THE PLAYER IN ITEM1")
        player.bullets_delay -= 10
        self.destroyed = True