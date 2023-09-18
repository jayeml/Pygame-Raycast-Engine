from main import *
from sprite import Sprite

set_walls = []

for i in range(16):
    if i % 2 == 0:
        x = 1671
    else:
        x = 1796

    y = 20 + (125 * (i//2))

    set_walls.append(Button((x, y, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80)))

walls = Button((1671, 1015, 100, 50), text="walls", color=(150, 150, 150), hover_color=(80, 80, 80))
npcs = Button((1796, 1015, 100, 50), text="npcs", color=(150, 150, 150), hover_color=(80, 80, 80))

setdude = Button((1671, 20, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80))
settree = Button((1796, 20, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80))
setburrito = Button((1671, 145, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80))

set_sprite = [setdude, settree, setburrito]


def map_maker():
    global dead_squares
    editor_running = True
    tile_type = 1
    sprite_type = 0
    sprite_place = 0
    mode = True
    removed = True

    dead_squares = []

    pygame.display.set_caption("Level Editor")

    while editor_running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                editor_running = False
                save()
                quit()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_z:
                    removed = False

        mouse = pygame.mouse.get_pressed()

        mousePos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            save()
            return
        for i in range(len(textures) + 1):
            if keys[pygame.K_0 + i]:
                tile_type = i
        if keys[pygame.K_c] and not keys[pygame.K_LCTRL]:
            for i in range(len(tile_map)):
                for j in range(len(tile_map[0])):
                    if i == 0 or i == len(tile_map) - 1 or j == 0 or j == len(tile_map[0]) - 1:
                        tile_map[i][j] = 1
                    else:
                        tile_map[i][j] = 0

        if keys[pygame.K_c] and keys[pygame.K_LCTRL]:
            sprite_list.clear()

        if keys[pygame.K_z] and keys[pygame.K_LCTRL] and not removed:
            if sprite_list:
                sprite_list.pop()
                removed = True

        # Fill in tile
        if mode:
            if len(tile_map) > mousePos[1] // 12 > 0 and len(tile_map[0]) > mousePos[0] // 12 > 0:
                if mouse[0]:
                    level[int(mousePos[1] / 12)][int(mousePos[0] / 12)] = tile_type
                if mouse[2]:
                    level[int(mousePos[1] / 12)][int(mousePos[0] / 12)] = 0
        if not mode and sprite_type != 0 and mouse[0] and mousePos[0] < 1644 and mousePos[1] < screen_height:
            sprite_place = 0
            sprite_list.append(Sprite(int(mousePos[0] / 12 * 8), int(mousePos[1] / 12 * 8), sprite_type, 180))

        screen.fill((64, 64, 64))
        x = 0
        y = 0
        for i in tile_map:
            if i:
                for j in i:
                    if level[int(y / 12)][int(x / 12)] > 0:
                        try:
                            map_color = color_averages[level[int(y / 12)][int(x / 12)] - 1]
                        except IndexError:
                            level[int(y / 12)][int(x / 12)] = 0
                            map_color = color_averages[0]
                        pygame.draw.rect(screen, map_color, (x, y, 12, 12))
                    x += 12
            x = 0
            y += 12

        for sp in sprite_list:
            if isinstance(sp, Sprite):
                screen.blit(pygame.transform.scale(type2sprite[math.floor(sp.type)], (12, 12)), (sp.x * 12 / 8 - 6, sp.y * 12 / 8  - 6))

        pygame.draw.rect(screen, (0, 0, 255), (144, 144, 12, 12))

        pygame.draw.rect(screen, (40, 40, 40), (1644, 0, 300, screen_height))

        if mode:
            for wall in set_walls:
                if wall.button(screen):
                    tile_type = set_walls.index(wall) + 1
                if tile_type == set_walls.index(wall) + 1:
                    wall.show_toggled(screen, (20, 20, 20))

        else:
            for sprite in set_sprite:
                if sprite.button(screen):
                    sprite_type = set_sprite.index(sprite) + 1
                if sprite_type == set_sprite.index(sprite) + 1:
                    sprite.show_toggled(screen, (20, 20, 20))

        if walls.button(screen):
            mode = True
        if npcs.button(screen):
            sprite_place = 0
            mode = False

        if mode:

            for i in range(16):
                if i % 2 == 0:
                    x = 1681
                else:
                    x = 1806

                y = 30 + (125 * (i // 2))

                image = pygame.transform.scale(textures[i], (80, 80))
                screen.blit(image, (x, y))

        else:
            ui_1 = pygame.transform.scale(dude, (80, 80))
            screen.blit(ui_1, (1681, 30))

            ui_2 = pygame.transform.scale(tree, (80, 80))
            screen.blit(ui_2, (1806, 30))

            ui_3 = pygame.transform.scale(burrito, (80, 80))
            screen.blit(ui_3, (1681, 155))

        if sprite_place <= 10:
            sprite_place += 10

        pygame.display.update()
        clock.tick(60)
        save()
