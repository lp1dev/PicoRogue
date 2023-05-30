
class Tile:
    def __init__(self, x, y, damage=0, res=None, collide=False, block_bullets=True):
        self.x = x
        self.y = y
        self.damage = damage
        self.width = 64
        self.res = res
        self.collide = collide
        self.block_bullets = block_bullets
        self.rect = None
        self.destroyed = False
        
    def hit(self, damage=1):
        return

    def collide_player(self, player, map):
        return

    def after_destroyed(self, pygame_handler):
        return
