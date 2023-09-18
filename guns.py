import math
import pygame
from random import randint, seed
from sprite import Sprite


def damage_particle(dist, x, y, dmgX, dmgY, screen, damage, font, random_num, count):
    seed(random_num*damage)
    scale = 2000 / (dist+1)
    center_x, center_y = x + scale, y
    count *= 1.5
    for i in range(10):
        rand_x, rand_y = randint(int(-scale), int(scale)), randint(0, int(scale*2))
        if rand_x > 0:
            rand_x += 10 - count
        else:
            rand_x -= 10 - count

        if rand_y > int(scale):
            rand_y += 10 - count
        else:
            rand_y -= 10 - count

        pygame.draw.rect(screen, (255, 0, 0), (center_x+rand_x, center_y+rand_y, scale/2, scale/2))
    font.render_to(screen, (dmgX, dmgY), str(math.floor(damage)), (255, 255, 255), size=scale)


class Gun:
    def __init__(self, damage, ammo_range, animation, image, launch_speed):
        self.damage = damage
        self.range = ammo_range
        self.image = image
        self.launch_speed = launch_speed
        self.animation = animation
        self.ani_len = len(animation)

    def launch(self, x, y, angle, sprite_list, projectile_list, damage):
        new_proj = Projectile(x, y, angle, 3, self.range, self.launch_speed, damage)
        sprite_list.append(new_proj)
        projectile_list.append(new_proj)


class BurritoLauncher(Gun):
    def __init__(self, image, animation):
        super().__init__(100, 75, animation, image, 2)

    def when_activated(self, player, current_tick, start_tick, sp_list, p_list):
        radians_angle = math.radians(player.ray_angle)
        self.launch_speed += int(current_tick - start_tick) // 2
        self.range += int(current_tick - start_tick) * 2
        self.damage += int(current_tick - start_tick)

        self.launch(player.x, player.y, radians_angle, sp_list, p_list, self.damage)

        self.damage = 100
        self.launch_speed = 2
        self.range = 50

    def show_gun(self, is_clicking, ticks, screen):
        screen.blit(self.image, (1180, 680))
        if is_clicking:
            screen.blit(self.animation[ticks % self.ani_len], (1180, 680))


class BurritoShotgun(Gun):
    def __init__(self, image, image2, animation):
        super().__init__(200, 75, animation, image, 2)
        self.frame_length = 2
        self.current_frame = 0
        self.active = False
        self.cooldown = 60
        self.image2 = image2

    def show_gun(self, screen):
        screen.blit(self.image, (805, 630))
        if self.cooldown <= 0:
            screen.blit(self.image2, (805, 630))

    def FLAMINGINFERNOBLAZE111111(self, player):
        if player.can_shotgun:
            for sp in player.can_shotgun:
                damage = (self.damage / (sp.dist/10) + sp.dist/2)
                sp.health -= damage
                if sp.health <= 0:
                    sp.type = 3

                return [damage, sp]
        else:
            return [0, 0]

    def when_launched(self, screen):

        screen.blit(self.animation[self.current_frame], (805, 630))

        if self.frame_length == 0:
            self.current_frame += 1
            self.frame_length = 2

        if self.current_frame > self.ani_len - 1:
            self.current_frame = 0
            return False

        self.frame_length -= 1

        return True


class Projectile:
    def __init__(self, x, y, angle, type, projectile_range, speed, damage):
        self.x = x
        self.y = y
        self.angle = angle
        self.type = type
        self.range = projectile_range
        self.speed = speed
        self.damage = damage
        self.dist = 0
        self.hitbox = pygame.Rect(self.x, self.y, 4, 4)

    def update(self, sprite_list, projectiles, tile_map, _):
        for i in range(self.speed):
            self.x += i * math.cos(self.angle)
            self.y += i * math.sin(self.angle)
            self.hitbox = pygame.Rect(self.x, self.y, 4, 4)
            if self.range == 0:
                sprite_list.remove(self)
                projectiles.remove(self)
                break

            try:
                if tile_map[int(self.y / 16)][int(self.x / 16)] > 0:
                    sprite_list.remove(self)
                    projectiles.remove(self)
                    break
            except IndexError:
                pass

            try:
                for sp in sprite_list:
                    if isinstance(sp, Sprite):
                        if sp.hitbox.colliderect(self.hitbox):
                            sprite_list.remove(self)
                            projectiles.remove(self)
                            sp.health -= self.damage
                            if sp.health <= 0:
                                sp.type = 3
            except ValueError:
                pass

        self.range -= 1
