import json
import math
import pygame
from numba import njit


def get_index(x, y):
    row_index = int(x / 8)
    col_index = int(y / 8)
    return row_index, col_index


class Sprite:
    def __init__(self, x, y, type, angle):
        self.x = x
        self.y = y
        self.type = type
        self.dist = 0
        self.hitbox = pygame.Rect(self.x, self.y, 4, 4)
        self.angle = angle
        self.health = 200
        self.see_player = False
        self.screen_x = 0
        self.screen_y = 0

    def update(self, _, __, tile_map, player):
        if self.type < 2 and self.see_player:

            dx = math.cos(self.angle)
            dy = math.sin(self.angle)

            new_row, new_col = get_index(self.y + dy, self.x + dx)

            if tile_map[new_row][new_col] > 0:
                self.x = 920
                self.y = 920
            else:
                p_row, p_col = get_index(player.y, player.x)
                if p_col == new_col and p_row == new_row:
                    player.health -= 1

            self.hitbox = pygame.Rect(self.x, self.y, 4, 4)

    def to_json(self):
        return {
            "x_pos": self.x,
            "y_pos": self.y,
            "type": self.type,
            "angle": self.angle
        }

    @classmethod
    def from_json(cls, json_data):
        return cls(
            x=json_data["x_pos"],
            y=json_data["y_pos"],
            type=json_data["type"],
            angle=json_data["angle"]
        )


def render_sprites(sp_list, player, screen, type2sprite, level, projectiles, tile_map):

    for sp in sp_list:
        sp.dist = math.dist([sp.x, sp.y], [player.x, player.y])
        sp.update(sp_list, projectiles, tile_map, player)

    new_sp_list = sorted(sp_list, key=lambda x: x.dist, reverse=True)

    for sp in new_sp_list:

        # sh, screen_x, st, can_shoot

        sp_info = sprite_calcs(sp.x, sp.y, player.x, player.y, player.z, player.ray_angle, level)

        if sp_info[0] is not None:

            sp.screen_x = sp_info[1]
            sp.screen_y = sp_info[2]

            sp.see_player = True

            if sp.type < 2:

                rot_sp = sp.angle % 360
                rot_p = player.ray_angle % 360

                if rot_sp - 45 < rot_p < rot_sp + 45:
                    sp.type = 1.1
                elif rot_sp - 135 < rot_p < rot_sp - 45:
                    sp.type = 1.3
                elif rot_sp + 45 < rot_p < rot_sp + 135:
                    sp.type = 1.2
                else:
                    sp.type = 1

            screen.blit(pygame.transform.scale(type2sprite[sp.type], (sp_info[0], sp_info[0])), (sp_info[1], sp_info[2]))

            if 960 - sp_info[0] < sp_info[1] < 960 + sp_info[0]/2 and sp.type < 2 and sp_info[3]:
                player.crosshair = (255, 0, 0)
                player.can_shotgun.append(sp)
        else:
            sp.see_player = False

    if not player.can_shotgun:
        player.crosshair = (0, 0, 0)


def load_sprites():
    try:
        with open("sprite_positions.json", 'r') as file:
            json_data = json.load(file)
            sprite_list = [Sprite.from_json(data) for data in json_data]
    except json.JSONDecodeError:
        sprite_list = []
    return sprite_list


@njit(fastmath=True)
def sprite_calcs(sx, sy, px, py, pz, p_rot, lvl):
    h_angle = math.degrees(math.atan2(sy - py, sx - px))
    h_angle_diff = h_angle - p_rot

    while h_angle_diff < -180:
        h_angle_diff += 360
    while h_angle_diff >= 180:
        h_angle_diff -= 360

    dist = math.sqrt((sx - px) ** 2 + (sy - py) ** 2)
    sh = int(10000 / (dist + 1) / 2)

    see_sp = can_see_sprite(px, py, sx, sy, lvl, dist)
    if see_sp[0]:
        screen_x = int(960 + h_angle_diff * 32)
        st = int(1080 / 2 - sh / 2)
        st -= sh * pz
        return sh, screen_x, st, see_sp[1]

    return None, None, None, None


@njit(fastmath=True)
def can_see_sprite(px, py, sx, sy, lvl_map, dist):

    dx = sx - px
    dy = sy - py
    dx /= dist+1e-99
    dy /= dist+1e-99

    map_len = [len(lvl_map), len(lvl_map[0])]

    steps = int(dist)

    can_shoot = True

    for i in range(steps):
        x = int(px + dx * i)
        y = int(py + dy * i)
        row_index = int(y / 8)
        col_index = int(x / 8)
        if row_index < map_len[0] and col_index < map_len[1]:
            if lvl_map[row_index][col_index] > 0:
                if lvl_map[row_index][col_index] != 10:
                    return False, True
                else:
                    can_shoot = False

    return True, can_shoot
