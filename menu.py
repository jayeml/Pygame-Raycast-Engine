from main import *
from Widgets.label import Label


def menu():
    pygame.display.set_caption("Raycast Engine (Move Mouse)")
    title = Label("Raycast Engine", x=screen_width//2, y=150, font=title_font, center=True)
    while True:
        screen.fill((3, 37, 126))
        render_walls(192, 192)
        player.ray_angle += .2
        player.rotation -= .2
        title.show(screen)
        player.x = player.y = 192
        player.z = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save()
                quit()

            elif event.type == pygame.MOUSEMOTION:
                pygame.display.set_caption("Raycast Engine")

        if play.button(screen):
            player.rotation = 0
            player.ray_angle = 270
            main()
        if edit.button(screen):
            from level_editor import map_maker
            map_maker()

        pygame.display.update()