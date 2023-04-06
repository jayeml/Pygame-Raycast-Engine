from game import *


def instructions():
    pygame.draw.rect(screen, (255, 236, 150), (32, 32, 1088, 704))
    one = font.render("1 - Set draw mode to cobblestone", True, (0, 0, 0))
    two = font.render("2 - Set draw mode to mossy cobblestone", True, (0, 0, 0))
    three = font.render("3 - Set draw mode to iron wall", True, (0, 0, 0))
    four = font.render("4 - Set draw mode to wood planks", True, (0, 0, 0))
    five = font.render("5 - Set draw mode to end goal", True, (0, 0, 0))
    c = font.render("C - Reset board", True, (0, 0, 0))
    esc = font.render("Esc - Back to the menu", True, (0, 0, 0))
    lc = font.render("Left Click - Draw", True, (0, 0, 0))
    rc = font.render("Right Click - Erase", True, (0, 0, 0))
    warning = font.render("LARGE OPEN AREAS MAY CRASH GAME!", True, (255, 0, 0))

    warning_rect = warning.get_rect(center=(screen_width // 2, screen_height // 2))

    screen.blit(one, (64, 64))
    screen.blit(two, (64, 96))
    screen.blit(three, (64, 128))
    screen.blit(four, (64, 160))
    screen.blit(five, (64, 192))
    screen.blit(c, (64, 224))
    screen.blit(esc, (64, 256))
    screen.blit(lc, (64, 288))
    screen.blit(rc, (64, 320))
    screen.blit(warning, warning_rect)


def map_maker():
    editor_running = True
    tile_type = 1
    show_help = False
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

        if keys[pygame.K_1]:
            tile_type = 1
        if keys[pygame.K_2]:
            tile_type = 2
        if keys[pygame.K_3]:
            tile_type = 3
        if keys[pygame.K_4]:
            tile_type = 4
        if keys[pygame.K_5]:
            tile_type = 5
        if keys[pygame.K_c]:
            for i in range(len(tile_map)):
                for j in range(len(tile_map[0])):
                    if i == 0 or i == len(tile_map)-1 or j == 0 or j == len(tile_map[0]) - 1:
                        tile_map[i][j] = 1
                    else:
                        tile_map[i][j] = 0
        if len(tile_map) > mousePos[1]//tile_size > 0 and len(tile_map[0]) > mousePos[0]//tile_size > 0:
            if mouse[0]:
                if tile_type != 5:
                    level[int(mousePos[1]/tile_size)][int(mousePos[0]/tile_size)] = tile_type
                else:
                    can_place = True
                    for i in range(len(tile_map)):
                        for j in range(len(tile_map[0])):
                            if level[i][j] == 5:
                                can_place = False
                    if can_place:
                        level[int(mousePos[1] / tile_size)][int(mousePos[0] / tile_size)] = 5
            if mouse[2]:
                level[int(mousePos[1]/tile_size)][int(mousePos[0]/tile_size)] = 0
            save()

        screen.fill((64, 64, 64))
        x = 0
        y = 0
        for i in tile_map:
            if i:
                for j in i:
                    if level[int(y / tile_size)][int(x / tile_size)] > 0:
                        if level[int(y / tile_size)][int(x / tile_size)] == 1:
                            map_color = (bricks1.get_at((1, 1)))
                        elif level[int(y / tile_size)][int(x / tile_size)] == 2:
                            map_color = (bricks2.get_at((1, 0)))
                        elif level[int(y / tile_size)][int(x / tile_size)] == 3:
                            map_color = (bricks3.get_at((1, 1)))
                        elif level[int(y / tile_size)][int(x / tile_size)] == 4:
                            map_color = (planks1.get_at((1, 1)))
                        elif level[int(y / tile_size)][int(x / tile_size)] == 5:
                            map_color = (goal.get_at((1, 1)))
                        pygame.draw.rect(screen, map_color, (x, y, tile_size, tile_size))
                    else:
                        pygame.draw.rect(screen, (200, 200, 200), (x, y, tile_size, tile_size), 1)
                    x += tile_size

            x = 0
            y += tile_size

        pygame.draw.rect(screen, (255, 0, 0), (192, 192, 16, 16))

        if show_help:
            instructions()

        if help.x <= mousePos[0] <= help.x + help.width and help.y <= mousePos[1] <= help.y + help.height:
            help.draw((150, 0, 0))
            if mouse[0]:
                show_help = True
        else:
            help.draw((200, 0, 0))

        if show_help:
            if done.x <= mousePos[0] <= done.x + done.width and done.y <= mousePos[1] <= done.y + done.height:
                done.draw((0, 150, 0))
                if mouse[0]:
                    show_help = False
            else:
                done.draw((0, 255, 0))
        pygame.display.set_caption("Fps: " + str(cf) + "/30")
        pygame.display.update()
        save()
        clock.tick(30)
