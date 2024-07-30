"""
I think the rendering bug we have left is due to the blit() calls taking too
much time and the rendering not keeping up with "fast" moving objects.

I should try to optimize my blit to not reblit all of the resources when something
changed, even though they're not updated on the screen.
"""

import pygame
from display.subrects import sub_rect
from sys import argv

class Renderer:
    def __init__(self, display, real_display, display_width, display_height, game_width, game_height):
        self.debug = 'debug' in argv
        self.display = display
        self.real_display = real_display
        self.display_width = display_width
        self.display_height = display_height
        self.game_width = game_width
        self.game_height = game_height
        self.res_to_render = []
        self.rendered = {}
        # self.step_x = (self.display_width - self.game_width) / 2
        # self.step_y = (self.display_height - self.game_height) / 2
        self.step_x = (self.real_display.get_width() / 2) - (self.game_width / 2)
        self.step_y = (self.real_display.get_height() / 2) - (self.game_height / 2)
        
        self.tile_width = 64
        self.game_ratio = self.game_height / self.game_width
        self.fake_display_rect = pygame.Rect(self.step_x + self.tile_width, self.step_y + self.tile_width, \
                                             self.display.get_width() - (self.tile_width * 2), self.display.get_height() - (self.tile_width * 2))
        self.updated_rects = []
        self.show_updates_rects = False
        self.cycles = 0
        self.background_color = (15, 31, 43)
        return


    def remove_prefix(self, prefix):
        for id in self.rendered.keys():
            if id.startswith(prefix):
                self.rendered[id]['deleted'] = True

    def remove_tiles(self):
        for id in self.rendered.keys():
            if id.startswith('tile_'):
                self.rendered[id]['deleted'] = True

    def remove_bullets(self):
        for id in self.rendered.keys():
            if id.startswith('bullet_'):
                self.rendered[id]['deleted'] = True

    def remove(self, _id):
        if _id in self.rendered.keys():
            self.rendered[_id]['deleted'] = True
        return
    
    def update(self, _id, res):
        res['x'] = self.rendered[_id]['x']
        res['y'] = self.rendered[_id]['y']
        self.rendered[_id] = res

    def future_render(self, res, pos, id, real_screen=True, force_redraw=False, weight=1):
        _res = {
            "res": res, 
            "pos": pos,
            "id": id, 
            "real_screen": real_screen, 
            "force_redraw": force_redraw,
            "weight": weight
        }
        self.res_to_render.append(_res)

        if real_screen:
             return pygame.rect.Rect(pos[0], pos[1], res.get_width(), res.get_height())
        scaled = self.scale_up(_res)
        return pygame.rect.Rect(_res['pos'][0], _res['pos'][1], scaled['res'].get_width(), scaled['res'].get_height())

    def scale_up(self, res):
        if self.display_height > self.game_height:
            scaled_res = res['res']
            res = res.copy()
            res['pos'] = (self.step_x + res['pos'][0], self.step_y + res['pos'][1])
            res['res'] = scaled_res
        return res

    def render_cycle(self):
        self.cleanup_cycle()
        sorted_res = sorted(self.res_to_render, key=lambda x: x['weight'])
        for res in sorted_res:
            if not res['real_screen']:
                scaled_res = self.scale_up(res)
                self.render_res(scaled_res)
            else:
                self.render_res(res)
            self.res_to_render.remove(res)
        self.res_to_render = []
        self.updated_rects = []
        return

    def cleanup_cycle(self):
        self.cycles += 1
        to_delete = []
        for _id in self.rendered.keys():
            if self.rendered[_id].get('deleted'):
                to_delete.append(_id)
        for _id in to_delete:
            self.redraw_background_afterdelete(self.rendered[_id])
            del self.rendered[_id]
        return

    def debug_rect(self, res_obj, color=(255, 0, 0)):
        if self.show_updates_rects:
            pygame.draw.rect(self.real_display, color, 
                                          (res_obj['pos'][0] + 2, res_obj['pos'][1] + 2, 
                                           res_obj['res'].get_width() + 4, res_obj['res'].get_height() + 4), 1)

    def render_tile(self, tile):
        self.render_res(tile.res, (tile.x, tile.y), tile.id)
        
    def redraw_background_aftermove(self, res_old, res_new):
        sorted_rendered = sorted(self.rendered.keys(), key=lambda x: self.rendered[x]['weight'])

        for res_id in sorted_rendered:
            res = self.rendered[res_id]
            if res['id'] != res_old['id']:
                rect = pygame.Rect(res['x'], res['y'], res['res'].get_width(), res['res'].get_height())
                rect_old = pygame.Rect(res_old['x'], res_old['y'], res_old['res'].get_width(), res_old['res'].get_height())
                rect_new = pygame.Rect(res_new['pos'][0], res_new['pos'][1], res_new['res'].get_width(), res_new['res'].get_height())
                if rect.colliderect(rect_old):
                    self.real_display.blit(res['res'], (res['x'], res['y'])) # We blit the whole res again but don't update all of the screen //TODO optimize this blit
                    # self.real_display.blit(res_old['res'], (res_old['x'], res_old['y'])) # We blit the whole res again but don't update all of the screen
                    diff_rects = sub_rect(rect_old, rect_new)
                    for diff_rect in diff_rects:
                        if self.debug:
                            pygame.draw.rect(self.real_display, (0, 255, 0), diff_rect)
                        pygame.display.update(diff_rect)
                        # pygame.display.update(rect_new)
        return
    
    def redraw_background_afterdelete(self, res):
        # Reblitting the background after res delete
        sorted_rendered = sorted(self.rendered.keys(), key=lambda x: self.rendered[x]['weight'])

        rect1 = pygame.Rect(res['pos'][0], res['pos'][1], res['res'].get_width(), res['res'].get_height())

        if res.get('real_screen'):
            pygame.draw.rect(self.real_display, self.background_color, rect1)

        res = self.rendered[res['id']]
        for res_id in sorted_rendered:
            if res_id != res['id']:
                other_res = self.rendered[res_id]
                rect1 = pygame.Rect(res['x'], res['y'], res['res'].get_width(), res['res'].get_height())
                if self.debug:
                    pygame.draw.rect(self.real_display, (0, 0, 255), rect1)
                # C'est ça qui déconne sur mon rendering, je n'ai pas fait la partie où je dois update le background après
                # avoir supprimé un res

                if rect1.colliderect(pygame.Rect(other_res['x'], other_res['y'], other_res['res'].get_width(), other_res['res'].get_height())):
                    self.real_display.blit(other_res['res'], (other_res['x'], other_res['y']))

                pygame.display.update(rect1)

    def redraw_background_res_update(self, res):
        # Reblitting the background after res change
        sorted_rendered = sorted(self.rendered.keys(), key=lambda x: self.rendered[x]['weight'])

        rect1 = pygame.Rect(res['pos'][0], res['pos'][1], res['res'].get_width(), res['res'].get_height())

        if res.get('real_screen'):
            pygame.draw.rect(self.real_display, self.background_color, rect1)

        for res_id in sorted_rendered:
            if res_id != res['id']:
                other_res = self.rendered[res_id]
                rect2 = pygame.Rect(other_res['x'], other_res['y'], other_res['res'].get_width(), other_res['res'].get_height())
                if rect1.colliderect(rect2):
                    self.real_display.blit(other_res['res'], (other_res['x'], other_res['y']))
                    if self.debug:
                        pygame.draw.rect(self.real_display, (0, 255, 255), rect1)
        pygame.display.update(rect1)

        return

    def render_res(self, res_obj):

        known_res = self.rendered.get(res_obj['id'])

        # TODO make it that if a res is on the fake screen and outside of the rect of the fake screen, it is not rendered

        res_rect = pygame.Rect(res_obj['pos'][0], res_obj['pos'][1], res_obj['res'].get_width(), res_obj['res'].get_height())
        if not self.fake_display_rect.colliderect(res_rect) and not res_obj.get('real_screen'):
            return

        if known_res and known_res.get('deleted') or res_obj.get('deleted'):
            raise Exception('Trying to render deleted res')

        for res in self.updated_rects:
            if res['res'].get_rect().colliderect(pygame.Rect(res_obj['pos'][0], res_obj['pos'][1], \
                                                             res_obj['res'].get_width(), res_obj['res'].get_height())):
                if res['weight'] < res_obj['weight']:
                    res_obj['force_redraw'] = True
        if known_res:
            if known_res["x"] != res_obj['pos'][0] or known_res["y"] != res_obj['pos'][1]:
                self.redraw_background_aftermove(known_res, res_obj) # Not the issue with the player model
            elif known_res["res"] == res_obj['res'] \
                and known_res["x"] == res_obj['pos'][0] \
                    and known_res["y"] == res_obj['pos'][1]:
                if not res_obj['force_redraw']:
                    return
            else:
                self.redraw_background_res_update(res_obj)

        self.debug_rect(res_obj, (0, 255, 0))

        rect = self.real_display.blit(res_obj['res'], (res_obj['pos'][0], res_obj['pos'][1]))
        pygame.display.update(rect)

        self.updated_rects.append(res_obj)

        self.rendered[res_obj['id']] = {
            "pos": res_obj['pos'],
            "x": res_obj['pos'][0], 
            "y": res_obj['pos'][1], 
            "res": res_obj['res'], 
            "id": res_obj['id'], 
            "weight": res_obj['weight'], # 2 is for tiles, 1 is default, 0 is bg
            "last_rect": rect,
            "deleted": res_obj.get('deleted'),
            "real_screen": res_obj.get('real_screen')
        }
        