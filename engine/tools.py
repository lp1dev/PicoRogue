from math import hypot

def distance(obj1, obj2):
    dx, dy = obj1.x - obj2.x, obj1.y - obj2.y
    return int(hypot(dx, dy))

def move_towards(obj, destination_x, destination_y):
    dx, dy = destination_x - obj.x, destination_y - obj.y
    dist = hypot(dx, dy)
    if int(dist) < 2:
        return
    dx, dy = dx / dist, dy / dist
    obj.x += dx * obj.speed
    obj.y += dy * obj.speed

def convert_pos_screen_game(pygame_handler, pos):
    ratio_width = pygame_handler.display_width / pygame_handler.width
    ratio_height = pygame_handler.display_height / pygame_handler.height
    return (int(pos[0] / ratio_width), int(pos[1] / ratio_height))