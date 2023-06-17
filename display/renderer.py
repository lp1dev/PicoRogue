import pygame
from display.subrects import sub_rect

class Renderer:
    def __init__(self, display, real_display, display_width, display_height, game_width, game_height):
        self.display = display
        self.real_display = real_display
        self.display_width = display_width
        self.display_height = display_height
        self.game_width = game_width
        self.game_height = game_height
        self.res_to_render = []
        self.tiles_rendered = []
        self.rendered = {}
        self.step_x = (self.display_width - self.game_width) / 2
        self.step_y = (self.display_height - self.game_height) / 2
        self.game_ratio = self.game_height / self.game_width
        self.updated_rects = []
        self.show_updates_rects = False
        return
    
    def remove(self, id):
        if id in self.rendered:
            self.rendered[id]['deleted'] = True
        return

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
        # if real_screen:
        #     return pygame.rect.Rect(pos[0], pos[1], res.get_width(), res.get_height())
        # scaled = self.scale(_res)
        # return pygame.rect.Rect(_res['pos'][0], _res['pos'][1], scaled['res'].get_width(), scaled['res'].get_height())

    def scale(self, res):
        res = res.copy()
        if self.display_height > self.game_height:
            scaled_res = res['res']
            res['pos'] = (self.step_x + res['pos'][0], self.step_y + res['pos'][1])
            res['res'] = scaled_res
        else:
            print('TODO IMPLEMENT DOWNSCALING')
            pass
        return res


    def render_cycle(self):
        self.cleanup_cycle()
        sorted_res = sorted(self.res_to_render, key=lambda x: x['weight'])
        for res in sorted_res:
            if not res['real_screen']:
                scaled_res = self.scale(res)
                self.render_res(scaled_res)
            else:
                self.render_res(res)
            self.res_to_render.remove(res)
        self.res_to_render = []
        self.updated_rects = []
        return

    def cleanup_cycle(self):
        to_delete = []
        print(self.rendered)
        for _id in self.rendered.keys():
            if self.rendered[_id].get('deleted'):
                print('GONNA DELETE', self.rendered[_id])
                self.redraw_background_afterdelete(self.rendered[_id])
                to_delete.append(_id)
                # del self.rendered[_id]
        for _id in to_delete:
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
        print('Redrawing after move', res_old, res_new)
        sorted_rendered = sorted(self.rendered.keys(), key=lambda x: self.rendered[x]['weight'])

        for res_id in sorted_rendered:
            res = self.rendered[res_id]
            if res['id'] != res_old['id']:
                rect = pygame.Rect(res['x'], res['y'], res['res'].get_width(), res['res'].get_height())
                rect_old = pygame.Rect(res_old['x'], res_old['y'], res_old['res'].get_width(), res_old['res'].get_height())
                rect_new = pygame.Rect(res_new['pos'][0], res_new['pos'][1], res_new['res'].get_width(), res_new['res'].get_height())
                if rect.colliderect(rect_old):
                    self.real_display.blit(res['res'], (res['x'], res['y'])) # We blit the whole res again but don't update all of the screen
                    diff_rects = sub_rect(rect_old, rect_new)
                    print('diff_rects', diff_rects)
                    for diff_rect in diff_rects:
                        # pygame.draw.rect(self.real_display, (0, 255, 0), diff_rect)
                        pygame.display.update(diff_rect)
        return
    
    def redraw_background_afterdelete(self, res):
        # Reblitting the background after res delete
        print('Redrawing after delete', res)
        sorted_rendered = sorted(self.rendered.keys(), key=lambda x: self.rendered[x]['weight'])

        res = self.rendered[res['id']]
        for res_id in sorted_rendered:
            if res_id != res['id']:
                rect1 = pygame.Rect(res['pos'][0], res['pos'][1], res['res'].get_width(), res['res'].get_height())
                # pygame.draw.rect(self.real_display, (0, 0, 255), rect1)
                pygame.display.update(rect1)

    def redraw_background_res_update(self, res):
        # Reblitting the background after res change
        print('Redrawing after res update', res)
        sorted_rendered = sorted(self.rendered.keys(), key=lambda x: self.rendered[x]['weight'])

        for res_id in sorted_rendered:
            if res_id != res['id']:
                other_res = self.rendered[res_id]
                rect1 = pygame.Rect(res['pos'][0], res['pos'][1], res['res'].get_width(), res['res'].get_height())
                rect2 = pygame.Rect(other_res['x'], other_res['y'], other_res['res'].get_width(), other_res['res'].get_height())
                if rect1.colliderect(rect2):
                    self.real_display.blit(other_res['res'], (other_res['x'], other_res['y']))
                    pygame.display.update(rect2)

        return

    def render_res(self, res_obj):

        known_res = self.rendered.get(res_obj['id'])
        # print('Rendering:', res_obj)
        # if self.updated_rects:
            # print('self.updated_rects', self.updated_rects)

        if known_res and known_res.get('deleted') or res_obj.get('deleted'):
            raise Exception('Trying to render deleted res')

        for res in self.updated_rects:
            if res['res'].get_rect().colliderect(pygame.Rect(res_obj['pos'][0], res_obj['pos'][1], \
                                                             res_obj['res'].get_width(), res_obj['res'].get_height())):
                if res['weight'] < res_obj['weight']:
                    res_obj['force_redraw'] = True
        if known_res:
            # print('Known res:', known_res)
            if known_res["x"] != res_obj['pos'][0] or known_res["y"] != res_obj['pos'][1]:
                self.redraw_background_aftermove(known_res, res_obj)
            elif known_res["res"] == res_obj['res']:
                if not res_obj['force_redraw']:
                    # print('No need to redraw', res_obj)
                    return
            else:
                self.redraw_background_res_update(res_obj)
    
        print('Have chosen to render:', res_obj)

        self.debug_rect(res_obj, (0, 255, 0))
        rect = self.real_display.blit(res_obj['res'], (res_obj['pos'][0], res_obj['pos'][1]))
        self.updated_rects.append(res_obj)

        self.rendered[res_obj['id']] = {
            "pos": res_obj['pos'], 
            "x": res_obj['pos'][0], 
            "y": res_obj['pos'][1], 
            "res": res_obj['res'], 
            "id": res_obj['id'], 
            "weight": res_obj['weight'], 
            "last_rect": rect
        }

        # pygame.display.update()
        pygame.display.update((res_obj['pos'][0], res_obj['pos'][1], res_obj['res'].get_width(), res_obj['res'].get_height()))