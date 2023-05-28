
class Player:
    def __init__(self):
        self.lives = 3
        self.max_lives = 3
        self.speed = 10
        self.x = 0
        self.y = 0
        self.bullets_delay = 20
        self.invulnerability_frames = 120
        self.bullets = []
        self.rect = None
        self.damage = 1
        self.collide = False
        self.time_since_last_damage = 100
        self.inventory = []
        return

    def hit(self, damage):
        if self.time_since_last_damage > self.invulnerability_frames:
            self.lives -= damage
            self.time_since_last_damage = 0
