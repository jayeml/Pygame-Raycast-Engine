from game import *
from sprite import Sprite
from Widgets.label import Label


help = Button((1098, 714, 28, 28), text='?', color=(255, 0, 0), press_color=(255, 0, 0))
done = Button(((screen_width//2 - 100), (screen_height//2 + 100), 200, 50), text='Done', color=(0, 255, 0),
              hover_color=(0, 155, 0))

set1 = Button((903, 20, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80))
set2 = Button((1028, 20, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80))
set3 = Button((903, 145, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80))
set4 = Button((1028, 145, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80))
set5 = Button((903, 270, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80))
set6 = Button((1028, 270, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80))
set7 = Button((903, 395, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80))
set8 = Button((1028, 395, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80))
set9 = Button((966, 520, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80))

set_walls = [set1, set2, set3, set4, set5, set6, set7, set8]

walls = Button((905, 650, 100, 50), text="walls", color=(150, 150, 150), hover_color=(80, 80, 80))
npcs = Button((1030, 650, 100, 50), text="npcs", color=(150, 150, 150), hover_color=(80, 80, 80))

setdude = Button((903, 20, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80))
settree = Button((1028, 20, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80))
setburrito = Button((903, 145, 100, 100), color=(150, 150, 150), hover_color=(80, 80, 80))

set_sprite = [setdude, settree, setburrito]


def instructions():
    pygame.draw.rect(screen, (255, 236, 150), (32, 32, 1088, 704))
    one = Label("1 - 9 Set Draw Mode", x=64, y=64)
    c = Label("C - Clear board", x=64, y=96)
    c_ctrl = Label("Ctrl + C - Clear sprites", x=64, y=128)
    esc = Label("Esc - Back to the menu", x=64, y=160)
    lc = Label("Left Click - Draw", x=64, y=192)
    rc = Label("Right Click - Erase", x=64, y=224)

    one.show(screen)
    c.show(screen)
    c_ctrl.show(screen)
    esc.show(screen)
    lc.show(screen)
    rc.show(screen)


def map_maker():
    editor_running = True
    tile_type = 1
    sprite_type = 0
    show_help = False
    sprite_place = 0
    mode = True

    pygame.display.set_caption("Level Editor")

    while editor_running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                editor_running = False
                save()
                quit()

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
            for sp in sprite_list:
                sprite_list.remove(sp)

        can_place = True
        for i in range(len(tile_map)):
            for j in range(len(tile_map[0])):
                if level[i][j] == 9:
                    can_place = False
        # Fill in tile
        if mode:
            if len(tile_map) > mousePos[1] // 12 > 0 and len(tile_map[0]) > mousePos[0] // 12 > 0:
                if mouse[0]:
                    if tile_type != 9:
                        level[int(mousePos[1] / 12)][int(mousePos[0] / 12)] = tile_type
                    else:
                        if can_place:
                            level[int(mousePos[1] / 12)][int(mousePos[0] / 12)] = 9
                if mouse[2]:
                    level[int(mousePos[1] / 12)][int(mousePos[0] / 12)] = 0
        if not mode and sprite_type != 0 and mouse[0] and sprite_place > 10 and mousePos[0] < 876 and mousePos[1] < 768:
            sprite_place = 0
            sprite_list.append(Sprite(mousePos[0] / 12 * 16, mousePos[1] / 12 * 16, sprite_type))

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
            screen.blit(pygame.transform.scale(type2sprite[sp.type], (12, 12)), (sp.x * 12 / 16, sp.y * 12 / 16))

        pygame.draw.rect(screen, (0, 0, 255), (144, 144, 12, 12))

        pygame.draw.rect(screen, (40, 40, 40), (876, 0, 276, 768))

        if help.button(screen):
            show_help = True

        if mode:
            for wall in set_walls:
                if wall.button(screen):
                    tile_type = set_walls.index(wall) + 1
                if tile_type == set_walls.index(wall) + 1:
                    wall.show_toggled(screen, (20, 20, 20))

            if set9.button(screen):
                tile_type = 9
            if tile_type == 9:
                set9.show_toggled(screen, (20, 20, 20))
            if not can_place:
                pygame.draw.rect(screen, (150, 0, 0), (966, 520, 100, 100))

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
            ui_1 = pygame.transform.scale(textures[0], (80, 80))
            screen.blit(ui_1, (913, 30))

            ui_2 = pygame.transform.scale(textures[1], (80, 80))
            screen.blit(ui_2, (1038, 30))

            ui_3 = pygame.transform.scale(textures[2], (80, 80))
            screen.blit(ui_3, (913, 155))

            ui_4 = pygame.transform.scale(textures[3], (80, 80))
            screen.blit(ui_4, (1038, 155))

            ui_5 = pygame.transform.scale(textures[4], (80, 80))
            screen.blit(ui_5, (913, 280))

            ui_6 = pygame.transform.scale(textures[5], (80, 80))
            screen.blit(ui_6, (1038, 280))

            ui_7 = pygame.transform.scale(textures[6], (80, 80))
            screen.blit(ui_7, (913, 405))

            ui_8 = pygame.transform.scale(textures[7], (80, 80))
            screen.blit(ui_8, (1038, 405))

            ui_9 = pygame.transform.scale(textures[8], (80, 80))
            screen.blit(ui_9, (976, 530))

        else:
            ui_1 = pygame.transform.scale(dude, (80, 80))
            screen.blit(ui_1, (913, 30))

            ui_2 = pygame.transform.scale(tree, (80, 80))
            screen.blit(ui_2, (1038, 30))

            ui_3 = pygame.transform.scale(burrito, (80, 80))
            screen.blit(ui_3, (913, 155))

        if show_help:
            instructions()

            if done.button(screen):
                show_help = False

        if sprite_place <= 10:
            sprite_place += 1

        pygame.display.update()
        save()
        clock.tick(30)
