from engine.tiles.flame import Flame
from engine.tiles.monsters.eye import Eye, Eye2
from engine.tiles.items import pick_item, Pedestal
from engine.tiles.door import Door

BASIC_TILES = {
    "F": {"build":Flame, "level": False}, 
    "E": {"build":Eye, "level": True},
    "2": {"build":Eye2, "level": True},
    "I": {"build":pick_item, "level": False},
    "i": {"build":Pedestal, "level": False}
}

def load_tiles(pygame_handler):
    room = pygame_handler._map.get_current_room()
    tile_width = pygame_handler.resources['room_wall_top_right.png'].get_width()
    step_x = tile_width
    step_y = tile_width

    for i in range(0, room.height):
        for j in range(0, room.width):
            tile_str = room.get_tile(i, j)
                        
            if tile_str == "S" and pygame_handler.player.x == 0 and pygame_handler.player.y == 0:
                pygame_handler.player.x = (j * tile_width) + step_x
                pygame_handler.player.y = (i * tile_width) + step_y
                pygame_handler.player.collide = True
    
            elif tile_str in BASIC_TILES.keys():
                if BASIC_TILES[tile_str]['level']:
                    tile = BASIC_TILES[tile_str]['build']((j * tile_width) + step_x, (i * tile_width) + step_y, level=pygame_handler.level)
                    pygame_handler.tiles.append(tile)
                else:
                    tile = BASIC_TILES[tile_str]['build']((j * tile_width) + step_x, (i * tile_width) + step_y)
                    pygame_handler.tiles.append(tile)

    if room.door_up:
        tile = Door((pygame_handler.width / 2) - (tile_width / 2), (tile_width * 0.2), "UP", is_open=room.start)
        pygame_handler.tiles.append(tile)
                    
    if room.door_down:
        tile = Door((pygame_handler.width / 2) - (tile_width / 2), (pygame_handler.height - tile_width - (tile_width * 0.2)), "DOWN", is_open=room.start)
        pygame_handler.tiles.append(tile)

    if room.door_left:
        tile = Door(tile_width * 0.2, (pygame_handler.height / 2 - (tile_width / 2)), "LEFT", is_open=room.start)
        pygame_handler.tiles.append(tile)

    if room.door_right:
        tile = Door(pygame_handler.width - tile_width - tile_width * 0.2, (pygame_handler.height / 2 - (tile_width / 2)), "RIGHT", is_open=room.start)
        pygame_handler.tiles.append(tile)