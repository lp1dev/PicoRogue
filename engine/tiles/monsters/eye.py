from os.path import join
from math import sqrt
from engine.bullet import Bullet
from engine.tiles.monsters.monster import Monster

class Eye(Monster):
    def __init__(self, x, y, damage=1, res=None, collide=True):
        self.bullets_delay = 70
        self.last_bullet = 0
        self.bullet_speed = 5
        Monster.__init__(self, x, y, damage, None, collide)

    def play(self, pygame_handler):
        self.last_bullet += 1
        if self.last_bullet > self.bullets_delay:
            self.shoot(pygame_handler)
            self.last_bullet = 0

    def shoot(self, pygame_handler):
        vector_x, vector_y = pygame_handler.player.x - self.x, pygame_handler.player.y - self.y
        distance = sqrt(vector_x ** 2 + vector_y **2)
        direc_x, direc_y = (self.bullet_speed * vector_x/distance, self.bullet_speed * vector_y/distance)
        bullet = Bullet(self.x, self.y, direc_x, direc_y, is_player=False, speed=self.bullet_speed, lifespan=100)
        pygame_handler.hostile_bullets.append(bullet)
        print(pygame_handler.hostile_bullets)