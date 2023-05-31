import pygame
from os import walk
from os.path import join

def load_resources():
    resources = {}
    for root, dirs, files in walk(join("resources", "textures")):
        for filename in files:
            if filename.endswith('.png'):
                resources[filename] = pygame.image.load(join("resources", "textures", filename)).convert_alpha()
    for root, dirs, files in walk(join("resources", "fonts")):
        for filename in files:
            if filename.endswith('.ttf') or filename.endswith('.otf'):
                resources[filename] = pygame.font.Font(join("resources", "fonts", filename), 32)
    print('Loaded resources', resources)
    return resources