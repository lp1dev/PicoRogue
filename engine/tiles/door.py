import pygame
from engine.tiles.tile import Tile
from os.path import join

class Door(Tile):
    def __init__(self, x, y, direction="UP", damage=0, res=None, collide=True):
        self.door_up = direction == "UP"
        self.door_down = direction == "DOWN"
        self.door_left = direction == "LEFT"
        self.door_right = direction == "RIGHT"

        Tile.__init__(self, x, y, damage, res, collide)

    def collide_player(self, player, map):
        print("DOOR TOUCHED")
        return
