class Tile:
    def __init__(self, x, y, damage=0, res=None, collide=False):
        self.x = x
        self.y = y
        self.damage = damage
        self.width = 64
        self.res = res
        self.collide = collide
        self.rect = None
        self.destroyed = False
        
    def hit(self):
        return
