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
    def __init__(self, player, floor=1, seed=None):
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
        self.width = MAX_WIDTH
        self.height = MAX_HEIGHT
        print('Map size is',  self._size)

        self.clear()
        self.generate()

        print(self)

    def clear(self):
        self._map = []
        for y in range(0, MAX_HEIGHT):
            self._map.append([])
            for x in range(0, MAX_WIDTH):
                self._map[y].append(None)

    def __str__(self):
        output = ""

        # Printing the map
        for y in range(0, MAX_HEIGHT):
            for x in range(0, MAX_WIDTH):
                room = self._map[y][x]
                if isinstance(room, Room):
                    if not room.special:
                        output += "[%s ]" %self.count_neighbours(y, x)
                    else:
                        output += "[%s]" %room.special
                else:
                    output += "    "
            output += "\n"

        # Printing the room
        output += '\n'
        room = self._map[self.cursor[0]][self.cursor[1]]
        height = len(room.tiles)
        width = len(room.tiles[0])

        # Printing the top section with the potential door
        for i in range(0, width + 1):
            output += "=="
        output += "\n"

        for i in range(0, width):
            if i == int(width/2) and self.get_room(self.cursor[0] - 1, self.cursor[1]):
                output += '[]' # If there is a room above, we print the door
            else:
                output += "__" if i != 0 else "\\_"
        output += "_/\n"

        # Printing the tiles

        for i, line in enumerate(room.tiles):
            if i == int(height/2) and self.get_room(self.cursor[0], self.cursor[1] - 1):
                output += "[]"
            else:
                output += " |"

            for tile in line:
                if tile == "0":
                    output += "  "
                elif tile == "F":
                    output += "🔥"
                elif tile == "S":
                    output += "😭"

            if i == int(height/2) and self.get_room(self.cursor[0], self.cursor[1] + 1):
                output += " []\n"
            else:
                output += " |\n"
        
        # Printing the bottom section with the potential door

        for i in range(0, width):
            if i == int(width/2) and self.get_room(self.cursor[0] + 1, self.cursor[1]):
                output += '[]' # If there is a room under, we print the door
            else:
                output += "--" if i != 0 else "/-"
        output += "-\\\n"

        for i in range(0, width + 1):
            output += "=="
        output += "\n"

        return output

    def move(self, y, x):
        self.cursor = (y, x)

    def get_current_room(self):
        return self.get_room(self.cursor[0], self.cursor[1])

    def get_room(self, y, x):
        """ Return the room at a position or None if it does not exists """
        if x > 0 and y > 0:
            if x < MAX_WIDTH and y < MAX_HEIGHT:
                return self._map[y][x]

    def count_dead_ends(self):
        dead_ends = 0
        self.dead_ends = []
        for y in range(0, MAX_HEIGHT):
            for x in range(0, MAX_WIDTH):
                if self.count_neighbours(y, x) < 2 and isinstance(self._map[y][x], Room):
                    self._map[y][x].dead_end = True
                    self.dead_ends.append((y, x))
                    dead_ends += 1
        return dead_ends

    def set_doors(self):
        """ Setting up rooms doors inside Room objects """
        
        for y in range(0, MAX_HEIGHT):
            for x in range(0, MAX_WIDTH):
                if isinstance(self._map[y][x], Room):
                    if y > 0 and isinstance(self._map[y - 1][x], Room):
                        self._map[y][x].door_up = True
                    if y < MAX_HEIGHT - 1 and isinstance(self._map[y + 1][x], Room):
                        self._map[y][x].door_down = True
                    if x > 0 and isinstance(self._map[y][x - 1], Room):
                        self._map[y][x].door_left = True
                    if x < MAX_WIDTH - 1 and isinstance(self._map[y][x + 1], Room):
                        self._map[y][x].door_right = True


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
        self.set_doors()

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


    def generate_next_room(self, cursor_y, cursor_x):
        # If we generated enough rooms, we stop
        if self.set_rooms >= self._size:
            return

        # We handle the top tile
        if cursor_y - 1 > 0:
            y = cursor_y - 1
            if randrange(0, ROOM_CREATION_PROB) > 0:
                if not isinstance(self._map[y][cursor_x], Room):
                    if not self.count_neighbours(y, cursor_x) > 1:
                        self._map[y][cursor_x] = Room(LOADER, self.floor, start=False)
                        self.set_rooms += 1
                        self.generate_next_room(y, cursor_x)

        # We handle the bottom tile
        if cursor_y + 1 < MAX_HEIGHT:
            y = cursor_y + 1
            if randrange(0, ROOM_CREATION_PROB) > 0:
                if not isinstance(self._map[y][cursor_x], Room):
                    if not self.count_neighbours(y, cursor_x) > 1:
                        self._map[y][cursor_x] = Room(LOADER, self.floor, start=False)
                        self.set_rooms += 1
                        self.generate_next_room(y, cursor_x)

        # We handle the right tile
        if cursor_x + 1 < MAX_WIDTH:
            x = cursor_x + 1
            if randrange(0, ROOM_CREATION_PROB) > 0:
                if not isinstance(self._map[cursor_y][x], Room):
                    if not self.count_neighbours(cursor_y, x) > 1:
                        self._map[cursor_y][x] = Room(LOADER, self.floor, start=False)
                        self.set_rooms += 1
                        self.generate_next_room(cursor_y, x)

        # We handle the left tile
        if cursor_x - 1 > 0:
            x = cursor_x - 1
            if randrange(0, ROOM_CREATION_PROB) > 0:
                if not isinstance(self._map[cursor_y][x], Room):
                    if not self.count_neighbours(cursor_y, x) > 1:
                        self._map[cursor_y][x] = Room(LOADER, self.floor, start=False)
                        self.set_rooms += 1
                        self.generate_next_room(cursor_y, x)
        return

    def count_neighbours(self, cursor_y, cursor_x):
        neighbours = 0
        if cursor_y > 0:
            if isinstance(self._map[cursor_y - 1][cursor_x], Room):
                neighbours += 1
        if cursor_y < MAX_HEIGHT - 1:
            if isinstance(self._map[cursor_y + 1][cursor_x], Room):
                neighbours += 1
        if cursor_x > 0:
            if isinstance(self._map[cursor_y][cursor_x - 1], Room):
                neighbours += 1
        if cursor_x < MAX_WIDTH - 1:
            if isinstance(self._map[cursor_y][cursor_x + 1], Room):
                neighbours += 1
        return neighbours