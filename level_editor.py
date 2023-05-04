from game import *
import subprocess


def instructions():
    pygame.draw.rect(screen, (255, 236, 150), (32, 32, 1088, 704))
    one = font.render("1 - 9 Set Draw Mode", True, (0, 0, 0))
    c = font.render("C - Reset board", True, (0, 0, 0))
    esc = font.render("Esc - Back to the menu", True, (0, 0, 0))
    lc = font.render("Left Click - Draw", True, (0, 0, 0))
    rc = font.render("Right Click - Erase", True, (0, 0, 0))
    warning = font.render("LARGE OPEN AREAS MAY CRASH GAME!", True, (255, 0, 0))

    warning_rect = warning.get_rect(center=(screen_width // 2, screen_height // 2))

    screen.blit(one, (64, 64))
    screen.blit(c, (64, 224))
    screen.blit(esc, (64, 256))
    screen.blit(lc, (64, 288))
    screen.blit(rc, (64, 320))
    screen.blit(warning, warning_rect)


def map_maker():
    editor_running = True
    tile_type = 1
    show_help = False
    can_open = 1000
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
        # Add new texture
        if keys[pygame.K_f] and can_open > 150:
            can_open = 0
            directory_path = "C:\\Users\\lrhar\\PycharmProjects\\3DRaycast\\Assets"

            existing_files = os.listdir(directory_path)

            if len(existing_files) <= 12:

                subprocess.call(['explorer', directory_path])

                while True:

                    new_files = os.listdir(directory_path)

                    added_files = [f for f in new_files if f not in existing_files]
                    if len(added_files) + len(existing_files) == 11:
                        for file in added_files:
                            x = textures.append(pygame.transform.scale(pygame.image.load("Assets\\" + file), (tile_size, tile_size)))
                        break
        # Fill in tile
        if len(tile_map) > mousePos[1] // tile_size > 0 and len(tile_map[0]) > mousePos[0] // tile_size > 0:
            if mouse[0]:
                if tile_type != 5:
                    level[int(mousePos[1] / tile_size)][int(mousePos[0] / tile_size)] = tile_type
                else:
                    can_place = True
                    for i in range(len(tile_map)):
                        for j in range(len(tile_map[0])):
                            if level[i][j] == 5:
                                can_place = False
                    if can_place:
                        level[int(mousePos[1] / tile_size)][int(mousePos[0] / tile_size)] = 5
            if mouse[2]:
                level[int(mousePos[1] / tile_size)][int(mousePos[0] / tile_size)] = 0
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

        pygame.draw.rect(screen, (255, 0, 0), (192, 192, 16, 16))

        if show_help:
            instructions()

        if can_open <= 150:
            can_open += 1

        pygame.display.set_caption("Fps: " + str(cf) + "/30")
        pygame.display.update()
        save()
        clock.tick(30)
