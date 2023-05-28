class Bullet:
    def __init__(self, x, y, vec_x, vec_y, is_player=True, speed=12):
        self.is_player = is_player
        self.speed = speed
        self.x = x
        self.y = y
        self.vec_x = vec_x
        self.vec_y = vec_y
        self.age = 0
        self.lifespan = 60
        return