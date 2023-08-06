import math
import pygame
from sprite import Sprite


class Gun:
    def __init__(self, damage, ammo_range, animation, image, launch_speed):
        self.damage = damage
        self.range = ammo_range
        self.image = image
        self.launch_speed = launch_speed
        self.animation = animation
        self.ani_len = len(animation)

    def launch(self, x, y, angle, sprite_list, projectile_list):
        new_proj = Projectile(x, y, angle, 3, self.range, self.launch_speed)
        sprite_list.append(new_proj)
        projectile_list.append(new_proj)


class BurritoLauncher(Gun):
    def __init__(self, image, animation):
        super().__init__(100, 75, animation, image, 2)

    def when_activated(self, player, current_tick, start_tick, sp_list, p_list):
        radians_angle = math.radians(player.ray_angle)
        self.launch_speed += int(current_tick - start_tick)//2
        self.range += int(current_tick - start_tick) * 2
        self.damage += int(current_tick - start_tick) * 2
        self.launch(player.x + 10 * math.cos(radians_angle), player.y + 10 * math.sin(radians_angle), radians_angle, sp_list, p_list)
        self.launch_speed = 2
        self.range = 50
        self.damage = 50

    def show_gun(self, is_clicking, ticks, screen):
        screen.blit(self.image, (650, 450))
        if is_clicking:
            screen.blit(self.animation[ticks % self.ani_len], (633, 450))


class BurritoShotgun(Gun):
    def __init__(self, image, image2, animation):
        super().__init__(100, 75, animation, image, 2)
        self.frame_length = 2
        self.current_frame = 0
        self.active = False
        self.cooldown = 60
        self.image2 = image2

    def show_gun(self, screen):
        screen.blit(self.image, (468, 395))
        if self.cooldown <= 0:
            screen.blit(self.image2, (468, 395))

    def FLAMINGINFERNOBLAZE111111(self, player):
        for sp in player.can_shotgun:
            if isinstance(sp, Sprite):
                if sp.dist <= self.range:
                    sp.type = 3

    def when_launched(self, screen):

        screen.blit(self.animation[self.current_frame], (468, 395))

        if self.frame_length == 0:
            self.current_frame += 1
            self.frame_length = 2

        if self.current_frame > self.ani_len - 1:
            self.current_frame = 0
            return False

        self.frame_length -= 1

        return True


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
        for i in range(self.speed):
            self.x += i * math.cos(self.angle)
            self.y += i * math.sin(self.angle)
            self.hitbox = pygame.Rect(self.x, self.y, 4, 4)
            if self.range == 0:
                sprite_list.remove(self)
                projectiles.remove(self)
                break

            if tile_map[int(self.y / 16)][int(self.x / 16)] > 0:
                sprite_list.remove(self)
                projectiles.remove(self)
                break

            for sp in sprite_list:
                if isinstance(sp, Sprite):
                    if sp.hitbox.colliderect(self.hitbox):
                        sp.type = 3

        self.range -= 1
