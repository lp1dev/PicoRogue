import pygame
from os.path import join
from engine.tiles.tile import Tile
from random import choice, randrange

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

class Coin(Consumable):
    def __init__(self, x, y):
        self.name = "Coin"
        self.res = pygame.image.load(join("resources", "textures", "coin.png")).convert_alpha()
        Consumable.__init__(self, x, y, self.res)

    def collide_player(self, player, map):
        if player.coins < player.max_coins:
            player.coins += 1
            self.destroyed = True

def pick_consumable(x, y):
    consumables = [ Battery, Coin ]
    Chosen = choice(consumables)
    return Chosen(x, y)

class ConsumablePedestal(Consumable):
    def __init__(self, x, y):
        self.price = randrange(3,5)
        #self.item = pick_consumable(x, y) 
        self.item = Battery(x, y)
        self.font_size = 32
        self.font = pygame.font.Font(join("resources", "fonts", "PressStart2P-Regular.ttf"), self.font_size)
        self.res = pygame.Surface((self.item.res.get_width() + self.font_size, self.item.res.get_height() + self.font_size), pygame.SRCALPHA)
        self.res.blit(self.item.res, (0, 0))
        self.res_price = self.font.render("{:02d}".format(self.price), True, (255,255,255))
        self.res.blit(self.res_price, (self.item.res.get_width() / 2, self.item.res.get_height() - 10))
        Consumable.__init__(self, x, y, self.res)

    def collide_player(self, player, _map):
        if player.coins >= self.price:
            player.coins -= self.price
            self.item.collide_player(player, _map)
            self.destroyed = True