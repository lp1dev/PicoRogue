class Player:
    def __init__(self):
        self.lives = 3
        self.max_lives = 3
        self.coins = 0
        self.max_coins = 99
        self.speed = 2
        self.x = 0
        self.y = 0
        self.bullets_delay = 20
        self.bullets_lifespan = 30
        self.bullets_speed = 5
        self.invulnerability_frames = 60
        self.bullets = []
        self.rect = None
        self.damage = 1
        self.collide = False
        self.time_since_last_damage = 100
        self.inventory = []
        self.animation_left = None
        self.animation_right = None
        self.orientation = "left"
        self.is_moving = False
        return
    
    def hit(self, damage):
        if self.time_since_last_damage > self.invulnerability_frames and self.lives > 0:
            self.lives -= damage
            self.time_since_last_damage = 0
