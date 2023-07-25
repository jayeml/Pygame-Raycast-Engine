import json
import math
import pygame


class Sprite:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.dist = 0

    def to_json(self):
        return {
            "x_pos": self.x,
            "y_pos": self.y,
            "type": self.type
        }

    @classmethod
    def from_json(cls, json_data):
        return cls(
            x=json_data["x_pos"],
            y=json_data["y_pos"],
            type=json_data["type"]
        )


def render_sprites(sp_list, player, screen, type2sprite, level):

    for sp in sp_list:
        sp.dist = math.dist([sp.x, sp.y], [player.x, player.y])

    new_sp_list = sorted(sp_list, key=lambda x: x.dist, reverse=True)

    for sp in new_sp_list:

        sx = sp.x
        sy = sp.y

        h_angle = (math.degrees(math.atan2(sy - player.y, sx - player.x)) % 360) - player.ray_angle
        screen_x = (h_angle * 19.2 + 576)
        dist = int(math.dist([sp.x, sp.y], [player.x, player.y]))

        if player.can_see_sprite(sx, sy, level) and -50 < screen_x < 1172:
            sh = (int(10000 / (dist + 1)) / 2)

            st = int(768 / 2 - sh / 2)

            screen.blit(pygame.transform.scale(type2sprite[sp.type], (sh, sh)), (screen_x, st))


def load_sprites():
    try:
        with open("sprite_positions.json", 'r') as file:
            json_data = json.load(file)
            sprite_list = [Sprite.from_json(data) for data in json_data]
    except json.JSONDecodeError:
        sprite_list = []
    return sprite_list

