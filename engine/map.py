from random import randrange, choice
from engine.room import Room
from engine.room_loader import Loader
from math import sqrt

LOADER=Loader('rooms/')
MAX_WIDTH = 10
MAX_HEIGHT = 9
ROOM_CREATION_PROB = 2
MIN_DEAD_ENDS = 4

class Map:
    def __init__(self, floor=1, seed=None):
        self.seed = seed
        self.floor = floor
        self._size = int(3.33 * floor + randrange(5, 7))
        self.set_rooms = 0
        self.dead_ends = []
        self.secret_room = None
        self.super_secret_room = None
        self.boss_room = None
        self.item_room = None
        self.shop = None
        self.cursor = (4, 4)
        print('Map size is',  self._size)

        self.clear()
        self.generate()

        print(self)

    def clear(self):
        self._map = []
        for i in range(0, MAX_HEIGHT):
            self._map.append([])
            for j in range(0, MAX_WIDTH):
                self._map[i].append(None)

    def __str__(self):
        output = ""

        for i in range(0, MAX_HEIGHT):
            for j in range(0, MAX_WIDTH):
                room = self._map[i][j]
                if isinstance(room, Room):
                    if not room.special:
                        output += "[%s ]" %self.count_neighbours(i, j)
                    else:
                        output += "[%s]" %room.special
                else:
                    output += "    "
            output += "\n"
        room = self._map[self.cursor[0]][self.cursor[1]]
        output += str(room)
        return output

    def count_dead_ends(self):
        dead_ends = 0
        self.dead_ends = []
        for i in range(0, MAX_HEIGHT):
            for j in range(0, MAX_WIDTH):
                if self.count_neighbours(i, j) < 2 and isinstance(self._map[i][j], Room):
                    self._map[i][j].dead_end = True
                    self.dead_ends.append((i, j))
                    dead_ends += 1
        return dead_ends

    def generate(self):
        while len(self.dead_ends) < MIN_DEAD_ENDS:
            self.clear()
            self._map[4][4] = Room(LOADER, self.floor, start=True, special="🏁") # We set the starting room
            self.set_rooms = 1
            self.generate_next_room(4, 4)
            self.count_dead_ends()
            print(self)
        if not self.assign_special_rooms():
            return self.generate()

    def assign_special_rooms(self):
        available_rooms = self.dead_ends
        boss_room = choice(available_rooms)
        self._map[boss_room[0]][boss_room[1]] = Room(LOADER, self.floor, start=False, special="💀")
        available_rooms.remove(boss_room)
        item_room = choice(available_rooms)
        self._map[item_room[0]][item_room[1]] = Room(LOADER, self.floor, start=False, special="⭐")
        available_rooms.remove(item_room)
        shop = choice(available_rooms)
        self._map[shop[0]][shop[1]] = Room(LOADER, self.floor, start=False, special="💰")
        available_rooms.remove(shop)
        if self.dist(boss_room[0], boss_room[1], 4, 4) < 2:
            return False
        if not self._map[4][4].start:
            return False
        return True

    def dist(self, x1, y1, x2, y2):
        """ Calculates the distance between two positions """
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


    def generate_next_room(self, cursor_x, cursor_y):
        # If we generated enough rooms, we stop
        if self.set_rooms >= self._size:
            return

        # We handle the top tile
        if cursor_x + 1 < MAX_HEIGHT:
            x = cursor_x + 1
            if randrange(0, ROOM_CREATION_PROB) > 0:
                if not isinstance(self._map[x][cursor_y], Room):
                    if not self.count_neighbours(x, cursor_y) > 1:
                        self._map[x][cursor_y] = Room(LOADER, self.floor, start=False)
                        self.set_rooms += 1
                        self.generate_next_room(x, cursor_y)

        # We handle the bottom tile
        if cursor_x - 1 >= 0:
            x = cursor_x - 1
            if randrange(0, ROOM_CREATION_PROB) > 0:
                if not isinstance(self._map[x][cursor_y], Room):
                    if not self.count_neighbours(x, cursor_y) > 1:
                        self._map[x][cursor_y] = Room(LOADER, self.floor, start=False)
                        self.set_rooms += 1
                        self.generate_next_room(x, cursor_y)

        # We handle the right tile
        if cursor_y + 1 < MAX_WIDTH:
            y = cursor_y + 1
            if randrange(0, ROOM_CREATION_PROB) > 0:
                if not isinstance(self._map[cursor_x][y], Room):
                    if not self.count_neighbours(cursor_x, y) > 1:
                        self._map[cursor_x][y] = Room(LOADER, self.floor, start=False)
                        self.set_rooms += 1
                        self.generate_next_room(cursor_x, y)

        # We handle the left tile
        if cursor_y - 1 > 0:
            y = cursor_y - 1
            print(self._map[cursor_x][y])
            if randrange(0, ROOM_CREATION_PROB) > 0:
                if not isinstance(self._map[cursor_x][y], Room):
                    if not self.count_neighbours(cursor_x, y) > 1:
                        self._map[cursor_x][y] = Room(LOADER, self.floor, start=False)
                        self.set_rooms += 1
                        self.generate_next_room(cursor_x, y)
        return

    def count_neighbours(self, cursor_x, cursor_y):
        neighbours = 0
        if cursor_x > 0:
            if isinstance(self._map[cursor_x - 1][cursor_y], Room):
                neighbours += 1
        if cursor_x < MAX_HEIGHT - 1:
            if isinstance(self._map[cursor_x + 1][cursor_y], Room):
                neighbours += 1
        if cursor_y > 0:
            if isinstance(self._map[cursor_x][cursor_y - 1], Room):
                neighbours += 1
        if cursor_y < MAX_WIDTH - 1:
            if isinstance(self._map[cursor_x][cursor_y + 1], Room):
                neighbours += 1
        return neighbours