from engine.room_loader import Loader

class Room:
    def __init__(self, loader, floor, start=False, special=None):
        self.floor = floor
        self.start = start
        self.finished = False
        self.dead_end = False
        self.special = special
        if start:
            self.tiles = loader.load(self.floor, 'start')
            print(self.tiles)
        else:
            self.tiles = loader.load(self.floor, 'placeholder')
        return

    def __str__(self):
        output = ""
        
        return output