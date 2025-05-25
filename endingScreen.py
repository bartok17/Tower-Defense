import pygame as pg
import constants as con
from Button import Button

class EndingScreen:
    def __init__(self, screen, game_won=False):
        self.screen = screen
        self.game_won = game_won
        self.font = pg.font.Font(None, 74)
        self.small_font = pg.font.Font(None, 50)

        button_width = 200
        button_height = 50
        button_y_start = con.SCREEN_HEIGHT // 2 + 50

        # Use text rendering for buttons if no image is provided
        self.play_again_button = Button(
            con.SCREEN_WIDTH // 2 - button_width // 2,
            button_y_start,
            None,
            text="Play Again",
            text_color=(255, 255, 255),
            font_size=30,
            width=button_width,
            height=button_height,
            color=(0,100,0)
        )
        self.main_menu_button = Button(
            con.SCREEN_WIDTH // 2 - button_width // 2,
            button_y_start + button_height + 20,
            None,
            text="Main Menu",
            text_color=(255, 255, 255),
            font_size=30,
            width=button_width,
            height=button_height,
            color=(100,0,0)
        )

    def draw(self):
        self.screen.fill((30, 30, 30))

        if self.game_won:
            title_text = self.font.render("You Won!", True, (0, 255, 0))
        else:
            title_text = self.font.render("Game Over", True, (255, 0, 0))

        title_rect = title_text.get_rect(center=(con.SCREEN_WIDTH // 2, con.SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(title_text, title_rect)

        self.play_again_button.draw(self.screen)
        self.main_menu_button.draw(self.screen)

        pg.display.flip()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "quit", None
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.play_again_button.is_clicked(pg.mouse.get_pos()):
                    print("Play Again button clicked (no functionality yet)")
                    return "play_again", None
                if self.main_menu_button.is_clicked(pg.mouse.get_pos()):
                    print("Main Menu button clicked (no functionality yet)")
                    return "main_menu", None
        return "running", None

# Test usage
if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode((con.SCREEN_WIDTH, con.SCREEN_HEIGHT))
    pg.display.set_caption("Ending Screen Test")
    clock = pg.time.Clock()

    ending_screen_win = EndingScreen(screen, game_won=True)
    current_screen_state = "running"
    while current_screen_state == "running":
        current_screen_state, _ = ending_screen_win.handle_events()
        ending_screen_win.draw()
        clock.tick(30)
    print(f"Ending screen action: {current_screen_state}")

    pg.quit()
