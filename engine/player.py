
class Player:
    def __init__(self):
        self.lives = 3
        self.max_lives = 3
        self.speed = 10
        self.x = 0
        self.y = 0
        self.bullets_delay = 30
        self.invulnerability_frames = 120
        self.bullets = []
        self.rect = None
        return