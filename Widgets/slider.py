from Widgets.base import *
from Widgets.label import Label


class Slider:
    def __init__(self, max_value, x, y, length, width, **kwargs):
        self.x = x
        self.y = y
        self.length = length
        self.width = width
        self.max_value = max_value
        self.min_value = kwargs.get("min_value", 0)
        self.vertical = kwargs.get("vertical", False)
        self.radius = kwargs.get("radius", 5)
        self.horizontal = kwargs.get("horizontal", False)
        self.line_color = kwargs.get("line_color", (150, 150, 150))
        self.circle_color = kwargs.get("circle_color", (255, 0, 0))
        self.text = kwargs.get("text", "")
        self.show_value = kwargs.get("show_value", False)
        self.font = kwargs.get("font", default_font)
        self.following = False
        self.nodes = []
        self.dist_between_nodes = self.length / (self.max_value - self.min_value)

        for i in range(self.max_value + 1):
            if self.horizontal:
                self.nodes.append(self.dist_between_nodes * i + self.x)
            else:
                self.nodes.append(self.dist_between_nodes * i + self.y)

        if self.vertical and self.horizontal:
            raise ValueError("Slider has to be either vertical or horizontal")
        if self.show_value and self.vertical:
            raise ValueError("Slider text only works in horizontal mode")
        if not self.vertical and not self.horizontal:
            self.horizontal = True

        if self.show_value and self.horizontal:
            self.label = Label("", x=self.x + self.length / 2, y=self.y - 35, center=True, font=self.font)

    def slide(self, screen, value):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]
        if self.vertical:
            pygame.draw.line(screen, self.line_color, (self.x, self.y), (self.x, self.y + self.length), self.width)
        elif self.horizontal:
            pygame.draw.line(screen, self.line_color, (self.x, self.y), (self.x + self.length, self.y), self.width)

        if self.horizontal:
            circle_x = (self.dist_between_nodes * (value - self.min_value) + self.x)

            if circle_x - self.radius < mouse_x < circle_x + self.radius and self.y - self.radius < mouse_y < self.y + self.radius:
                if mouse_down:
                    self.following = True
        else:
            circle_y = (self.dist_between_nodes * (value - self.min_value) + self.y)

            if circle_y - self.radius < mouse_y < circle_y + self.radius and self.x - self.radius < mouse_x < self.x + self.radius:
                if mouse_down:
                    self.following = True

        if self.following:
            if self.horizontal:
                if self.x < mouse_x < self.x + self.length:
                    min_difference = float('inf')

                    for num in self.nodes:
                        difference = abs(mouse_x - num)
                        if difference < min_difference:
                            min_difference = difference
                            closest_value = num

                    circle_x = closest_value
                    value = self.nodes.index(closest_value) + self.min_value
            else:
                if self.y < mouse_y < self.y + self.length:
                    min_difference = float('inf')

                    for num in self.nodes:
                        difference = abs(mouse_y - num)
                        if difference < min_difference:
                            min_difference = difference
                            closest_value = num

                    circle_y = closest_value
                    value = self.nodes.index(closest_value) + self.min_value
                else:
                    self.following = False

        if not mouse_down:
            self.following = False

        if self.horizontal:
            pygame.draw.circle(screen, self.circle_color, (int(circle_x), self.y), self.radius)
            if self.show_value:
                self.label.text = f"{self.text}: {value}"
                self.label.show(screen)
        else:
            pygame.draw.circle(screen, self.circle_color, (self.x, int(circle_y)), self.radius)

        return value
