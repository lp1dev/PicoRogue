import pygame
import pygame
from os.path import join


class Animation:
    def __init__(self, filename, num_frames, fps=60, tile_length=64, selected_frame=0, width=None, height=None, duration=0.25):
        self.timer = 0
        self.fps = fps
        self.duration_seconds = duration
        self.frame = selected_frame
        self.filename = filename
        self.num_frames = num_frames
        self.wide_res = pygame.image.load(join("resources", "textures", filename)).convert_alpha()
        self.tile_length = tile_length
        self.selected_frame = selected_frame
        self.width = width
        self.height = height

    def get_frame(self, frame):
        if self.width and self.height:
            return self.wide_res.subsurface((self.width * frame, 0, self.width, self.height))
        else:
            return self.wide_res.subsurface((self.tile_length * frame, 0, self.tile_length, self.tile_length))
        
    def get_next_frame(self):
        self.timer += 1
        if self.timer >= (self.fps * self.duration_seconds):
            self.timer = 0
            self.frame += 1
            if self.frame >= self.num_frames:
                self.frame = 0
        output = pygame.Surface((self.tile_length, self.tile_length), pygame.SRCALPHA, 32)
        output.blit(self.wide_res, (0, 0), (self.tile_length * self.frame, 0, self.tile_length, self.tile_length))
        return output

