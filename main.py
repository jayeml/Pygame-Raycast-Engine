import pygame
import math
import os
import json
import guns
import sprite
import pygame.freetype
from copy import deepcopy
from guns import BurritoLauncher, BurritoShotgun
from numba import njit, typed
from random import randint
from Widgets.button import Button

pygame.init()

screen_width = 1920
screen_height = 1080
halfheight = screen_height // 2
tile_size = 8
screen = pygame.display.set_mode((screen_width, screen_height), pygame.HWSURFACE | pygame.DOUBLEBUF)

clock = pygame.time.Clock()

font = pygame.font.SysFont('arial', 30)
title_font = pygame.font.SysFont('arial', 100)
damage_font = pygame.freetype.Font('Assets\\Impact.ttf')
canChange = 0

current_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(current_dir, "Assets")
sprites_dir = os.path.join(assets_dir, "sprites")
gun_dir = os.path.join(assets_dir, "guns")
walls_dir = os.path.join(assets_dir, "walls")
wall_list = os.listdir(walls_dir)

launcher_dir = os.path.join(gun_dir, "launcher")
launcher_list = os.listdir(launcher_dir)

shotgun_dir = os.path.join(gun_dir, "shotgun")
shotgun_list = os.listdir(shotgun_dir)

victory_screen = pygame.image.load(os.path.join(assets_dir, "victory.jpg"))
victory_screen = pygame.transform.scale(victory_screen, (screen_width, screen_height))

defeat_screen = pygame.image.load(os.path.join(assets_dir, "defeat.jpg"))
defeat_screen = pygame.transform.scale(defeat_screen, (screen_width, screen_height))

textures = []
projectiles = []

color_averages = []

for i in wall_list:
    if ".png" in i:
        image_path = os.path.join(walls_dir, i)
        textures.append(pygame.image.load(image_path).convert())


launcher_charge = []
burrito_launcher = pygame.transform.scale(pygame.image.load(os.path.join(launcher_dir, "gun.png")).convert_alpha(), (600, 400))

for i in launcher_list:
    if "charge" in i:
        image_path = os.path.join(launcher_dir, i)
        launcher_charge.append(pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (480, 320)))

shotgun_fire = []
burrito_shotgun = pygame.transform.scale(pygame.image.load(os.path.join(shotgun_dir, "gun.png")).convert_alpha(), (306, 450))
bs_ammo = pygame.transform.scale(pygame.image.load(os.path.join(shotgun_dir, "ammo.png")).convert_alpha(), (306, 450))

for i in shotgun_list:
    if "fire" in i:
        image_path = os.path.join(shotgun_dir, i)
        shotgun_fire.append(pygame.transform.scale(pygame.image.load(image_path).convert_alpha(), (306, 450)))


dude = pygame.image.load(os.path.join(sprites_dir, "dude.png")).convert_alpha()
dude_back = pygame.image.load(os.path.join(sprites_dir, "dude_back.png")).convert_alpha()
dude_side = pygame.image.load(os.path.join(sprites_dir, "dude_side.png")).convert_alpha()
dude_side2 = pygame.image.load(os.path.join(sprites_dir, "dude_side2.png")).convert_alpha()

tree = pygame.image.load(os.path.join(sprites_dir, "tree.png")).convert_alpha()
burrito = pygame.image.load(os.path.join(sprites_dir, "burrito.png")).convert_alpha()


type2sprite = {
        1: dude,
        1.1: dude_back,
        1.2: dude_side,
        1.3: dude_side2,
        2: tree,
        3: burrito
    }

map_created = False


def set_dead_squares(array):
    rows = len(array)
    cols = len(array[0])

    def has_nearby_zero(row, col):
        for dr in range(row-2, row+3):
            for dc in range(col-2, col+3):
                try:
                    if array[dr][dc] > 0:
                        return True
                except IndexError:
                    pass
        return False

    updated_array = [[17 if array[row][col] == 0 and not has_nearby_zero(row, col) else array[row][col] for col in range(cols)] for row in range(rows)]

    return updated_array


with open("Map", "r") as f:
    map_lines = f.readlines()

str2int = {
    ",": 10,
    ".": 11,
    "/": 12,
    "<": 13,
    ">": 14,
    "?": 15,
    ":": 16
}

int2str = {
    10: ",",
    11: ".",
    12: "/",
    13: "<",
    14: ">",
    15: "?",
    16: ":"
}

level = typed.List()
tile_map = []
for line in map_lines:
    map_row1 = []
    for char in line.strip():
        try:
            map_row1.append(int(char))
        except ValueError:
            map_row1.append(str2int[char])
    if map_row1:
        level.append(map_row1)
        tile_map.append(map_row1)

dead_squares = typed.List(set_dead_squares(tile_map))

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
        self.x = 96
        self.y = 96
        self.z = 0
        self.oldx = self.x
        self.oldy = self.y
        self.speed = 3
        self.rotation = 0
        self.ray_angle = 270
        self.fov = 60
        self.you_win = False
        self.you_lose = False
        self.isSprinting = 0
        self.view_bob_offset = 0.0
        self.view_bob_speed = 0.1
        self.bob_height = 5
        self.mouse_sensitivity = 4
        self.settings = False
        self.moved = False
        self.health = 100
        self.can_shotgun = []
        self.breaking = False
        self.crosshair = (0, 0, 0)

    def update(self):

        self.view_bob_speed = 0.01 * self.speed / self.speed

        self.view_bob_offset = math.sin(pygame.time.get_ticks() * self.view_bob_speed) * player.bob_height

        if self.isSprinting > 0:
            self.isSprinting -= 1
        else:
            self.speed = 3

        if self.health <= 0:
            player.you_lose = True

        self.can_shotgun.clear()
        self.breaking = False

    def ui(self):
        pygame.draw.rect(screen, (150, 150, 150), (10, 998, 300, 75))

        bar_x = 0
        bar_color = (0, 255, 0)

        if 50 >= self.health > 10:
            bar_color = (255, 165, 0)
        elif self.health <= 10:
            bar_color = (255, 0, 0)

        for number in range(0, self.health):
            pygame.draw.rect(screen, bar_color, (20 + bar_x, 1008, 3, 55))
            bar_x += 2.8

    def collision(self, dx, dy):
        global level

        new_x = self.x + dx
        new_y = self.y + dy

        final_x = self.x
        final_y = self.y

        row_index, col_index = sprite.get_index(self.y, self.x)
        new_row, new_col = sprite.get_index(new_y, new_x)

        try:
            if tile_map[row_index][new_col] == 0:
                final_x += dx
                self.moved = True

            if tile_map[new_row][col_index] == 0:
                final_y += dy
                self.moved = True

            if tile_map[new_row][new_col] == 16:
                self.you_win = True

            if tile_map[new_row][new_col] > 0:
                self.speed = 4

            if self.breaking:
                tile_map[new_row][new_col] = 0
                level = typed.List(tile_map)
            return final_x, final_y
        except IndexError:
            return self.x, self.y


def random_color():
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)
    return r, g, b


win = Button(((screen_width // 2 - 100), (screen_height // 2 + 65), 200, 50), text="WINNER!!!", hover_color=random_color())
lose = Button(((screen_width // 2 - 100), (screen_height // 2 + 65), 200, 50), text="LOSER LLLLLL", color=(64, 64, 64), hover_color=(150, 0, 0))


@njit(fastmath=True)
def cast_walls(angle, iteration, lvl_map, dead_map, x, y, z, fov, player_rot, ray_num):
    end = [x, y]
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    rdx = math.sin(math.radians(player_rot))
    rdy = math.cos(math.radians(player_rot))
    fix_fish_eye = rdx * cos_angle + rdy * sin_angle
    total_skipped = 0

    translucent = False

    for i in range(10000):
        row_index = int(end[1] / tile_size)
        col_index = int(end[0] / tile_size)

        if dead_map[row_index][col_index] == 17:
            total_skipped += 8

        if lvl_map[row_index][col_index] > 0:

            ray_x = iteration * (screen_width / fov)
            wall_type = lvl_map[row_index][col_index]

            dist = fix_fish_eye * (i + total_skipped)
            dist = int(abs(dist))

            wall_height = int(10000 / (dist + 1))

            wall_top = int(screen_height / 2 - wall_height / 2)
            wall_bottom = wall_top + wall_height

            wall_top -= (wall_height * z)
            wall_bottom -= (wall_height * z)

            if wall_type == 10:
                translucent = True

            if wall_type != 10 or ray_num % 2 != 0:
                return ray_x, wall_top, wall_bottom, wall_height, end[0], end[1], dist, wall_type, translucent

        end[0] = x + (i + total_skipped) * cos_angle
        end[1] = y + (i + total_skipped) * sin_angle

    return 0, 0, 0, 0, 0, 0, 0, 0, False


def render_walls():
    screen.fill((100, 210, 255))
    pygame.draw.rect(screen, (100, 100, 100), (0, screen_height/2 + -player.z*10, screen_width, screen_height))
    x = player.x
    y = player.y

    it = 0
    ray_num = 0
    deg = player.ray_angle - (player.fov // 2)
    for i in range(screen_width // 2 + 1):
        # row = ray_x, wall_top, wall_bottom, wall_height, end[0], end[1], dist, wall_type, translucent

        try:
            row = cast_walls(math.radians(round(deg, 2)), it, level, dead_squares, x, y, player.z, player.fov, player.rotation, ray_num)
            tile_type = textures[row[7] - 1]
            tile_x = ((row[4] + row[5]) / tile_size) % 1
            tile_x = math.floor(tile_x * 16)
            wall_surf = tile_type.subsurface((tile_x, 0, 1, 16))

            if row[8]:
                transWallSurf = pygame.transform.scale(wall_surf, (2, row[3]))
            else:
                transWallSurf = pygame.transform.scale(wall_surf, (4, row[3]))

            screen.blit(transWallSurf, (int(row[0]), int(row[1])))

        except IndexError:
            pass

        ray_num += 1
        it += player.fov / (screen_width / 2 + 1)
        deg += player.fov / (screen_width / 2 + 1)


def save():
    global level, dead_squares
    with open('map', 'w') as f:
        map_copy = deepcopy(tile_map)
        for i in range(len(map_copy)):
            for j in range(len(map_copy[0])):
                if map_copy[i][j] >= 10:
                    map_copy[i][j] = int2str[map_copy[i][j]]
        for i in map_copy:
            f.write(''.join(map(str, i)) + '\n')
        level = typed.List(tile_map)

    if sprite_list:
        json_sprites = [sp.to_json() for sp in sprite_list if isinstance(sp, sprite.Sprite)]

        with open("sprite_positions.json", 'w') as sp_pos:
            json.dump(json_sprites, sp_pos, indent=2)
    dead_squares = typed.List(set_dead_squares(tile_map))


running = True

player = Player()

with open("settings.json", 'r') as file:
    try:
        json_data = json.load(file)
        player.mouse_sensitivity = json_data["mouse_sensitivity"]
        player.bob_height = json_data["view_bob"]/100
        player.x = json_data["x"]
        player.y = json_data["y"]
    except json.decoder.JSONDecodeError:
        pass


burrito_launcher = BurritoLauncher(burrito_launcher, launcher_charge)
burrito_shotgun = BurritoShotgun(burrito_shotgun, bs_ammo, shotgun_fire)


def main():
    global running, canChange
    pygame.mouse.set_visible(False)
    pygame.mouse.set_pos(screen_width // 2, screen_height // 2)
    prev_mousePos = pygame.mouse.get_pos()[0]
    accumulated_change = 0
    current_gun = 0
    start_ticks = 0
    current_tick = 0
    show_particles = 0
    is_clicking = False

    particle_info = (-100, sprite.Sprite(-5000, -5000, 1, 1))

    save()

    while running:

        player.update()
        render_walls()
        sprite.render_sprites(sprite_list, player, screen, type2sprite, level, projectiles, tile_map)
        pygame.draw.circle(screen, player.crosshair, (screen_width/2-3, screen_height/2), 6)

        if current_gun == 0:
            burrito_launcher.show_gun(is_clicking, int(current_tick - start_ticks), screen)
        else:
            burrito_shotgun.show_gun(screen)
            burrito_shotgun.cooldown -= 1
            if burrito_shotgun.active:
                burrito_shotgun.active = burrito_shotgun.when_launched(screen)

        player.ui()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()

            if not player.you_win and not player.you_lose:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if current_gun == 0:
                            start_ticks = current_tick
                            is_clicking = True
                        elif burrito_shotgun.cooldown <= 0:
                            particle_info = burrito_shotgun.FLAMINGINFERNOBLAZE111111(player)
                            particle_info.append(randint(-50, 70))
                            particle_info.append(randint(-10, 20))
                            burrito_shotgun.active = True
                            burrito_shotgun.cooldown = 60
                            show_particles = 10

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        is_clicking = False
                        if current_gun == 0:
                            burrito_launcher.when_activated(player, current_tick, start_ticks, sprite_list, projectiles)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    player.z = 0
                    player.isSprinting = 30
                    player.speed = 6
                if event.key == pygame.K_ESCAPE:
                    save()
                    pygame.mouse.set_visible(True)
                    from menu import settings
                    if settings():
                        return

                if event.key == pygame.K_h:
                    player.health -= 10

        player.moved = False
        keys = pygame.key.get_pressed()

        if not player.you_win and not player.you_lose:

            mousePos = pygame.mouse.get_pos()[0]
            change = (mousePos - prev_mousePos)
            accumulated_change += change
            player.ray_angle += accumulated_change / player.mouse_sensitivity
            player.rotation -= accumulated_change / player.mouse_sensitivity

            player.rotation %= 360
            player.ray_angle %= 360

            pygame.mouse.set_pos(screen_width // 2, screen_height // 2)

            if change != 0:
                accumulated_change = 0

            dx = player.speed * math.sin(math.radians(player.rotation))
            dy = player.speed * math.cos(math.radians(player.rotation))

            side_dx = (player.speed / 4) * math.sin(math.radians(player.rotation + 90))
            side_dy = (player.speed / 4) * math.cos(math.radians(player.rotation + 90))

            player.oldx = player.x
            player.oldy = player.y

            if keys[pygame.K_SPACE]:
                player.breaking = True
            if keys[pygame.K_w]:
                player.x, player.y = player.collision(-dx, -dy)
            if keys[pygame.K_s]:
                player.x, player.y = player.collision(dx, dy)
            if keys[pygame.K_a]:
                player.x, player.y = player.collision(-side_dx, -side_dy)
            if keys[pygame.K_d]:
                player.x, player.y = player.collision(side_dx, side_dy)
            if keys[pygame.K_x]:
                save()
                pygame.mouse.set_visible(True)
                return

            for i in range(2):
                if keys[pygame.K_1 + i]:
                    current_gun = i

            pygame.mouse.set_pos(screen_width // 2, screen_height // 2)

            if tile_map[int(player.y / tile_size)][int(player.x / tile_size)] > 0:
                player.x = player.oldx
                player.y = player.oldy

            if player.moved:
                player.z += player.view_bob_offset
                if player.z > 0:
                    player.z = 0
            elif player.z < 0:
                player.z += .1

        # damage, sp

        # dist, x, y, screen, damage, font
        sp = particle_info[1]
        if particle_info[0] > 0 and show_particles != 0:
            guns.damage_particle(sp.dist, sp.screen_x, sp.screen_y, sp.screen_x + particle_info[2], sp.screen_y + particle_info[3],
                                 screen, particle_info[0], damage_font, particle_info[2], show_particles)
            show_particles -= 1

        if player.you_win:
            pygame.mouse.set_visible(True)
            screen.blit(victory_screen, (0, 0))
            win.hover_color = random_color()
            if win.button(screen):
                player.you_win = False
                pygame.mouse.set_visible(False)
                player.x = 96
                player.y = 96
                player.z = 0

        if player.you_lose:
            pygame.mouse.set_visible(True)
            screen.blit(defeat_screen, (0, 0))
            if lose.button(screen):
                player.you_lose = False
                player.x = 96
                player.y = 96
                player.z = 0
                player.health = 100
                pygame.mouse.set_pos(1250, 960)
                return
        if int(clock.get_fps()) < 50 and current_tick > 100:
            pass
        pygame.display.update()

        canChange += 1
        current_tick += .1

        clock.tick(60)


if __name__ == '__main__':
    from menu import menu
    menu()
