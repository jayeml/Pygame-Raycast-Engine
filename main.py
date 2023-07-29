import pygame
import math
import os
import json
import sprite
import numba as nb
import numpy as np
from random import randint
from Widgets.button import Button

pygame.init()

screen_width = 1152
screen_height = 768
halfheight = screen_height // 2
tile_size = 16
screen = pygame.display.set_mode((screen_width, screen_height), pygame.HWSURFACE | pygame.DOUBLEBUF)

clock = pygame.time.Clock()

font = pygame.font.SysFont('arial', 30)
title_font = pygame.font.SysFont('arial', 100)

canChange = 0

bob_height = .02

current_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(current_dir, "Assets")
sprites_dir = os.path.join(assets_dir, "sprites")
walls = os.path.join(assets_dir, "walls")
wall_list = os.listdir(walls)

victory_screen = pygame.image.load(os.path.join(assets_dir, "victory.jpg"))
victory_screen = pygame.transform.scale(victory_screen, (screen_width, screen_height))

sky1 = pygame.image.load(os.path.join(assets_dir, "sky.jpg"))
sky1 = pygame.transform.scale(sky1, (screen_width / 2, screen_height//2))


textures = []
color_averages = []

for i in wall_list:
    if ".png" in i:
        image_path = os.path.join(walls, i)
        textures.append(pygame.transform.scale(pygame.image.load(image_path).convert(), (tile_size, tile_size)))

textures_data = np.array([pygame.surfarray.array3d(texture) for texture in textures], dtype=np.uint8)

dude = pygame.image.load(os.path.join(sprites_dir, "ufo dude.png")).convert_alpha()
tree = pygame.image.load(os.path.join(sprites_dir, "tree.png")).convert_alpha()
burrito = pygame.image.load(os.path.join(sprites_dir, "burrito.png")).convert_alpha()

type2sprite = {
        1: dude,
        2: tree,
        3: burrito
    }

map_created = False

with open("Map", "r") as f:
    map_lines = f.readlines()

level = nb.typed.List()
tile_map = []
for line in map_lines:
    map_row1 = []
    for char in line.strip():
        map_row1.append(int(char))
    if map_row1:
        level.append(map_row1)
        tile_map.append(map_row1)

sprite_list = sprite.load_sprites()


def get_tile_color(image):
    width, height = image.get_size()
    total_r, total_g, total_b = 0, 0, 0

    for x in range(width):
        for y in range(height):
            r, g, b, _ = image.get_at((x, y))
            if g > r and b < 200:
                g *= 1.5
            total_r += r
            total_g += g
            total_b += b

    pixel_count = width * height
    average_r = total_r // pixel_count
    average_g = total_g // pixel_count
    average_b = total_b // pixel_count

    return average_r, average_g, average_b


for i in textures:
    color_averages.append(get_tile_color(i))


class Player:
    def __init__(self):
        self.x = 192
        self.y = 192
        self.z = 0
        self.oldx = self.x
        self.oldy = self.y
        self.speed = 5
        self.rotation = 0
        self.ray_angle = 270
        self.fov = 60
        self.hitbox = pygame.Rect(self.x - 25, self.y - 25, 16, 16)
        self.you_win = False
        self.view_bob_offset = 0.0
        self.view_bob_speed = 0.0
        self.moved = False

    def update(self):
        self.hitbox.centerx = self.x
        self.hitbox.centery = self.y

        self.view_bob_speed = 0.01 * self.speed / self.speed

        self.view_bob_offset = math.sin(pygame.time.get_ticks() * self.view_bob_speed) * bob_height
        self.view_bob_offset = 0

    def collision(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        final_x = self.x
        final_y = self.y

        row_index, col_index = get_index(self.y, self.x)
        new_row, new_col = get_index(new_y, new_x)

        if tile_map[row_index][new_col] == 0:
            final_x += dx
            self.moved = True

        if tile_map[new_row][col_index] == 0:
            final_y += dy
            self.moved = True

        if tile_map[new_row][new_col] == 9:
            self.you_win = True

        return final_x, final_y


def random_color():
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    return r, g, b


def get_index(row, col):
    row_index = int(row / tile_size)
    col_index = int(col / tile_size)
    return row_index, col_index


play = Button(((screen_width // 2 - 100), (screen_height // 2 - 50), 200, 50), text='Start',
              command="from game import main\nmain()", hover_color=(64, 64, 64))
edit = Button(((screen_width // 2 - 100), (screen_height // 2 + 50), 200, 50), text='Level Editor',
              command="from level_editor import map_maker\nmap_maker()", hover_color=(64, 64, 64))
win = Button(((screen_width // 2 - 100), (screen_height // 2 + 65), 200, 50), text="WINNER!!!", hover_color=random_color())

buttons = [play, edit]


@nb.jit(nopython=True)
def cast_walls(angle, iteration, lvlMap, x, y, z, fov, player_rot, ray_num):
    end = [x, y]
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    rdx = math.sin(math.radians(player_rot))
    rdy = math.cos(math.radians(player_rot))
    fix_fish_eye = rdx * cos_angle + rdy * sin_angle

    translucent = False

    for i in range(10000):
        row_index = int(end[1] / tile_size)
        col_index = int(end[0] / tile_size)

        if row_index < 0 or col_index < 0 or row_index >= len(lvlMap) or col_index >= len(lvlMap[0]):
            break

        if lvlMap[row_index][col_index] > 0:

            ray_x = iteration * (screen_width / fov)
            wall_type = lvlMap[row_index][col_index]

            dist = fix_fish_eye * i
            dist = int(abs(dist))

            wall_height = int(10000 / (dist + 1))

            wall_top = int(screen_height / 2 - wall_height / 2)
            wall_bottom = wall_top + wall_height

            wall_top -= (wall_height * z)
            wall_bottom -= (wall_height * z)

            if wall_type == 4:
                translucent = True

            if wall_type != 4 or ray_num % 2 != 0:
                return ray_x, wall_top, wall_bottom, wall_height, end[0], end[1], dist, wall_type, translucent

        end[0] = x + i * cos_angle
        end[1] = y + i * sin_angle


@nb.jit(nopython=True)
def floor_calcs(px, py, pa):
    floor_data = np.zeros((screen_width, screen_height, 3), dtype=np.uint8)
    for i in range(screen_width):
        v_rot = pa + math.radians(i / (screen_width / 60) - 30)
        sin, cos, cos2 = math.sin(v_rot), math.cos(v_rot), math.cos(math.radians(i / (screen_width / 60) - 30))
        for j in range(screen_height // 2, 0, -1):
            n = (screen_height / 2) / (screen_height / 2 - j + 1)
            x, y = px + cos * n, py + sin * n
            xx, yy = int(x * 2 % 1 * 16), int(y * 2 % 1 * 16)

            if int(x) % 2 == 0 and int(y) % 2 == 0:
                floor_data[i, screen_height - j] = (0, 0, 0)
            else:
                floor_data[i, screen_height - j] = (255, 255, 255)

    return floor_data


def render_walls(x, y):
    screen.fill((200, 200, 200))

    floor_data = floor_calcs(player.x, player.y, player.rotation)

    floor_surface = pygame.surfarray.make_surface(floor_data)
    screen.blit(floor_surface, (0, 0))


    it = 0
    ray_num = 0
    deg = player.ray_angle - (player.fov // 2)
    for i in range(screen_width // 2 + 1):
        # row = ray_x, wall_top, wall_bottom, wall_height, end[0], end[1], dist, wall_type, translucent, alt_translucent

        row = cast_walls(math.radians(deg), it, level, x, y, player.z, player.fov, player.rotation, ray_num)
        tile_type = textures[row[7] - 1]
        tile_x = (row[4] + row[5]) % tile_size
        wall_surf = tile_type.subsurface((tile_x, 0, 1, tile_type.get_height()))

        if row[8]:
            transWallSurf = pygame.transform.scale(wall_surf, (1, row[3]))
            pygame.draw.line(screen, color_averages[row[7] - 1], (row[0], row[1]), (row[0], row[2]), 1)
        else:
            transWallSurf = pygame.transform.scale(wall_surf, (2, row[3]))
            pygame.draw.line(screen, color_averages[row[7] - 1], (row[0], row[1]), (row[0], row[2]), 2)

        screen.blit(transWallSurf, (int(row[0]), int(row[1])))

        # pygame.draw.line(screen, (0, 128, 0), (row[0], row[2] - 1), (row[0], screen_height), 2)
        # pygame.draw.line(screen, (181, 211, 231), (row[0], 0), (row[0], row[1]), 2)

        ray_num += 1
        it += player.fov / (screen_width / 2 + 1)
        deg += player.fov / (screen_width / 2 + 1)




def save():
    global level
    with open('Map', 'w') as f:
        for i in tile_map:
            f.write(''.join(map(str, i)) + '\n')
        level = nb.typed.List(tile_map)

    if sprite_list:
        json_sprites = [sp.to_json() for sp in sprite_list]

        with open("sprite_positions.json", 'w') as sp_pos:
            json.dump(json_sprites, sp_pos, indent=2)


running = True

player = Player()


def main():
    global running, canChange
    pygame.mouse.set_visible(False)
    pygame.mouse.set_pos(screen_width // 2, screen_height // 2)
    prev_mousePos = pygame.mouse.get_pos()[0]
    accumulated_change = 0

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()

        keys = pygame.key.get_pressed()

        player.moved = False

        if not player.you_win:

            mousePos = pygame.mouse.get_pos()[0]
            change = (mousePos - prev_mousePos)
            accumulated_change += change
            player.ray_angle += accumulated_change / 4
            player.rotation -= accumulated_change / 4
            player.ray_angle %= 360
            player.rotation %= 360
            pygame.mouse.set_pos(screen_width // 2, screen_height // 2)

            if change != 0:
                accumulated_change = 0

            if keys[pygame.K_ESCAPE]:
                save()
                pygame.mouse.set_visible(True)
                return

            dx = player.speed * math.sin(math.radians(player.rotation))
            dy = player.speed * math.cos(math.radians(player.rotation))

            side_dx = (player.speed / 2) * math.sin(math.radians(player.rotation + 90))
            side_dy = (player.speed / 2) * math.cos(math.radians(player.rotation + 90))

            player.oldx = player.x
            player.oldy = player.y
            player.speed = 4

            if keys[pygame.K_w]:
                player.x, player.y = player.collision(-dx, -dy)
            if keys[pygame.K_s]:
                player.x, player.y = player.collision(dx, dy)
            if keys[pygame.K_a]:
                player.x, player.y = player.collision(-side_dx, -side_dy)
            if keys[pygame.K_d]:
                player.x, player.y = player.collision(side_dx, side_dy)
            if keys[pygame.K_SPACE]:
                player.z -= .5
            if keys[pygame.K_LSHIFT] and player.z < 0:
                player.z += .5

            if keys[pygame.K_f]:
                player.speed *= 2

            pygame.mouse.set_pos(screen_width // 2, screen_height // 2)

        if tile_map[int(player.y / tile_size)][int(player.x / tile_size)] > 0:
            if tile_map[int(player.y / tile_size)][int(player.x / tile_size)] == 9:
                player.you_win = True
            else:
                player.x = player.oldx
                player.y = player.oldy

        player.update()

        #screen.fill((3, 37, 126))

        if player.moved:
            player.z += player.view_bob_offset
            if player.z > 0:
                player.z = 0
        elif player.z < 0:
            player.z += .01

        render_walls(player.hitbox.centerx, player.hitbox.centery)
        sprite.render_sprites(sprite_list, player, screen, type2sprite, level)

        if player.you_win:
            pygame.mouse.set_visible(True)
            screen.blit(victory_screen, (0, 0))
            win.hover_color = random_color()
            if win.button(screen):
                player.you_win = False
                pygame.mouse.set_visible(False)
                player.x = 192
                player.y = 192
                player.z = 0

        pygame.display.set_caption("Fps: " + str(int(clock.get_fps())) + "/60")
        pygame.display.update()

        canChange += 1
        clock.tick(60)


if __name__ == '__main__':
    from menu import menu
    menu()

