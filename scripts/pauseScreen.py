import pygame as pg

from .Button import Button
from . import constants as con


class PauseScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pg.font.Font(None, 74)
        self.resume_button = Button(
            con.SCREEN_WIDTH // 2 - 100, con.SCREEN_HEIGHT // 2, None,
            text="Resume", text_color=(255, 255, 255), font_size=40,
            width=200, height=60, color=(50, 150, 50)
        )

    def draw(self):

        overlay = pg.Surface((con.SCREEN_WIDTH, con.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        text = self.font.render("Paused", True, (255, 255, 255))
        text_rect = text.get_rect(center=(con.SCREEN_WIDTH // 2, con.SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(text, text_rect)
        self.resume_button.draw(self.screen)
        pg.display.flip()


    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "quit"
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.resume_button.is_clicked(pg.mouse.get_pos()):
                    return "resume"
        return "pause"
