from game import *

help = Button(1098, 714, '?', 28, 28)
done = Button((screen_width//2 - 100), (screen_height//2 + 100), 'Done', 200, 50)

l_a = Button(1132, (screen_height//2 + 20), '<', 20, 30)
r_a = Button(880, (screen_height//2 + 20), '>', 20, 30)

set1 = Button(905, 20, "", 100, 100)
set2 = Button(1030, 20, "", 100, 100)
set3 = Button(905, 145, "", 100, 100)
set4 = Button(1030, 145, "", 100, 100)
set5 = Button(905, 270, "", 100, 100)
set6 = Button(1030, 270, "", 100, 100)
set7 = Button(905, 395, "", 100, 100)
set8 = Button(1030, 395, "", 100, 100)
set9 = Button(968, 520, "", 100, 100)

walls = Button(905, 650, "walls", 100, 50)
npcs = Button(1030, 650, "npcs", 100, 50)

setdude = Button(905, 20, "", 100, 100)
settree = Button(1030, 20, "", 100, 100)
setburrito = Button(905, 145, "", 100, 100)


def instructions():
    pygame.draw.rect(screen, (255, 236, 150), (32, 32, 1088, 704))
    one = font.render("1 - 9 Set Draw Mode", True, (0, 0, 0))
    c = font.render("C - Reset board", True, (0, 0, 0))
    esc = font.render("Esc - Back to the menu", True, (0, 0, 0))
    lc = font.render("Left Click - Draw", True, (0, 0, 0))
    rc = font.render("Right Click - Erase", True, (0, 0, 0))

    screen.blit(one, (64, 64))
    screen.blit(c, (64, 96))
    screen.blit(esc, (64, 128))
    screen.blit(lc, (64, 160))
    screen.blit(rc, (64, 192))


def map_maker():
    global sprites
    editor_running = True
    tile_type = 1
    sprite_type = 1
    show_help = False
    show_ui = False
    can_open = 0
    sprite_place = 0
    mode = True

    type2sprite = {
        1: dude,
        2: tree,
        3: burrito
    }

    while editor_running:

        cf = str(int(clock.get_fps()))

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
            menu()
        for i in range(len(textures) + 1):
            if keys[pygame.K_0 + i]:
                tile_type = i
        if keys[pygame.K_c]:
            for i in range(len(tile_map)):
                for j in range(len(tile_map[0])):
                    if i == 0 or i == len(tile_map) - 1 or j == 0 or j == len(tile_map[0]) - 1:
                        tile_map[i][j] = 1
                    else:
                        tile_map[i][j] = 0
            sprites = []
        can_place = True
        for i in range(len(tile_map)):
            for j in range(len(tile_map[0])):
                if level[i][j] == 5:
                    can_place = False
        # Fill in tile
        if not show_ui and can_open > 10:
            if mode:
                if len(tile_map) > mousePos[1] // tile_size > 0 and len(tile_map[0]) > mousePos[0] // tile_size > 0:
                    if mouse[0]:
                        if tile_type != 5:
                            level[int(mousePos[1] / tile_size)][int(mousePos[0] / tile_size)] = tile_type
                        else:
                            if can_place:
                                level[int(mousePos[1] / tile_size)][int(mousePos[0] / tile_size)] = 5
                    if mouse[2]:
                        level[int(mousePos[1] / tile_size)][int(mousePos[0] / tile_size)] = 0
            if not mode:
                if mouse[0] and len(sprites) < 5 and sprite_place >= 10:
                    sprites.append(Sprite(mousePos[0], mousePos[1], type2sprite[sprite_type]))
                    sprite_place = 0

            save()

        screen.fill((64, 64, 64))
        x = 0
        y = 0
        for i in tile_map:
            if i:
                for j in i:
                    if level[int(y / tile_size)][int(x / tile_size)] > 0:
                        try:
                            map_color = textures[level[int(y / tile_size)][int(x / tile_size)] - 1].get_at((1, 0))
                        except IndexError:
                            level[int(y / tile_size)][int(x / tile_size)] = 0
                            map_color = textures[0].get_at((1, 0))
                        pygame.draw.rect(screen, map_color, (x, y, tile_size, tile_size))
                    x += tile_size
            x = 0
            y += tile_size

        for sp in sprites:
            screen.blit(pygame.transform.scale(sp.type, (16, 16)), (sp.x - 8, sp.y + 8))

        pygame.draw.rect(screen, (0, 0, 255), (192, 192, 16, 16))

        if not show_ui:
            if l_a.x <= mousePos[0] <= l_a.x + l_a.width and l_a.y <= mousePos[1] <= l_a.y + l_a.height:
                l_a.draw((80, 80, 80))
                if mouse[0]:
                    show_ui = True
            else:
                l_a.draw((150, 150, 150))

        if show_ui:

            pygame.draw.rect(screen, (40, 40, 40), (880, 0, 372, 768))

            if help.detect_collide(mousePos[0], mousePos[1]):
                help.draw((150, 0, 0))
                if mouse[0]:
                    show_help = True
            else:
                help.draw((200, 0, 0))
            if mode:
                if set1.detect_collide(mousePos[0], mousePos[1]):
                    set1.draw((80, 80, 80))
                    if mouse[0]:
                        tile_type = 1
                elif tile_type == 1:
                    set1.draw((20, 20, 20))
                else:
                    set1.draw((150, 150, 150))

                if set2.detect_collide(mousePos[0], mousePos[1]):
                    set2.draw((80, 80, 80))
                    if mouse[0]:
                        tile_type = 2
                elif tile_type == 2:
                    set2.draw((20, 20, 20))
                else:
                    set2.draw((150, 150, 150))

                if set3.detect_collide(mousePos[0], mousePos[1]):
                    set3.draw((80, 80, 80))
                    if mouse[0]:
                        tile_type = 3
                elif tile_type == 3:
                    set3.draw((20, 20, 20))
                else:
                    set3.draw((150, 150, 150))

                if set4.detect_collide(mousePos[0], mousePos[1]):
                    set4.draw((80, 80, 80))
                    if mouse[0]:
                        tile_type = 4
                elif tile_type == 4:
                    set4.draw((20, 20, 20))
                else:
                    set4.draw((150, 150, 150))

                if set5.detect_collide(mousePos[0], mousePos[1]):
                    set5.draw((80, 80, 80))
                    if mouse[0]:
                        tile_type = 6
                elif tile_type == 6:
                    set5.draw((20, 20, 20))
                else:
                    set5.draw((150, 150, 150))

                if set6.detect_collide(mousePos[0], mousePos[1]):
                    set6.draw((80, 80, 80))
                    if mouse[0]:
                        tile_type = 7
                elif tile_type == 7:
                    set6.draw((20, 20, 20))
                else:
                    set6.draw((150, 150, 150))

                if set7.detect_collide(mousePos[0], mousePos[1]):
                    set7.draw((80, 80, 80))
                    if mouse[0]:
                        tile_type = 8
                elif tile_type == 8:
                    set7.draw((20, 20, 20))
                else:
                    set7.draw((150, 150, 150))

                if set8.detect_collide(mousePos[0], mousePos[1]):
                    set8.draw((80, 80, 80))
                    if mouse[0]:
                        tile_type = 9
                elif tile_type == 9:
                    set8.draw((20, 20, 20))
                else:
                    set8.draw((150, 150, 150))

                if not can_place:
                    set9.draw((150, 0, 0))
                elif set9.detect_collide(mousePos[0], mousePos[1]):
                    set9.draw((80, 80, 80))
                    if mouse[0]:
                        tile_type = 5
                elif tile_type == 5:
                    set9.draw((20, 20, 20))
                else:
                    set9.draw((150, 150, 150))

            else:
                if setdude.detect_collide(mousePos[0], mousePos[1]):
                    setdude.draw((80, 80, 80))
                    if mouse[0]:
                        sprite_type = 1
                elif sprite_type == 1:
                    setdude.draw((20, 20, 20))
                else:
                    setdude.draw((150, 150, 150))

                if settree.detect_collide(mousePos[0], mousePos[1]):
                    settree.draw((80, 80, 80))
                    if mouse[0]:
                        sprite_type = 2
                elif sprite_type == 2:
                    settree.draw((20, 20, 20))
                else:
                    settree.draw((150, 150, 150))

                if setburrito.detect_collide(mousePos[0], mousePos[1]):
                    setburrito.draw((80, 80, 80))
                    if mouse[0]:
                        sprite_type = 3
                elif sprite_type == 3:
                    setburrito.draw((20, 20, 20))
                else:
                    setburrito.draw((150, 150, 150))

            if walls.detect_collide(mousePos[0], mousePos[1]):
                walls.draw((80, 80, 80))
                if mouse[0]:
                    mode = True
            elif mode:
                walls.draw((50, 50, 50))
            else:
                walls.draw((150, 150, 150))

            if npcs.detect_collide(mousePos[0], mousePos[1]):
                npcs.draw((80, 80, 80))
                if mouse[0]:
                    mode = False
            elif not mode:
                npcs.draw((50, 50, 50))
            else:
                npcs.draw((150, 150, 150))

            if r_a.detect_collide(mousePos[0], mousePos[1]):
                r_a.draw((80, 80, 80))
                if mouse[0]:
                    show_ui = False
                    can_open = 0
            else:
                r_a.draw((150, 150, 150))

            if mode:
                ui_1 = pygame.transform.scale(textures[0], (80, 80))
                screen.blit(ui_1, (915, 30))

                ui_2 = pygame.transform.scale(textures[1], (80, 80))
                screen.blit(ui_2, (1040, 30))

                ui_3 = pygame.transform.scale(textures[2], (80, 80))
                screen.blit(ui_3, (915, 155))

                ui_4 = pygame.transform.scale(textures[3], (80, 80))
                screen.blit(ui_4, (1040, 155))

                ui_5 = pygame.transform.scale(textures[5], (80, 80))
                screen.blit(ui_5, (915, 280))

                ui_6 = pygame.transform.scale(textures[6], (80, 80))
                screen.blit(ui_6, (1040, 280))

                ui_7 = pygame.transform.scale(textures[7], (80, 80))
                screen.blit(ui_7, (915, 405))

                ui_8 = pygame.transform.scale(textures[8], (80, 80))
                screen.blit(ui_8, (1040, 405))

                ui_9 = pygame.transform.scale(textures[4], (80, 80))
                screen.blit(ui_9, (978, 530))

            else:
                ui_1 = pygame.transform.scale(dude, (80, 80))
                screen.blit(ui_1, (915, 30))

                ui_2 = pygame.transform.scale(tree, (80, 80))
                screen.blit(ui_2, (1040, 30))

                ui_3 = pygame.transform.scale(burrito, (80, 80))
                screen.blit(ui_3, (915, 155))

        if show_help:
            instructions()

            if done.x <= mousePos[0] <= done.x + done.width and done.y <= mousePos[1] <= done.y + done.height:
                done.draw((0, 150, 0))
                if mouse[0]:
                    show_help = False
            else:
                done.draw((0, 255, 0))

        if can_open <= 150:
            can_open += 1

        if sprite_place <= 10:
            sprite_place += 1

        pygame.display.set_caption("Fps: " + str(cf) + "/30")
        pygame.display.update()
        save()
        clock.tick(30)
