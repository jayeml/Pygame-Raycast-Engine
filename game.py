import pygame
import numpy as np
import numba as nb
from numba.typed import List
from random import randint
import os

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
sprites = os.path.join(assets_dir, "sprites")
walls = os.path.join(assets_dir, "walls")
wall_list = os.listdir(walls)

textures = []

for i in wall_list:
    if ".png" in i:
        image_path = os.path.join(walls, i)
        textures.append(pygame.transform.scale(pygame.image.load(image_path).convert(), (tile_size, tile_size)))

dude = pygame.image.load(os.path.join(sprites, "dude.png")).convert_alpha()
tree = pygame.image.load(os.path.join(sprites, "tree.png")).convert_alpha()
burrito = pygame.image.load(os.path.join(sprites, "burrito.png")).convert_alpha()

sprites = []

map_created = False

map_file = open("Map", "r")
map_lines = map_file.readlines()
map_file.close()

level = List()
tile_map = []
for line in map_lines:
    map_row1 = []
    for char in line.strip():
        map_row1.append(int(char))
    if map_row1:
        level.append(map_row1)
        tile_map.append(map_row1)


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
    def __init__(self, x, y, pic):
        self.x = x
        self.y = y
        self.type = pic


class Button:
    def __init__(self, x, y, text, width, height):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.text = text
        self.color = (0, 0, 0)

    def draw(self, color):
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), 0, 3)
        text = font.render(self.text, True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text, text_rect)

    def detect_collide(self, x, y):
        if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
            return True
        else:
            return False


play = Button((screen_width//2 - 100), (screen_height//2 - 50), 'Start', 200, 50)
edit = Button((screen_width//2 - 100), (screen_height//2 + 50), 'Level Editor', 200, 50)
win = Button((screen_width//2 - 100), (screen_height//2 + 100), "WINNER!!!", 200, 50)

buttons = [play, edit]


@nb.jit(nopython=True)
def cast_walls(angle, iteration, lvlMap, x, y, z, fov, player_rot):
    dist = 0
    end = [x, y]
    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)
    rdx = np.sin(np.deg2rad(player_rot))
    rdy = np.cos(np.deg2rad(player_rot))
    dot_product = rdx * cos_angle + rdy * sin_angle
    while True:
        row_index = int(end[1] / tile_size)
        col_index = int(end[0] / tile_size)
        dist += 1
        end[0] = x + dist * cos_angle
        end[1] = y + dist * sin_angle
        if lvlMap[row_index][col_index] > 0:
            dist = np.sqrt(((end[0] - x) ** 2) + ((end[1] - y) ** 2))
            dist *= dot_product
            dist = int(abs(dist))

            wall_height = int(10000 / (dist + 1))

            wall_top = int(screen_height / 2 - wall_height / 2)
            wall_bottom = wall_top + wall_height

            wall_top -= (wall_height * z)
            wall_bottom -= (wall_height * z)

            ray_x = iteration * (screen_width / fov)

            type = lvlMap[row_index][col_index]

            return ray_x, wall_top, wall_bottom, wall_height, end[0], end[1], dist, type


@nb.jit(nopython=True)
def canSeeSprite(px, py, sx, sy, s_dist, lvlMap):
    end = [px, py]

    steps = max((sx - px), (sy - py))
    dx = (sx - px) / steps
    dy = (sy - py) / steps

    for i in range(s_dist):
        row_index = int(end[1] / 16)
        col_index = int(end[0] / 16)
        if lvlMap[row_index][col_index] > 0:
            return False
        else:
            end[0] += dx
            end[1] += dy
    return True


def save():
    global level
    with open('Map', 'w') as f:
        for i in tile_map:
            f.write(''.join(map(str, i)) + '\n')
        level = List(tile_map)


def refresh_window():
    if not player.you_win:
        screen.fill((3, 37, 126))
        pygame.draw.rect(screen, (0, 128, 0), (0, screen_height / 2, screen_width, screen_height / 2))

        it = 0
        deg = player.ray_angle - (player.fov//2)
        for i in range(screen_width + 1):
            x, y = player.hitbox.centerx, player.hitbox.centery
            z = player.z
            it += player.fov / screen_width
            deg += player.fov / screen_width

            row = cast_walls(np.deg2rad(deg), it, level, x, y, z, player.fov, player.rotation)
            tile_type = textures[row[7] - 1]
            tile_x = (row[4] + row[5]) % tile_size
            wall_surf = tile_type.subsurface((tile_x, 0, 1, tile_type.get_height()))
            transWallSurf = pygame.transform.scale(wall_surf, (1, row[3]))
            pygame.draw.line(screen, (0, 0, 0), (row[0], row[1]), (row[0], row[2]), 2)
            screen.blit(transWallSurf, (row[0], row[1]))

            for sp in sprites:

                sx = sp.x
                sy = sp.y

                h_angle = np.rad2deg(np.arctan2(sy - player.y, sx - player.x)) - player.ray_angle
                screen_x = (h_angle * (screen_width / 60)) + (screen_width / 2)
                dist = int(np.sqrt(((sx - player.x) ** 2) + ((sy - player.y) ** 2)))

                if 0 < screen_x < screen_width and canSeeSprite(player.x, player.y, sx, sy, dist, level):

                    sh = int(10000 / (dist + 1))/2
                    st = int(screen_height / 2 - sh / 2)
                    screen.blit(pygame.transform.scale(sp.type, (sh, sh)), (screen_x, st))

    if player.you_win:

        win_screen = title_font.render('YOU WIN!!!!!', True, 0)
        win_rect = win_screen.get_rect(center=(screen_width // 2, 150))
        screen.blit(win_screen, win_rect)

    pygame.display.set_caption("Fps: " + str(cf) + "/30")
    pygame.display.update()


running = True

player = Player()


def menu():
    pygame.display.set_caption("Raycaster (Move Mouse)")
    while True:
        screen.fill((100, 100, 100))
        title = title_font.render('Raycast Engine', True, 0)
        title_rect = title.get_rect(center=(screen_width // 2, 150))
        screen.blit(title, title_rect)
        player.x = player.y = 192
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save()
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play.x <= event.pos[0] <= play.x + play.width and play.y <= event.pos[1] <= play.y + play.height:
                    main()
                if edit.x <= event.pos[0] <= edit.x + edit.width and edit.y <= event.pos[1] <= edit.y + edit.height:
                    from level_editor import map_maker
                    map_maker()
            elif event.type == pygame.MOUSEMOTION:
                pygame.display.set_caption("Raycaster")
                for button in buttons:
                    if button.x <= event.pos[0] <= button.x + button.width and button.y <= event.pos[1] <= button.y + button.height:
                        button_color = (64, 64, 64)
                    else:
                        button_color = (255, 255, 255)

                    button.draw(button_color)
                pygame.display.update()


def main():
    global running, canChange, renderMode, cf, draw_line
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if win.x <= event.pos[0] <= win.x + win.width and win.y <= event.pos[1] <= win.y + win.height and player.you_win:
                    player.you_win = False
                    player.x = player.y = 192
                    player.rotation = 0
                    player.ray_angle = 270
            elif event.type == pygame.MOUSEMOTION:
                if player.you_win:
                    if win.x <= event.pos[0] <= win.x + win.width and win.y <= event.pos[1] <= win.y + win.height:
                        win.draw((randint(0, 255), randint(0, 255), randint(0, 255)))
                    else:
                        win.draw((255, 255, 255))

        cf = str(int(clock.get_fps()))

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            player.rotation += player.speed/2
            player.ray_angle -= player.speed/2
        elif keys[pygame.K_d]:
            player.rotation -= player.speed/2
            player.ray_angle += player.speed/2

        if keys[pygame.K_ESCAPE]:
            save()
            menu()

        dx = player.speed * np.sin(np.deg2rad(player.rotation))
        dy = player.speed * np.cos(np.deg2rad(player.rotation))
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

        player.update_hitbox()

        refresh_window()

        canChange += 1
        clock.tick(30)