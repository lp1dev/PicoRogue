from engine.room_loader import Loader
from random import randrange

class Room:
    def __init__(self, loader, floor, start=False, special=None):
        self.floor = floor
        self.floor = 1 # TODO change, since there is only one floor so far
        self.start = start
        self.finished = False
        self.dead_end = False
        self.width = 0
        self.height = 0
        self.special = special
        self.door_up = False
        self.door_down = False
        self.door_left = False
        self.door_right = False
        self.id = randrange(100000, 999999)

        if start:
            self.tiles = loader.load(self.floor, 'start')
        elif not special:
            chosen_room = randrange(1, 10)
            self.tiles = loader.load(self.floor, '%s' %chosen_room)
        elif special == "⭐":
            self.tiles = loader.load(self.floor, 'item')
        elif special == "💀":
            self.tiles = loader.load(self.floor, 'boss')
        elif special == "💰":
            self.tiles = loader.load(self.floor, 'shop')
        else:
            raise Exception("Unknown room type", special)
            
        self.height = len(self.tiles)
        self.width = len(self.tiles[0]) - 1
        return

    def get_tile(self, x, y):
        if x >= 0 and x < self.height:
            if y >= 0 and y < self.width:
                return self.tiles[x][y]

    def __str__(self):
        output = ""
        for line in self.tiles:
            for tile in line:
                if tile == "0":
                    output += "[   ]"
            output += '\n'
        return output