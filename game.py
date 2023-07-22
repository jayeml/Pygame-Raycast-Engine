import pygame
import math
import json
import os
import numba as nb
from random import randint
from Widgets.button import Button
from Widgets.label import Label
from numba.typed import List

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

draw_line = True

current_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(current_dir, "Assets")
sprites_dir = os.path.join(assets_dir, "sprites")
walls = os.path.join(assets_dir, "walls")
wall_list = os.listdir(walls)

victory_screen = pygame.image.load(os.path.join(assets_dir, "victory.jpg"))
victory_screen = pygame.transform.scale(victory_screen, (screen_width, screen_height))

textures = []
color_averages = []

for i in wall_list:
    if ".png" in i:
        image_path = os.path.join(walls, i)
        textures.append(pygame.transform.scale(pygame.image.load(image_path).convert(), (tile_size, tile_size)))

dude = pygame.image.load(os.path.join(sprites_dir, "dude.png")).convert_alpha()
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

level = List()
tile_map = []
for line in map_lines:
    map_row1 = []
    for char in line.strip():
        map_row1.append(int(char))
    if map_row1:
        level.append(map_row1)
        tile_map.append(map_row1)


def get_tile_color(image):
    width, height = image.get_size()
    total_r, total_g, total_b = 0, 0, 0

    for x in range(width):
        for y in range(height):
            r, g, b, _ = image.get_at((x, y))
            if g > r and g > b:
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
        self.speed = 6
        self.rotation = 0
        self.ray_angle = 270
        self.fov = 60
        self.hitbox = pygame.Rect(self.x - 25, self.y - 25, 16, 16)
        self.you_win = False

    def update_hitbox(self):
        self.hitbox.centerx = self.x
        self.hitbox.centery = self.y


class Sprite:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type

    def to_json(self):
        return {
            "x_pos": self.y,
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


try:
    with open("sprite_positions", 'r') as file:
        json_data = json.load(file)
        sprite_list = [Sprite.from_json(data) for data in json_data]
except json.JSONDecodeError:
    sprite_list = []


def random_color():
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    return r, g, b


play = Button(((screen_width // 2 - 100), (screen_height // 2 - 50), 200, 50), text='Start',
              command="from game import main\nmain()", hover_color=(64, 64, 64))
edit = Button(((screen_width // 2 - 100), (screen_height // 2 + 50), 200, 50), text='Level Editor',
              command="from level_editor import map_maker\nmap_maker()", hover_color=(64, 64, 64))
win = Button(((screen_width // 2 - 100), (screen_height // 2 + 65), 200, 50), text="WINNER!!!", hover_color=random_color())

buttons = [play, edit]


@nb.jit(nopython=True)
def cast_walls(angle, iteration, lvlMap, x, y, z, fov, player_rot):
    dist = 0
    end = [x, y]
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    rdx = math.sin(math.radians(player_rot))
    rdy = math.cos(math.radians(player_rot))
    dot_product = rdx * cos_angle + rdy * sin_angle
    while True:
        row_index = int(end[1] / tile_size)
        col_index = int(end[0] / tile_size)
        dist += 1
        end[0] = x + dist * cos_angle
        end[1] = y + dist * sin_angle
        if lvlMap[row_index][col_index] > 0:
            dist *= dot_product
            dist = int(abs(dist))

            wall_height = int(10000 / (dist + 1))

            wall_top = int(screen_height / 2 - wall_height / 2)
            wall_bottom = wall_top + wall_height

            wall_top -= (wall_height * z)
            wall_bottom -= (wall_height * z)

            ray_x = iteration * (screen_width / fov)

            type = lvlMap[row_index][col_index]

            return ray_x, wall_top, wall_bottom, wall_height, end[0], end[1], dist, type, False


def render_walls(x, y):
    it = 0
    deg = player.ray_angle - (player.fov // 2)
    for i in range(screen_width + 1):
        z = player.z
        it += player.fov / screen_width
        deg += player.fov / screen_width

        row = cast_walls(math.radians(deg), it, level, x, y, z, player.fov, player.rotation)
        tile_type = textures[row[7] - 1]
        tile_x = (row[4] + row[5]) % tile_size
        wall_surf = tile_type.subsurface((tile_x, 0, 1, tile_type.get_height()))
        transWallSurf = pygame.transform.scale(wall_surf, (1, row[3]))
        pygame.draw.line(screen, color_averages[row[7] - 1], (row[0], row[1]), (row[0], row[2]), 2)
        screen.blit(transWallSurf, (row[0], row[1]))


@nb.jit(nopython=True)
def canSeeSprite(px, py, sx, sy, lvlMap):
    dx = sx - px
    dy = sy - py
    dist = math.sqrt(dx ** 2 + dy ** 2)
    dx /= dist
    dy /= dist

    steps = int(dist)

    for i in range(steps):
        x = int(px + dx * i)
        y = int(py + dy * i)
        row_index = int(y / 16)
        col_index = int(x / 16)
        if lvlMap[row_index][col_index] > 0:
            return False
    return True


def save():
    global level
    with open('Map', 'w') as f:
        for i in tile_map:
            f.write(''.join(map(str, i)) + '\n')
        level = List(tile_map)

    if sprite_list:
        json_sprites = [sp.to_json() for sp in sprite_list]

        with open("sprite_positions", 'w') as sp_pos:
            json.dump(json_sprites, sp_pos, indent=2)


def refresh_window():
    screen.fill((3, 37, 126))
    pygame.draw.rect(screen, (0, 128, 0), (0, screen_height / 2, screen_width, screen_height / 2))

    render_walls(player.hitbox.centerx, player.hitbox.centery)

    for sp in sprite_list:
        sx = sp.x
        sy = sp.y

        dx = sx - player.x
        dy = sy - player.y

        h_angle = (math.degrees(math.atan2(dy, dx)) - player.ray_angle) % 360
        screen_x = int((h_angle * (screen_width / player.fov)) + (screen_width / 2))
        dist = int(math.sqrt(((sx - player.x) ** 2) + ((sy - player.y) ** 2)))

        if canSeeSprite(player.x, player.y, sx, sy, level):
            sh = int(10000 / (dist + 1)) / 2
            st = int(screen_height / 2 - sh / 2)

            screen.blit(pygame.transform.scale(type2sprite[sp.type], (sh, sh)), (screen_x, st))

    if player.you_win:
        screen.blit(victory_screen, (0, 0))
        win.hover_color = random_color()
        if win.button(screen):
            player.you_win = False
            menu()

    pygame.display.set_caption("Fps: " + str(cf) + "/40")
    pygame.display.update()


running = True

player = Player()


def menu():
    pygame.display.set_caption("Raycaster (Move Mouse)")
    title = Label("Raycast Engine", x=screen_width//2, y=150, font=title_font, center=True)
    while True:
        screen.fill((3, 37, 126))
        pygame.draw.rect(screen, (0, 128, 0), (0, screen_height / 2, screen_width, screen_height / 2))
        render_walls(192, 192)
        player.ray_angle += .2
        player.rotation -= .2
        title.show(screen)
        player.x = player.y = 192
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save()
                quit()

            elif event.type == pygame.MOUSEMOTION:
                pygame.display.set_caption("Raycaster")

        if play.button(screen):
            player.rotation = 0
            player.ray_angle = 270
            main()
        if edit.button(screen):
            from level_editor import map_maker
            map_maker()

        pygame.display.update()
        print(len(sprite_list))


def main():
    global running, canChange, renderMode, cf, draw_line
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()

        cf = str(int(clock.get_fps()))

        keys = pygame.key.get_pressed()

        if not player.you_win:
            if keys[pygame.K_a]:
                player.rotation += player.speed / 2
                player.ray_angle -= player.speed / 2
            elif keys[pygame.K_d]:
                player.rotation -= player.speed / 2
                player.ray_angle += player.speed / 2

            if keys[pygame.K_ESCAPE]:
                save()
                return

            dx = player.speed * math.sin(math.radians(player.rotation))
            dy = player.speed * math.cos(math.radians(player.rotation))
            player.speed = 6
            if keys[pygame.K_w]:
                player.oldx = player.x
                player.x -= dx
                player.oldy = player.y
                player.y -= dy
            elif keys[pygame.K_s]:
                player.oldx = player.x
                player.x += dx
                player.oldy = player.y
                player.y += dy
            elif keys[pygame.K_SPACE]:
                player.z -= .5
            elif keys[pygame.K_LSHIFT] and player.z < 0:
                player.z += .5

            if keys[pygame.K_f]:
                player.speed *= 2

        if tile_map[int(player.y / tile_size)][int(player.x / tile_size)] > 0 and player.z >= 0:
            if tile_map[int(player.y / tile_size)][int(player.x / tile_size)] == 9:
                player.you_win = True
            else:
                player.x = player.oldx
                player.y = player.oldy

        player.update_hitbox()

        refresh_window()

        canChange += 1
        clock.tick(40)
