import math
import pygame
from sprite import Sprite


class Gun:
    def __init__(self, damage, ammo_range, image, animation, launch_speed):
        self.damage = damage
        self.range = ammo_range
        self.image = image
        self.launch_speed = launch_speed
        self.animation = animation
        self.ani_len = len(animation)

    def show_gun(self, hasClicked, ticks, screen):
        screen.blit(self.image, (650, 450))
        if hasClicked:
            screen.blit(self.animation[ticks % self.ani_len], (633, 450))

    def launch(self, x, y, angle, sprite_list, projectile_list):
        new_proj = Projectile(x, y, angle, 3, self.range, self.launch_speed)
        sprite_list.append(new_proj)
        projectile_list.append(new_proj)


class BurritoLauncher(Gun):
    def __init__(self, image, animation):
        super().__init__(50, 100, image, animation, 2)

    def when_launched(self, player, current_tick, start_tick, sp_list, p_list):
        self.launch_speed += int(current_tick - start_tick) * 2
        self.range += int(current_tick - start_tick) * 2
        self.damage += int(current_tick - start_tick) * 2
        self.launch(player.x + .0001, player.y + .0001, math.radians(player.ray_angle), sp_list, p_list)
        self.launch_speed = 2
        self.range = 50
        self.damage = 50
        player.speed = 5


# noinspection SpellCheckingInspection
class Projectile:
    def __init__(self, x, y, angle, type, projectile_range, speed):
        self.x = x
        self.y = y
        self.angle = angle
        self.type = type
        self.range = projectile_range
        self.speed = speed
        self.dist = 0
        self.hitbox = pygame.Rect(self.x, self.y, 4, 4)

    def update(self, sprite_list, projectiles, tile_map):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.hitbox = pygame.Rect(self.x, self.y, 4, 4)
        self.range -= 1
        if self.range == 0:
            sprite_list.remove(self)
            projectiles.remove(self)
        try:
            if tile_map[int(self.y / 16)][int(self.x / 16)] > 0:
                sprite_list.remove(self)
                projectiles.remove(self)

        except IndexError:
            sprite_list.remove(self)
            projectiles.remove(self)

        except ValueError:
            pass

    def collision(self, sprite_list):
        for sp in sprite_list:
            if isinstance(sp, Sprite):
                if sp.hitbox.colliderect(self.hitbox):
                    sp.type = 3
