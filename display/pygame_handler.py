import pygame
from os import walk
from os.path import join
from engine.bullet import Bullet

class PygameHandler:
    def __init__(self, width, height):
        pygame.init()
        self.width = width
        self.height = height
        self.display = pygame.display.set_mode((width, height))
        pygame.display.set_caption('PycoRogue')
        self.clock = pygame.time.Clock()
        self.resources = {}
        self.load_resources()
        self.player = {"x": 0, "y": 0, "speed": 5, "bullets": [], "bullets_delay": 30}
        self.time_since_last_bullet = 0
        return

    def handle_event(self, map):
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
         
        keys = pygame.key.get_pressed()
        self.move_player(map, keys)

    def move_player(self, map, keys):
        # Movement
        tile_width = self.resources['room_wall_top_right.png'].get_width()

        new_x = self.player["x"] + (keys[pygame.K_d] - keys[pygame.K_a]) * self.player["speed"]
        new_y = self.player["y"] + (keys[pygame.K_s] - keys[pygame.K_w]) * self.player["speed"]
        if new_x > tile_width and new_x + tile_width < (self.width - tile_width):
            self.player["x"] = new_x
        if new_y > tile_width and new_y + tile_width < (self.height - tile_width):
            self.player["y"] = new_y

        # Bullet shots
        if (keys[pygame.K_UP] or keys[pygame.K_DOWN] \
            or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) \
                and self.time_since_last_bullet > self.player["bullets_delay"]:
                    print(self.time_since_last_bullet, print(self.player["bullets_delay"]))
                    bullet_vec_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 11 # DEBUG static speed
                    bullet_vec_y = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * 11 # DEBUG static speed
                    bullet = Bullet(self.player["x"], self.player["y"], bullet_vec_x, bullet_vec_y)
                    self.player["bullets"].append(bullet)
                    self.time_since_last_bullet = 0
        else:
            self.time_since_last_bullet += 1

    def load_resources(self):
        for root, dirs, files in walk(join("resources", "textures")):
            for filename in files:
                if filename.endswith('.png'):
                    self.resources[filename] = pygame.image.load(join("resources", "textures", filename)).convert_alpha()
        print(self.resources)

    def display_bullets(self):
        res = self.resources["bullet.png"]
        print(self.player)
        print(self.player["bullets"])
        for bullet in self.player["bullets"]:
            bullet.age += 1
            if bullet.age > bullet.lifespan:
                self.player["bullets"].remove(bullet)
            next_x = bullet.x + bullet.vec_x
            next_y = bullet.y + bullet.vec_y
            print(bullet.x, next_x, bullet.y, next_y, bullet.vec_x, bullet.vec_y)
            self.display.blit(res, (next_x, next_y))
            bullet.x = next_x
            bullet.y = next_y
            


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

            for i in range(0, room.height):
                for j in range(0, room.width):
                    tile = room.get_tile(i, j)
                        
                    res = self.resources['tile.png'].copy()
                    if tile == "S" and self.player["x"] == 0 and self.player["y"] == 0:
                        self.player["x"] = (j * tile_width) + step_x
                        self.player["y"] = (i * tile_width) + step_y
                    elif tile == "F":
                        res.blit(self.resources['fire.png'], (0, 0))
                    self.display.blit(res, (((tile_width * j) + step_x, (tile_width * i) + step_y)))
    
    def display_walls(self):
            tile_width = self.resources['room_wall_top_right.png'].get_width()
            self.display.blit(self.resources['room_wall_top_left.png'], (0, 0))
            self.display.blit(self.resources['room_wall_top_right.png'], (self.width - tile_width, 0))
            self.display.blit(self.resources['room_wall_top_right.png'], (0, self.height - tile_width))
            self.display.blit(self.resources['room_wall_top_left.png'], (self.width - tile_width, self.height - tile_width))



    def display_player(self):
        self.display.blit(self.resources['player.png'], (self.player['x'], self.player['y']))

    def draw(self):
            pygame.display.flip()
            
