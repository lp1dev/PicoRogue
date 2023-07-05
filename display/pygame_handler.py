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
        self.current_room = None
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

    # def blit(self, res, pos, display="game"):
    #     rect = Rect(pos[0], pos[1], res.get_width(), res.get_height())
    #     if (pos[0], pos[1], res, rect) not in self.displayed_res:
    #         self.displayed_res.append((pos[0], pos[1], res, rect, display))
    #         self.future_blit(pos[0], pos[1], res, display)
    #     return rect

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
        shot = False
        tile_width = self.renderer.tile_width

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

        if keys[pygame.K_d] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_w]:
            new_x = self.player.x + (keys[pygame.K_d] - keys[pygame.K_a]) * self.player.speed
            new_y = self.player.y + (keys[pygame.K_s] - keys[pygame.K_w]) * self.player.speed
            if new_x > tile_width and new_x < self.renderer.game_width - (tile_width * 2):
                self.player.x = new_x
            if new_y > tile_width and new_y < self.renderer.game_height - (tile_width * 2):
                self.player.y = new_y

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
            # print('self.resources[crosshair.png]', self.resources['crosshair.png'])
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
                bullet.destroy(self)
                if bullet in self.player.bullets:
                    self.player.bullets.remove(bullet)
                elif bullet in self.hostile_bullets:
                    self.hostile_bullets.remove(bullet)
            else:
                bullet.rect = self.renderer.future_render(bullet.res, (next_x, next_y), bullet.id, real_screen=False, force_redraw=False, weight=3)


    def draw_map(self):
        step = 5

        if self.map_data.get('room_id') == self._map.get_current_room().id and self.map:
            self.renderer.future_render(self.map, (self.display_width - self.map.get_width() - (step * self._map.width), 0), "map", True)
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
                    self.map.blit(res, (((res.get_width() + step) * x), ((res.get_height() + step) * y)))
        self.renderer.future_render(self.map, (self.display_width - self.map.get_width() - (step * self._map.width), 0), "map", True)
        return

    def draw_tiles(self):
            self.renderer.future_render(self.resources['bg1.png'], (0, 0), "background", real_screen=False, force_redraw=False, weight=1)
            room = self._map.get_current_room()

            if self.current_room != room.id:
                self.renderer.remove_tiles()
                self.renderer.remove_bullets()
                pygame.display.update()

            if room.id in self.known_rooms.keys():
                self.current_room = room.id
                self.tiles = self.known_rooms[room.id]
            else:
                self.current_room = room.id
                self.known_rooms[room.id] = []
                self.tiles = []

            if len(self.tiles) > 0:
                for tile in self.tiles:
                    if tile.destroyed:
                        tile.after_destroyed(self)
                        self.tiles.remove(tile)
                        self.renderer.remove(tile.id)
                    else:
                        tile.rect = self.renderer.future_render(tile.res, (tile.x, tile.y), tile.id, real_screen=False, force_redraw=False, weight=2)
                return
            else:
                load_tiles(self)

            self.known_rooms[room.id] = self.tiles

    def draw_hud(self):
        self.draw_hud_lives()
        self.draw_hud_coins()

    def draw_hud_lives(self):
        if self.hud_data.get('lives') == self.player.lives and self.cache.get('lives'):
            self.renderer.future_render(self.cache['lives'], (32, 32), "lives")
            return
        
        tile_width = self.resources["life.png"].get_width()
        lives = None

        lives = pygame.Surface(((tile_width * 1.2) * (self.player.lives + 1), tile_width * self.player.max_lives), pygame.SRCALPHA)
        self.hud_data['lives'] = self.player.lives

        for i in range(0, self.player.max_lives):
            if i < self.player.lives:
                lives.blit(self.resources["life.png"], (tile_width * 1.2 * (i + 1), tile_width / 2))
            else:
                lives.blit(self.resources["life_empty.png"], (tile_width * 1.2 * (i + 1), tile_width / 2))
        self.cache['lives'] = lives
        self.renderer.future_render(lives, (32, 32), "lives", real_screen=True, force_redraw=True)
    
    def draw_hud_coins(self):
        if self.hud_data.get('coins') == self.player.coins and self.cache['coins']:
            self.renderer.future_render(self.cache['coins'], (0, 0), "hud_coins")
            return
        
        hud_coins = pygame.Surface((32 * 10, self.display_height), pygame.SRCALPHA)
        self.hud_data['coins'] = self.player.coins
     
        coins_text = self.resources["PressStart2P-Regular.ttf"].render("{:02d}".format(self.player.coins), True, (255,255,255))
        hud_coins.blit(self.resources['coin.png'], (32, 120))
        hud_coins.blit(coins_text, (32 + 64, 132))

        self.renderer.future_render(hud_coins, (0, 0), "coins_hud")
        self.cache['coins'] = hud_coins
        
    def draw_hud_level(self):
        if self.hud_data.get('level') == self.level and self.cache.get('level'):
            self.renderer.future_render(self.cache['level'], (self.display_width / 2 - 128, self.display_height - 64), "hud_level")
            return
        
        level_text = self.resources["PressStart2P-Regular.ttf"].render("Level {}".format(self.level), True, (255,255,255))
        hud_level = pygame.Surface((level_text.get_width(), level_text.get_height()), pygame.SRCALPHA)
        self.hud_data['level'] = self.level
        hud_level.blit(level_text, (0, 0))
        self.renderer.future_render(hud_level, (self.display_width / 2 - 128, self.display_height - 64), "hud_level")
        self.cache['level'] = hud_level
        return

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
        self.player.rect = self.renderer.future_render(player_res, (self.player.x, self.player.y), "player", real_screen=False, force_redraw=False, weight=3)
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
    
        if self.player.bullets_lifespan != self.stats_data.get('bullets_lifespan') or self.cache.get('stats_bullets_lifespan_text') is None:
            bullets_lifespan_text = self.resources["PressStart2P-Regular.ttf"].render("blt durat*: {}".format(self.player.bullets_lifespan), True, (255,255,255))
            self.renderer.future_render(bullets_lifespan_text, (step_x, step_y + 32 * 3), "stats_bullets_lifespan")
            self.cache['stats_bullets_lifespan_text'] = bullets_lifespan_text
            self.stats_data['bullets_lifespan'] = self.player.bullets_lifespan
        else:
            self.renderer.future_render(self.cache['stats_bullets_lifespan_text'], (step_x, step_y + 32 * 3), "stats_bullets_lifespan")

        if self.player.bullets_speed != self.stats_data.get('bullets_speed') or self.cache.get('stats_bullets_speed_text') is None:
            bullets_speed_text = self.resources["PressStart2P-Regular.ttf"].render("blt speed : {}".format(self.player.bullets_speed), True, (255,255,255))
            self.renderer.future_render(bullets_speed_text, (step_x, step_y + 32 * 4), "stats_bullets_speed")
            self.cache['stats_bullets_speed_text'] = bullets_speed_text
            self.stats_data['bullets_speed'] = self.player.bullets_speed
        else:
            self.renderer.future_render(self.cache['stats_bullets_speed_text'], (step_x, step_y + 32 * 4), "stats_bullets_speed")

        if self.player.invulnerability_frames != self.stats_data.get('invulnerability_frames') or self.cache.get('invulnerability_frames') is None:
            invulnerability_frames_text = self.resources["PressStart2P-Regular.ttf"].render("Inv frames: {}".format(self.player.invulnerability_frames), True, (255,255,255))
            self.renderer.future_render(invulnerability_frames_text, (step_x, step_y + 32 * 5), "stats_invulnerability_frames")
            self.cache['stats_invulnerability_frames_text'] = invulnerability_frames_text
            self.stats_data['invulnerability_frames'] = self.player.invulnerability_frames
        else:
            self.renderer.future_render(self.cache['stats_invulnerability_frames_text'], (step_x, step_y + 32 * 5), "stats_invulnerability_frames")

        if self.player.damage != self.stats_data.get('damage') or self.cache.get('damage') is None:
            damage_text = self.resources["PressStart2P-Regular.ttf"].render("Damage    : {}".format(self.player.damage), True, (255,255,255))
            self.renderer.future_render(damage_text, (step_x, step_y + 32 * 6), "stats_damage")
            self.cache['stats_damage_text'] = damage_text
            self.stats_data['damage'] = self.player.damage
        else:
            self.renderer.future_render(self.cache['stats_damage_text'], (step_x, step_y + 32 * 6), "stats_damage")

        # Game stats
        if self.clock.get_fps() != self.stats_data.get('fps') or self.cache.get('fps') is None:
            fps_text = self.resources["PressStart2P-Regular.ttf"].render("FPS       : {}".format(int(self.clock.get_fps())), True, (255,255,255))
            self.renderer.future_render(fps_text, (step_x, step_y + 32 * 8), "stats_fps")
            self.cache['stats_fps_text'] = fps_text
            self.stats_data['fps'] = self.clock.get_fps()

        return

    def draw(self):
        if self.background_color is None:
            self.background_color = self.renderer.background_color
            pygame.draw.rect(self.real_display, self.background_color, (0, 0, self.display_width, self.display_height))

        self.draw_tiles()
        self.draw_player()
        self.draw_bullets()
        if self.display_stats:
            self.draw_stats()
        else:
            self.renderer.remove_prefix("stats_")
        self.draw_hud()
        if self.display_map:
            self.draw_map()
            self.draw_hud_level()
        else:
            self.renderer.remove("map")
            self.renderer.remove("hud_level")
        self.renderer.render_cycle()

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
                    # print(self._map.cursor)
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
                            bullet.destroy(self)
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
