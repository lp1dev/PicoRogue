from abc import ABC, abstractmethod
from random import randrange

class Tile:
    def __init__(self, x, y, damage=0, res=None, collide=False, block_bullets=True):
        self.id = randrange(0, 99999)
        self.x = x
        self.y = y
        self.damage = damage
        self.width = 64
        self.res = res
        self.collide = collide
        self.block_bullets = block_bullets
        self.rect = None
        self.destroyed = False
        
    @abstractmethod
    def hit(self, damage=1):
        pass

    @abstractmethod
    def collide_player(self, player, map):
        pass

    @abstractmethod
    def after_destroyed(self, pygame_handler):
        pass

    def get_center_x(self):
        return self.x + self.res.get_width() / 2
    
    def get_center_y(self):
        return self.y + self.res.get_height() / 2