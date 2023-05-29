import pygame
from os import walk
from os.path import join
from engine.bullet import Bullet
from engine.tiles.tile import Tile
from engine.tiles.flame import Flame
from engine.tiles.door import Door, TrapDoor
from engine.tiles.monsters.eye import Eye, Eye2
from engine.tiles.monsters.monster import Monster
from engine.player import Player
from engine.map import Map
from engine.tiles.items import pick_item
from time import sleep

class PygameHandler:
    def __init__(self, display_width, display_height, player, _map):
        pygame.init()
        self.width = 960
        self.height = 832
#        self.display = pygame.display.set_mode((width, height))
        self.display_width = display_width
        self.display_height = display_height
        ### Resolution change test
        self.real_display = pygame.display.set_mode((display_width, display_height))
        self.display = pygame.Surface((self.width, self.height))

        pygame.display.set_caption('PycoRogue')
        self.clock = pygame.time.Clock()
        self.resources = {}
        self.load_resources()
        self.player = player
        self.hostile_bullets = []
        self.time_since_last_bullet = 100
        self._map = _map
        self.known_rooms = {}
        self.tiles = []
        self.level = 1
        self.room = None
        return

    def handle_event(self):
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)

        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            exit(0)

        if keys[pygame.K_r]:
            self.reset()
            sleep(0.3)
            return

        self.move_player(keys)
        


    def move_player(self, keys):
        if self.player.lives < 1:
            return
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
                    bullet = Bullet(self.player.x, self.player.y, bullet_vec_x, bullet_vec_y, is_player=True, speed=self.player.bullets_speed, damage = self.player.damage, lifespan=self.player.bullets_lifespan)
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


    def draw_map(self):
        gray = self.resources['gray_square_map.png']
        white = self.resources['white_square_map.png']
        white_x = self.resources['white_square_map_x.png']

        for y in range(0, self._map.height):
            for x in range(0, self._map.width):
                room = self._map.get_room(y, x)
                if room:
                    res = gray if room.id not in self.known_rooms.keys() else white
                    if y == self._map.cursor[0] and x == self._map.cursor[1]:
                        res = white_x
                        self.room = room
                    if room.special:
                        if room.special == "💀":
                            res = res.copy()
                            res.blit(self.resources['skull_map.png'], (0, 0))
                    self.display.blit(res, ((self.width - 300) + ((res.get_width() - 2) * x), 30 + ((res.get_height() - 2) * y)))
        return

    def draw_tiles(self):
            self.display.blit(self.resources['bg1.png'], (0, 0))
            tile_width = self.resources['room_wall_top_right.png'].get_width()
            step_x = tile_width
            step_y = tile_width
            room = self._map.get_current_room()

            if room.id in self.known_rooms.keys():
                self.tiles = self.known_rooms[room.id]
            else:
                self.known_rooms[room.id] = []
                self.tiles = []

            if len(self.tiles) > 0:
                for tile in self.tiles:
                    if tile.destroyed:
                        tile.after_destroyed(self)
                        self.tiles.remove(tile)
                    else:
                        self.display.blit(tile.res, (tile.x, tile.y))
                return
            for i in range(0, room.height):
                for j in range(0, room.width):
                    tile = room.get_tile(i, j)
                        
                    if tile == "S" and self.player.x == 0 and self.player.y == 0:
                        self.player.x = (j * tile_width) + step_x
                        self.player.y = (i * tile_width) + step_y
                        self.player.collide = True
                    elif tile == "F":
                        tile = Flame((tile_width * j) + step_x, (tile_width * i) + step_y, 1, self.resources['fire.png'], collide=True)
                        self.tiles.append(tile)
                    elif tile == "E":
                        tile = Eye((tile_width * j) + step_x, (tile_width * i) + step_y, level=self.level)
                        self.tiles.append(tile)
                    elif tile == "2":
                        tile = Eye2((tile_width * j) + step_x, (tile_width * i) + step_y, level=self.level)
                        self.tiles.append(tile)
                    elif tile == "I":
                        tile = pick_item((tile_width * j) + step_x, (tile_width * i) + step_y)
                        self.tiles.append(tile)
                    if room.door_up:
                        tile = Door((self.width / 2) - (tile_width / 2), (tile_width * 0.2), "UP", is_open=room.start)
                        self.tiles.append(tile)
                    
                    if room.door_down:
                        tile = Door((self.width / 2) - (tile_width / 2), (self.height - tile_width - (tile_width * 0.2)), "DOWN", is_open=room.start)
                        self.tiles.append(tile)

                    if room.door_left:
                        tile = Door(tile_width * 0.2, (self.height / 2 - (tile_width / 2)), "LEFT", is_open=room.start)
                        self.tiles.append(tile)

                    if room.door_right:
                        tile = Door(self.width - tile_width - tile_width * 0.2, (self.height / 2 - (tile_width / 2)), "RIGHT", is_open=room.start)
                        self.tiles.append(tile)

                    self.known_rooms[room.id] = self.tiles
    
    def draw_hud(self):
        tile_width = self.resources["life.png"].get_width()
        for i in range(0, self.player.max_lives):
            if i < self.player.lives:
                self.display.blit(self.resources["life.png"], (tile_width * 1.2 * (i + 1), tile_width / 2))
            else:
                self.display.blit(self.resources["life_empty.png"], (tile_width * 1.2 * (i + 1), tile_width / 2))

    def draw_player(self):
        if self.player.time_since_last_damage < self.player.invulnerability_frames:
            self.player.rect = self.display.blit(self.resources['player_inv.png'], (self.player.x, self.player.y))
        else:
            self.player.rect = self.display.blit(self.resources['player.png'], (self.player.x, self.player.y))

    def draw(self):
        self.draw_tiles()
        self.draw_player()
        self.draw_bullets()
        self.draw_hud()
        self.draw_map()

        # Scaling
        scaled = pygame.transform.scale(self.display, (self.width, self.height))
        step = 0
        if self.display_height < self.height:
            scale_ratio = self.height / self.display_height    
            game_ratio = self.height / self.width
            scaled = pygame.transform.scale(self.display, (self.display_width * game_ratio, self.display_height))

        if self.display_width > self.display_width * game_ratio:
            step = (self.display_width - (self.display_width * game_ratio)) / 2
        self.real_display.fill((255, 255, 255))
        self.real_display.blit(scaled, (step, 0))
        pygame.display.update()

    def handle_collisions(self):
        self.handle_player_collisions()
        self.handle_bullets_collision()
        return

    def handle_player_collisions(self):
        for tile in self.tiles:
            if not self.player.collide:
                return
            tile_rect = pygame.Rect((tile.x, tile.y), (tile.width, tile.width))
            if tile.collide and tile_rect.colliderect(self.player.rect):
                tile.collide_player(self.player, self._map)
                if tile.damage:
                    self.player.hit(tile.damage)

                if isinstance(tile, TrapDoor):
                    self.level += 1
                    self.reset(keep_player=True)
                    sleep(0.3)
                    return

                if isinstance(tile, Door) and tile.is_open:
                    print(self._map.cursor)
                    if tile.door_up:
                        self._map.move(self._map.cursor[0] - 1, self._map.cursor[1])
                        self.player.x = tile.x
                        self.player.y = self.height - tile.y - (tile.res.get_width() * 2)
                    if tile.door_down:
                        self._map.move(self._map.cursor[0] + 1, self._map.cursor[1])
                        self.player.x = tile.x
                        self.player.y = self.height - tile.y
                    if tile.door_left:
                        self._map.move(self._map.cursor[0], self._map.cursor[1] - 1)
                        self.player.x = self.width - tile.x - (tile.res.get_width() * 2)
                        self.player.y = tile.y
                    if tile.door_right:
                        self._map.move(self._map.cursor[0], self._map.cursor[1] + 1)
                        self.player.x = self.width - tile.x
                        self.player.y = tile.y

                    self.tiles = []
                    self.player.bullets = []
                    self.hostile_bullets = []
                    self.player.collide = True
                    sleep(0.2) # TODO replace w/ an animation
                    return

        self.player.time_since_last_damage += 1
        return

    def reset(self, keep_player=False):
        if not keep_player:
            self.player = Player()
            self.level = 1
        self.hostile_bullets = []
        self.time_since_last_bullet = 100
        self.tiles = []
        self.known_rooms = {}
        self._map = Map(self.player, self.level)
        return

    def handle_bullets_collision(self):
        for bullet in self.player.bullets + self.hostile_bullets:
            for tile in self.tiles:
                tile_rect = pygame.Rect((tile.x, tile.y), (tile.width, tile.width))
                if tile.collide and tile_rect.colliderect(bullet.rect):
                    if bullet in self.player.bullets:
                        if tile.block_bullets:
                            self.player.bullets.remove(bullet)
                        tile.hit(self.player.damage)
        for bullet in self.hostile_bullets:
            if bullet.rect.colliderect(self.player.rect):
                self.player.hit(bullet.damage)


    def handle_ennemies(self):
        monsters = 0
        for tile in self.tiles:
            if isinstance(tile, Monster):
                tile.play(self)
                monsters += 1
        if monsters == 0:
            if self.room and self.room.special == "💀":
                has_trapdoor = False
                for tile in self.tiles:
                    if isinstance(tile, TrapDoor):
                        has_trapdoor = True
                if not has_trapdoor:
                    tile = TrapDoor(400, 400)
                    self.tiles.append(tile)
            for tile in self.tiles:
                if isinstance(tile, Door) and not tile.is_open:
                    tile.open()
        return
