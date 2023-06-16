import pygame
from os import walk
from os.path import join
from math import hypot
from engine.bullet import Bullet
from engine.tiles.door import Door, TrapDoor
from engine.tiles.monsters.monster import Monster
from resources.loader import load_resources
from engine.player import Player
from engine.map import Map
from engine.tools import move_towards, convert_pos_screen_game, distance
from engine.animation import Animation
from engine.tiles.loader import load_tiles
from pygame.locals import *
from display.renderer import Renderer
from time import sleep

class PygameHandler:
    def __init__(self, display_width, display_height, player, _map, fps):
        pygame.init()
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

        self.width = 960
        self.height = 832
        #
        # self.width = (14 + 2) * 64 # 11 tiles + 2 for the border
        # self.height = (11 + 2) * 64 # 14 tiles + 2 for the border
        #
        self.display_width = display_width
        self.display_height = display_height
        self.real_display = pygame.display.set_mode((display_width,  display_height), FULLSCREEN, 16, 0, 1)
        self.display = pygame.Surface((self.width, self.height))
        self.display_rect = None
        self.renderer = Renderer(self.display, self.real_display,  self.display_width, self.display_height, self.width, self.height)
        self.fps = fps
        #
        pygame.display.set_caption('PycoRogue')
        self.clock = pygame.time.Clock()
        self.resources = load_resources()
        self.player = player
        self.hostile_bullets = []
        self.time_since_last_bullet = 100
        self._map = _map
        self.known_rooms = {}
        self.tiles = []
        self.level = 1
        self.room = None
        self.mouse = False
        self.mouse_pressed = False
        self.keys_timers = {}
        # Purely display related
        self.background_color = None
        self.displayed_res = []
        self.displayed_last_frame = []
        self.pos_to_update = []
        self.to_update = []
        self.to_update_real = []
        # Map
        self.display_map = True
        self.map = None
        self.map_data = {}
        # HUD
        self.hud = None
        self.hud_data = {}
        # Stats
        self.display_stats = False
        self.stats_data = {}
        self.stats = None
        self.cache = {}
        return

    def blit(self, res, pos, display="game"):
        rect = Rect(pos[0], pos[1], res.get_width(), res.get_height())
        if (pos[0], pos[1], res, rect) not in self.displayed_res:
            self.displayed_res.append((pos[0], pos[1], res, rect, display))
            self.future_blit(pos[0], pos[1], res, display)
        return rect

    def future_blit(self, x, y, res, display="game"):
        rect = Rect(x, y, res.get_width(), res.get_height())
        if display == "game":
            self.to_update.append((x, y, res, rect))
        elif display == "real":
            self.to_update_real.append((x, y, res, rect))
        return rect

    def handle_event(self):
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse = True
                self.mouse_pressed = True
            if event.type == pygame.MOUSEBUTTONUP:
                self.mouse_pressed = False

            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            exit(0)

        if keys[pygame.K_r]:
            if not self.keys_timers.get(pygame.K_r) or self.keys_timers.get(pygame.K_r) <= 0:
                self.reset()
                sleep(0.3)
            self.keys_timers[pygame.K_r] = self.clock.get_fps() * 0.5 # 0.5 seconds
            return
        
        if keys[pygame.K_TAB]:
            if not self.keys_timers.get(pygame.K_TAB) or self.keys_timers.get(pygame.K_TAB) <= 0:
                self.display_map = not self.display_map
                self.hud = None
            self.keys_timers[pygame.K_TAB] = self.clock.get_fps() * 0.25 # 0.25 seconds
        
        if keys[pygame.K_p]:
            if not self.keys_timers.get(pygame.K_p) or self.keys_timers.get(pygame.K_p) <= 0:
                self.display_stats = not self.display_stats
            self.keys_timers[pygame.K_p] = self.clock.get_fps() * 0.25

        for timer in self.keys_timers.keys():
            if self.keys_timers[timer] > 0:
                self.keys_timers[timer] -= 1

        self.move_player(keys)
        

    def move_player(self, keys):
        if self.player.lives < 1:
            return
        # Movement
        tile_width = self.resources['room_wall_top_right.png'].get_width()
        shot = False



        if keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]:
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.player.orientation = "right"
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.player.orientation = "left"
            self.player.is_moving = True
        else:
            self.player.is_moving = False

        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            self.player.orientation = "right" if keys[pygame.K_RIGHT] else "left"

        new_x = self.player.x + (keys[pygame.K_d] - keys[pygame.K_a]) * self.player.speed
        new_y = self.player.y + (keys[pygame.K_s] - keys[pygame.K_w]) * self.player.speed
        self.player.x = new_x
        self.player.y = new_y
        # if new_x > tile_width and new_x + tile_width < (self.width - tile_width):
        #     self.player.x = new_x
        # if new_y > tile_width and new_y + tile_width < (self.height - tile_width):
        #     self.player.y = new_y

        # Bullet shots

        if (keys[pygame.K_UP] or keys[pygame.K_DOWN] \
            or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) \
                and self.time_since_last_bullet > self.player.bullets_delay:
                    bullet_vec_x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 11 # DEBUG static speed
                    bullet_vec_y = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * 11 # DEBUG static speed
                    bullet = Bullet(self.player.x + 25, self.player.y + 16, bullet_vec_x, bullet_vec_y, is_player=True, speed=self.player.bullets_speed, damage = self.player.damage, lifespan=self.player.bullets_lifespan)
                    self.player.bullets.append(bullet)
                    shot = True
        elif (keys[pygame.K_o] or keys[pygame.K_k] \
            or keys[pygame.K_l] or keys[pygame.K_SEMICOLON]) \
                and self.time_since_last_bullet > self.player.bullets_delay:
                    bullet_vec_x = (keys[pygame.K_SEMICOLON] - keys[pygame.K_k]) * 11 # DEBUG static speed
                    bullet_vec_y = (keys[pygame.K_l] - keys[pygame.K_o]) * 11 # DEBUG static speed
                    bullet = Bullet(self.player.x + 25, self.player.y + 16, bullet_vec_x, bullet_vec_y, is_player=True, speed=self.player.bullets_speed, damage = self.player.damage, lifespan=self.player.bullets_lifespan)
                    self.player.bullets.append(bullet)
                    shot = True
        # Autoshoot with mouse click
        if self.mouse_pressed:
            pos = pygame.mouse.get_pos()
            # pos = convert_pos_screen_game(self, pos)
            # self.blit(self.resources['crosshair.png'], (pos[0] - 16, pos[1] - 16))
            print('self.resources[crosshair.png]', self.resources['crosshair.png'])
            self.renderer.future_render(self.resources['crosshair.png'], (pos[0] - 16, pos[1] - 16), "crosshair", real_screen=True, force_redraw=False, weight=4)
            # move_towards(self.player, pos[0], pos[1])
            # print(self.time_since_last_bullet, self.player.bullets_delay)
            # if self.time_since_last_bullet > self.player.bullets_delay:
            #     closest = None
            #     lowest_distance = 1000
            #     for tile in self.tiles:
            #         if isinstance(tile, Monster):
            #             monster_dist = distance(self.player, tile)
            #             if monster_dist < lowest_distance:
            #                 lowest_distance = monster_dist
            #                 closest = tile
            #     if closest: # If there is a monster close to us
            #         dx, dy = closest.x - self.player.x, closest.y - self.player.y
            #         dist = hypot(dx, dy)
            #         dx, dy = dx / dist, dy / dist
            #         bullet = Bullet(self.player.x, self.player.y, dx * 11, dy * 11, is_player=True, speed=self.player.bullets_speed, damage = self.player.damage, lifespan=self.player.bullets_lifespan)
            #         self.player.bullets.append(bullet)
            #         shot = True
        else:
            self.renderer.remove("crosshair")

        if not shot:
            self.time_since_last_bullet += 1
        else:
            self.time_since_last_bullet = 0

    def draw_bullets(self):
        for bullet in self.player.bullets + self.hostile_bullets:
            bullet.age += 1
            next_x = bullet.x + bullet.vec_x
            next_y = bullet.y + bullet.vec_y
            bullet.x = next_x
            bullet.y = next_y
            if bullet.age > bullet.lifespan:
                if bullet in self.player.bullets:
                    self.player.bullets.remove(bullet)
                elif bullet in self.hostile_bullets:
                    self.hostile_bullets.remove(bullet)
                self.renderer.remove(bullet.id)

            bullet.rect = self.renderer.future_render(bullet.res, (next_x, next_y), bullet.id, real_screen=False, force_redraw=False, weight=2)


    def draw_map(self):
        step = 5

        if self.map_data.get('room_id') == self._map.get_current_room().id and self.map:
            self.blit(self.map, (self.display_width - self.map.get_width() - (step * self._map.width), 0), "real")
            return

        gray = self.resources['gray_square_map.png']
        white = self.resources['white_square_map.png']
        white_x = self.resources['white_square_map_x.png']

        self.map = pygame.Surface((self._map.width * gray.get_width() +  (step * self._map.width), self._map.height * gray.get_width() +  (step * self._map.height)), pygame.SRCALPHA)

        self.map_data['room_id'] = self._map.get_current_room().id

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
                    print('x', res.get_width() * x)
                    print('y', res.get_height() * y)
                    self.map.blit(res, (((res.get_width() + step) * x), ((res.get_height() + step) * y)))
        self.blit(self.map, (self.display_width - self.map.get_width(), 0), "real")
        return

    def draw_tiles(self):
            self.renderer.future_render(self.resources['bg1.png'], (0, 0), "background", real_screen=False, force_redraw=False, weight=1)
            return 
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
                        self.blit(tile.res, (tile.x, tile.y))
                return
            else:
                load_tiles(self)

            self.known_rooms[room.id] = self.tiles

    def draw_lives(self):
        if self.hud_data.get('lives') == self.player.lives and self.cache.get('lives'):
            self.renderer.future_render(self.cache['lives'], (32, 32), "lives")
            return
        
        tile_width = self.resources["life.png"].get_width()
        lives = pygame.Surface(((tile_width * 1.2) * self.player.lives, tile_width * 2), pygame.SRCALPHA)
        self.hud_data['lives'] = self.player.lives

        for i in range(0, self.player.max_lives):
            if i < self.player.lives:
                lives.blit(self.resources["life.png"], (tile_width * 1.2 * (i + 1), tile_width / 2))
            else:
                lives.blit(self.resources["life_empty.png"], (tile_width * 1.2 * (i + 1), tile_width / 2))
        self.cache['lives'] = lives
        self.renderer.future_render(lives, (32, 32), "lives")
    
    def draw_hud(self):

        # We only update the hud if its data has changed
        if self.hud_data.get('lives') == self.player.lives:
            if self.hud_data.get('coins') == self.player.coins:
                if self.hud_data.get('level') == self.level and self.hud:
                    self.renderer.future_render(self.hud, (0, 0), "hud")
                    # self.blit(self.hud, (0, 0), "real") 
                    return
        
        # self.hud = pygame.Surface((32 * , self.display_height), pygame.SRCALPHA)
        self.hud_data['lives'] = self.player.lives
        self.hud_data['coins'] = self.player.coins
        self.hud_data['level'] = self.level
        # Draw lives
     
        # Draw coins
        coins_text = self.resources["PressStart2P-Regular.ttf"].render("{:02d}".format(self.player.coins), True, (255,255,255))
        self.hud.blit(self.resources['coin.png'], (32, 100))
        self.hud.blit(coins_text, (32 + 64, 108))
        #
        if self.display_map:
            level_text = self.resources["PressStart2P-Regular.ttf"].render("Level {}".format(self.level), True, (255,255,255))
            self.hud.blit(level_text, ((self.display_width / 2) - level_text.get_width() / 2, self.display_height - 128))
        self.renderer.future_render(self.hud, (0, 0), "hud")
        
        # self.blit(self.hud, (0, 0), "real")

    def draw_player(self):
        if self.player.animation_left is None:
            self.player.animation_left = Animation('player_tileset_left.png', 2, fps=60, tile_length=64, width=2, height=1, duration=0.25)
            self.player.animation_right = Animation('player_tileset_right.png', 2, fps=60, tile_length=64, width=2, height=1, duration=0.25)
        
        player_res = self.resources['player_right.png'] if self.player.orientation == 'right' else self.resources['player_left.png']
        if self.player.is_moving:
            if self.player.orientation == 'left':
                player_res = self.player.animation_left.get_next_frame()
            elif self.player.orientation == 'right':
                player_res = self.player.animation_right.get_next_frame()
    
        if self.player.time_since_last_damage < self.player.invulnerability_frames:
            player_res.set_alpha(128)
        else:
            player_res.set_alpha(255)
            # self.player.rect = self.display.blit(self.resources['player_inv.png'], (self.player.x, self.player.y))
        # else:
        self.renderer.future_render(player_res, (self.player.x, self.player.y), "player", real_screen=False, force_redraw=False, weight=3)
        # self.player.rect = self.display.blit(player_res, (self.player.x, self.player.y))

    def draw_stats(self):
        # We only update the stats if its data has changed
        # if self.stats_data.get('speed') == self.player.speed:
        #     if self.stats_data.get('bullets_delay') == self.player.bullets_delay:
        #         if self.stats_data.get('bullets_lifespan') == self.player.bullets_lifespan:
        #             if self.stats_data.get('bullets_speed') == self.player.bullets_speed:
        #                 if self.stats_data.get('invulnerability_frames') == self.player.invulnerability_frames:
        #                     if self.stats_data.get('damage') == self.player.damage:
        #                         if self.stats_data.get('fps') == int(self.clock.get_fps()):
        #                             self.renderer.future_render(self.stats, (40, 200), "stats")
        #                             return
        
        step_x = 30 # pixels
        step_y = 200 # pixels


        self.stats_data['bullets_lifespan'] = self.player.bullets_lifespan
        self.stats_data['bullets_speed'] = self.player.bullets_speed
        self.stats_data['invulnerability_frames'] = self.player.invulnerability_frames
        self.stats_data['damage'] = self.player.damage
        self.stats_data['fps'] = int(self.clock.get_fps())

        bullets_delay_text = self.resources["PressStart2P-Regular.ttf"].render("blt delay : {}".format(self.player.bullets_delay), True, (255,255,255))
        bullets_lifespan_text = self.resources["PressStart2P-Regular.ttf"].render("blt durat*: {}".format(self.player.bullets_lifespan), True, (255,255,255))
        bullets_speed_text = self.resources["PressStart2P-Regular.ttf"].render("blt speed : {}".format(self.player.bullets_speed), True, (255,255,255))
        invulnerability_frames_text = self.resources["PressStart2P-Regular.ttf"].render("Inv frames: {}".format(self.player.invulnerability_frames), True, (255,255,255))
        damage_text = self.resources["PressStart2P-Regular.ttf"].render("Damage    : {}".format(self.player.damage), True, (255,255,255))
        fps_text = self.resources["PressStart2P-Regular.ttf"].render("FPS       : {}".format(int(self.clock.get_fps())), True, (255,255,255))

        # Player stats
        print(self.player.speed, self.stats_data.get('speed'), self.player.speed != self.stats_data.get('speed'))
        if self.player.speed != self.stats_data.get('speed'):
            speed_text = self.resources["PressStart2P-Regular.ttf"].render("Speed     : {}".format(self.player.speed), True, (255,255,255))
            self.renderer.future_render(speed_text, (step_x, step_y), "stats_speed")
            self.cache['stats_speed_text'] = speed_text
            self.stats_data['speed'] = self.player.speed
        else:
            self.renderer.future_render(self.cache['stats_speed_text'], (step_x, step_y), "stats_speed")

        if self.player.bullets_delay != self.stats_data.get('bullets_delay'):
            bullets_delay_text = self.resources["PressStart2P-Regular.ttf"].render("blt delay : {}".format(self.player.bullets_delay), True, (255,255,255))
            self.renderer.future_render(bullets_delay_text, (step_x, step_y + 32 * 2), "stats_bullets_delay")
            self.cache['stats_bullets_delay_text'] = bullets_delay_text
            self.stats_data['bullets_delay'] = self.player.bullets_delay
        else:
            self.renderer.future_render(self.cache['stats_bullets_delay_text'], (step_x, step_y + 32 * 2), "stats_bullets_delay")
        return

    def draw(self):
        if self.background_color is None:
            self.background_color = pygame.Surface((self.renderer.step_x, self.display_height))
            self.background_color.fill((15, 31, 43))
        self.renderer.future_render(self.background_color, (0, 0), "background_color", real_screen=True, force_redraw=False, weight=0)
        self.draw_tiles()
        self.draw_player()
        self.draw_bullets()
        if self.display_stats:
            self.draw_stats()
        self.draw_lives()
        # self.draw_hud()
        self.renderer.render_cycle()
        pass
        
        # self.draw_tiles()
        # self.draw_player()

        # for to_draw in self.displayed_res:
        #     if to_draw[4] == 'game':
        #         if to_draw not in self.displayed_last_frame:
        #             self.display.blit(to_draw[2], (to_draw[0], to_draw[1]))

        # # Scaling
        # scaled = pygame.transform.scale(self.display, (self.width, self.height))
        # step = 0
        # game_ratio = self.height / self.width

        # if self.display_height < self.height:
        #     scaled = pygame.transform.scale(self.display, (self.display_width * game_ratio, self.display_height))

        # if self.display_width > self.width:
        #     step = (self.display_width - self.width) / 2
        # else:
        #     step = (self.display_width - (self.display_height / game_ratio)) / 2

        # # Actual drawing
        # self.real_display.fill((15, 31, 43))


        # self.display_rect = self.blit(scaled, (step, 0), "real")


        # if self.display_map:
        #     self.draw_map()
        # if self.display_stats:
        #     self.draw_stats()

        # print("LEN SELF.DISPLAYED_RES", len(self.displayed_res))

        # for to_draw in self.displayed_res:
        #     if to_draw[4] == 'real':
        #         if to_draw not in self.displayed_last_frame:
        #             self.real_display.blit(to_draw[2], (to_draw[0], to_draw[1]))


        
        # # self.real_display.blit(self.display, (0, 0))

        # for to_update in self.to_update_real:
        #     print('to_update', to_update)
        #     pygame.display.update(to_update[3])
        #     # self.to_update.remove(to_update)
        # # pygame.display.update(game)

        # self.displayed_last_frame = self.displayed_res
        # self.displayed_res = []
        # self.to_update = []
        # self.to_update_real = []
        # pygame.display.update()


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
                    tile = TrapDoor((self.width / 2) - 32, (self.height /2) - 32)
                    self.tiles.append(tile)
            for tile in self.tiles:
                if isinstance(tile, Door) and not tile.is_open:
                    tile.open()
        return
