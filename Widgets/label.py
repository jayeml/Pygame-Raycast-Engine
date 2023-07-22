from Widgets.base import *


class Label:
    def __init__(self, text,  **kwargs):
        self.text = text
        self.color = kwargs.get("color", (0, 0, 0))
        self.font = kwargs.get("font", default_font)
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.center = kwargs.get("center", False)

    def show(self, window):

        text = self.font.render(self.text, True, self.color)
        if self.center:
            text_rect = text.get_rect(center=(self.x, self.y))
            window.blit(text, text_rect)
        else:
            window.blit(text, (self.x, self.y))




