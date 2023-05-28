import pygame
from os import walk
from os.path import join

class PygameHandler:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.display = pygame.display.set_mode((width, height))
        pygame.display.set_caption('PycoRogue')
        self.resources = {}
        self.load_resources()
        self.player = {"x": 0, "y": 0, "speed": 10}
        return

    def handle_event(self, map):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
         
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    self.player["x"] += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.player["speed"]
                    self.player["y"] += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.player["speed"]

    def load_resources(self):
        for root, dirs, files in walk(join("resources", "textures")):
            for filename in files:
                if filename.endswith('.png'):
                    self.resources[filename] = pygame.image.load(join("resources", "textures", filename)).convert_alpha()
        print(self.resources)

    def display_map(self, map):
        gray = self.resources['gray_square_map.png']
        white = self.resources['white_square_map.png']


        for i in range(0, map.height):
            for j in range(0, map.width):
                room = map.get_room(j, i)
                if room:
                    res = gray
                    if i == map.cursor[0] and j == map.cursor[1]:
                        res = white
                    if room.special:
                        print(room.special)
                        if room.special == "💀":
                            res = res.copy()
                            res.blit(self.resources['skull_map.png'], (0, 0))
                    self.display.blit(res, ((self.width - 300) + ((res.get_width() - 2) * i), 30 + ((res.get_height() - 2) * j)))
        return

    def display_tiles(self, map):
            self.display.fill([255, 255, 255])
            tile_width = self.resources['room_wall_top_right.png'].get_width()
            step_x = tile_width
            step_y = tile_width
            room = map.get_current_room()

            # Putting top/bottom diagonal tiles
            self.display.blit(self.resources['room_wall_top_left.png'], (0, 0))
            self.display.blit(self.resources['room_wall_top_right.png'], (self.width - tile_width, 0))
            self.display.blit(self.resources['room_wall_top_right.png'], (0, self.height - tile_width))
            self.display.blit(self.resources['room_wall_top_left.png'], (self.width - tile_width, self.height - tile_width))

            # Putting walls
            print('Room width, height', room.width, room.height)
            for i in range(0, room.height):
                if i != 0:
                    res_left = self.resources['room_wall_left.png']
                    res_right = self.resources['room_wall_right.png']
                    self.display.blit(res_left, (0, res_left.get_height() * i))
                    self.display.blit(res_right, (self.width - res_left.get_width(), res_left.get_height() * i))
                for j in range(0, room.width):
                    if j != 0:
                        self.display.blit(self.resources['room_wall_top.png'], ((tile_width * j), 0))
                        self.display.blit(self.resources['room_wall_bottom.png'], (tile_width * j, self.height - tile_width))

                    tile = room.get_tile(i, j)
                        
                    res = self.resources['tile.png'].copy()
                    if tile == "S" and self.player["x"] == 0 and self.player["y"] == 0:
                        self.player["x"] = (j * tile_width) + step_x
                        self.player["y"] = (i * tile_width) + step_y
                    elif tile == "F":
                        res.blit(self.resources['fire.png'], (0, 0))
                    self.display.blit(res, (((tile_width * j) + step_x, (tile_width * i) + step_y)))
            self.display.blit(self.resources['room_wall_bottom.png'], (self.width - tile_width * 2, self.height - tile_width))
            self.display.blit(self.resources['room_wall_bottom.png'], (self.width - tile_width * 2, self.height - tile_width))
    
    def display_player(self):
        self.display.blit(self.resources['player.png'], (self.player['x'], self.player['y']))

    def draw(self):
            pygame.display.flip()
            
