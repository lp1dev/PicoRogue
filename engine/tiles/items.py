import pygame
from engine.tiles.tile import Tile
from os.path import join
from random import randrange
import importlib

class Item(Tile):
    def __init__(self, x, y, res=None):
        self.name = "Generic Item"
        self.res = pygame.image.load(join("resources", "textures", "item.png")).convert_alpha() if not res else res
        Tile.__init__(self, x, y, 0, self.res, collide=True, block_bullets=False)

    def collide_player(self, player, map):
        return

class Item1(Item):
    def __init__(self, x, y):
        self.name = "Bullets++"
        self.res = pygame.image.load(join("resources", "textures", "item1.png")).convert_alpha()
        Item.__init__(self, x, y, self.res)

    def collide_player(self, player, map):
        player.bullets_delay -= 2
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

class Item4(Item):
    def __init__(self, x, y):
        self.name = "Speed++"
        self.res = pygame.image.load(join("resources", "textures", "item4.png")).convert_alpha()
        Item.__init__(self, x, y, self.res)

    def collide_player(self, player, map):
        player.speed += 1
        self.destroyed = True

class Item5(Item):
    def __init__(self, x, y):
        self.name = "Range++"
        self.res = pygame.image.load(join("resources", "textures", "item5.png")).convert_alpha()
        Item.__init__(self, x, y, self.res)

    def collide_player(self, player, map):
        player.bullets_lifespan += 2
        self.destroyed = True

class Item6(Item):
    def __init__(self, x, y):
        self.name = "Invulnerability++"
        self.res = pygame.image.load(join("resources", "textures", "item6.png")).convert_alpha()
        Item.__init__(self, x, y, self.res)

    def collide_player(self, player, map):
        player.invulnerability_frames += 5
        self.destroyed = True

def pick_item(x, y, pool="all"):
    chosen = randrange(1, 6)
    ItemClass = getattr(importlib.import_module("engine.tiles.items"), "Item%s" %chosen)
    return ItemClass(x, y)

class ItemPedestal(Item):
    def __init__(self, x, y):
        self.price = randrange(7, 15)
        self.item = pick_item(x, y)
        self.font_size = 32
        self.font = pygame.font.Font(join("resources", "fonts", "PressStart2P-Regular.ttf"), self.font_size)
        self.res = pygame.Surface((self.item.res.get_width() + self.font_size, self.item.res.get_height() + self.font_size), pygame.SRCALPHA)
        self.res.blit(self.item.res, (0, 0))
        self.res_price = self.font.render("{:02d}".format(self.price), True, (255,255,255))
        self.res.blit(self.res_price, (self.item.res.get_width() / 2, self.item.res.get_height() - 10))
        Item.__init__(self, x, y, self.res)

    def collide_player(self, player, _map):
        if player.coins >= self.price:
            player.coins -= self.price
            self.item.collide_player(player, _map)
            self.destroyed = True