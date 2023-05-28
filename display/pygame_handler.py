import pygame
from os import walk
from os.path import join
from engine.bullet import Bullet
from engine.tiles.tile import Tile
from engine.tiles.flame import Flame
from engine.tiles.door import Door
from engine.tiles.monsters.eye import Eye
from engine.tiles.monsters.monster import Monster
from time import sleep

class PygameHandler:
    def __init__(self, width, height, player):
        pygame.init()
        self.width = width
        self.height = height
        self.display = pygame.display.set_mode((width, height))
        pygame.display.set_caption('PycoRogue')
        self.clock = pygame.time.Clock()
        self.resources = {}
        self.load_resources()
        self.player = player
        self.hostile_bullets = []
        self.time_since_last_bullet = 100
        self.tiles = []
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

        new_x = self.player.x + (keys[pygame.K_d] - keys[pygame.K_a]) * self.player.speed
        new_y = self.player.y + (keys[pygame.K_s] - keys[pygame.K_w]) * self.player.speed
        if new_x > tile_width and new_x + tile_width < (self.width - tile_width):
            self.player.x = new_x
        if new_y > tile_width and new_y + tile_width < (self.height - tile_width):
            self.player.y = new_y

        # Bullet shots
        if (keys[pygame.K_UP] or keys[pygame.K_DOWN] \
            or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) \
                and self.time_since_last_bullet > self.player.bullets_delay:
                    bullet_vec_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 11 # DEBUG static speed
                    bullet_vec_y = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * 11 # DEBUG static speed
                    bullet = Bullet(self.player.x, self.player.y, bullet_vec_x, bullet_vec_y)
                    self.player.bullets.append(bullet)
                    self.time_since_last_bullet = 0
        else:
            self.time_since_last_bullet += 1

    def load_resources(self):
        for root, dirs, files in walk(join("resources", "textures")):
            for filename in files:
                if filename.endswith('.png'):
                    self.resources[filename] = pygame.image.load(join("resources", "textures", filename)).convert_alpha()
        print(self.resources)

    def draw_bullets(self):
        for bullet in self.player.bullets + self.hostile_bullets:
            bullet.age += 1
            if bullet.age > bullet.lifespan:
                if bullet in self.player.bullets:
                    self.player.bullets.remove(bullet)
                elif bullet in self.hostile_bullets:
                    self.hostile_bullets.remove(bullet)
            next_x = bullet.x + bullet.vec_x
            next_y = bullet.y + bullet.vec_y
            bullet.rect = self.display.blit(bullet.res, (next_x, next_y))
            bullet.x = next_x
            bullet.y = next_y


    def draw_map(self, map):
        gray = self.resources['gray_square_map.png']
        white = self.resources['white_square_map.png']

        for y in range(0, map.height):
            for x in range(0, map.width):
                room = map.get_room(y, x)
                if room:
                    res = gray
                    if y == map.cursor[0] and x == map.cursor[1]:
                        res = white
                    if room.special:
                        if room.special == "💀":
                            res = res.copy()
                            res.blit(self.resources['skull_map.png'], (0, 0))
                    self.display.blit(res, ((self.width - 300) + ((res.get_width() - 2) * x), 30 + ((res.get_height() - 2) * y)))
        return

    def draw_tiles(self, map):
            self.display.fill([255, 255, 255])
            tile_width = self.resources['room_wall_top_right.png'].get_width()
            step_x = tile_width
            step_y = tile_width
            room = map.get_current_room()

            if len(self.tiles) > 0:
                for tile in self.tiles:
                    if tile.destroyed:
                        self.tiles.remove(tile)
                    else:
                        res = self.resources['tile.png'].copy()
                        self.display.blit(tile.res, (tile.x, tile.y))
                return
            for i in range(0, room.height):
                for j in range(0, room.width):
                    tile = room.get_tile(i, j)
                        
                    res = self.resources['tile.png'].copy()
                    if tile == "S" and self.player.x == 0 and self.player.y == 0:
                        self.player.x = (j * tile_width) + step_x
                        self.player.y = (i * tile_width) + step_y
                        self.player.collide = True
                    elif tile == "F":
                        res.blit(self.resources['fire.png'], (0, 0))
                        tile = Flame((tile_width * j) + step_x, (tile_width * i) + step_y, 1, self.resources['fire.png'], collide=True)
                        self.tiles.append(tile)
                    elif tile == "E":
                        tile = Eye((tile_width * j) + step_x, (tile_width * i) + step_y)
                        self.tiles.append(tile)

                    if room.door_up:
                        tile = Door((self.width / 2) - (tile_width / 2), (tile_width / 2), "UP", 0, self.resources['door.png'], collide=True)
                        self.display.blit(res, (tile.x, tile.y))
                        self.tiles.append(tile)
                    
                    if room.door_down:
                        tile = Door((self.width / 2) - (tile_width / 2), (self.height - tile_width - (tile_width / 2)), "DOWN", 0, self.resources['door.png'], collide=True)
                        self.display.blit(res, (tile.x, tile.y))
                        self.tiles.append(tile)

                    if room.door_left:
                        tile = Door(tile_width / 2, (self.height / 2 - (tile_width / 2)), "LEFT", 0, self.resources['door.png'], collide=True)
                        self.display.blit(res, (tile.x, tile.y))
                        self.tiles.append(tile)

                    if room.door_right:
                        tile = Door(self.width - tile_width - tile_width / 2, (self.height / 2 - (tile_width / 2)), "RIGHT", 0, self.resources['door.png'], collide=True)
                        self.display.blit(res, (tile.x, tile.y))
                        self.tiles.append(tile)

                    self.display.blit(res, (((tile_width * j) + step_x, (tile_width * i) + step_y)))
    
    def draw_hud(self, map):
        tile_width = self.resources["life.png"].get_width()
        for i in range(0, self.player.max_lives):
            if i < self.player.lives:
                self.display.blit(self.resources["life.png"], (tile_width * 1.1 * i, 0))
            else:
                self.display.blit(self.resources["life_empty.png"], (tile_width * 1.1 * i, 0))

    def draw_player(self):
        self.player.rect = self.display.blit(self.resources['player.png'], (self.player.x, self.player.y))

    def draw(self, map):
        self.draw_tiles(map)
        self.draw_player()
        self.draw_bullets()
        self.draw_hud(map)
        self.draw_map(map)
        pygame.display.flip()

    def handle_collisions(self, map):
        self.handle_player_collisions(map)
        self.handle_bullets_collision()
        return

    def handle_player_collisions(self, map):
        for tile in self.tiles:
            if not self.player.collide:
                return
            tile_rect = pygame.Rect((tile.x, tile.y), (tile.width, tile.width))
            if tile.collide and tile_rect.colliderect(self.player.rect):
                if tile.damage:
                    self.player.hit(tile.damage)

                if isinstance(tile, Door):
                    print(map.cursor)
                    if tile.door_up:
                        map.move(map.cursor[0] - 1, map.cursor[1])
                        self.player.x = tile.x
                        self.player.y = self.height - tile.y - (tile.res.get_width() * 2)
                    if tile.door_down:
                        map.move(map.cursor[0] + 1, map.cursor[1])
                        self.player.x = tile.x
                        self.player.y = self.height - tile.y
                    if tile.door_left:
                        map.move(map.cursor[0], map.cursor[1] - 1)
                        self.player.x = self.width - tile.x - (tile.res.get_width() * 2)
                        self.player.y = tile.y
                    if tile.door_right:
                        map.move(map.cursor[0], map.cursor[1] + 1)
                        self.player.x = self.width - tile.x
                        self.player.y = tile.y

                    self.tiles = []
                    self.player.bullets = []
                    self.player.collide = True
                    sleep(0.2) # TODO replace w/ an animation
                    return

        self.player.time_since_last_damage += 1
        return

    def handle_bullets_collision(self):
        for bullet in self.player.bullets:
            for tile in self.tiles:
                tile_rect = pygame.Rect((tile.x, tile.y), (tile.width, tile.width))
                if tile.collide and tile_rect.colliderect(bullet.rect):
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    tile.hit()
        for bullet in self.hostile_bullets:
            if bullet.rect.colliderect(self.player.rect):
                self.player.hit(bullet.damage)


    def handle_ennemies(self):
        for tile in self.tiles:
            if isinstance(tile, Monster):
                tile.play(self)
        return
