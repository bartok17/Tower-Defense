import pygame as pg
import constants as con
from Button import Button # Assuming Button class is in Button.py

class EndingScreen:
    def __init__(self, screen, game_won=False):
        self.screen = screen
        self.game_won = game_won
        self.font = pg.font.Font(None, 74)
        self.small_font = pg.font.Font(None, 50)

        button_width = 200
        button_height = 50
        button_y_start = con.SCREEN_HEIGHT // 2 + 50

        # Placeholder button image (or use text rendering for buttons)
        # For simplicity, we'll use text rendering if no image is provided
        # If you have a button image, load it here:
        # button_img = pg.image.load("path_to_your_button_image.png").convert_alpha()
        # button_img = pg.transform.scale(button_img, (button_width, button_height))

        self.play_again_button = Button(
            con.SCREEN_WIDTH // 2 - button_width // 2,
            button_y_start,
            None, # button_img
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
            None, # button_img
            text="Main Menu",
            text_color=(255, 255, 255),
            font_size=30,
            width=button_width,
            height=button_height,
            color=(100,0,0)
        )

    def draw(self):
        self.screen.fill((30, 30, 30))  # Dark background

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
                return "quit", None # Signal to quit the entire application
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.play_again_button.is_clicked(pg.mouse.get_pos()):
                    print("Play Again button clicked (no functionality yet)")
                    return "play_again", None # Placeholder action
                if self.main_menu_button.is_clicked(pg.mouse.get_pos()):
                    print("Main Menu button clicked (no functionality yet)")
                    return "main_menu", None # Placeholder action
        return "running", None # Continue showing the ending screen

# Example usage (for testing purposes, not part of the class file)
if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode((con.SCREEN_WIDTH, con.SCREEN_HEIGHT))
    pg.display.set_caption("Ending Screen Test")
    clock = pg.time.Clock()

    # Assuming Button class is defined and works with text
    # If Button requires an image, you'll need to provide one.
    # For this example, Button class should be adaptable or a simple rect-based button.

    # Test Game Over
    # ending_screen_lose = EndingScreen(screen, game_won=False)
    # current_screen_state = "running"
    # while current_screen_state == "running":
    #     current_screen_state, _ = ending_screen_lose.handle_events()
    #     ending_screen_lose.draw()
    #     clock.tick(30)
    # print(f"Ending screen action: {current_screen_state}")

    # Test Game Won
    ending_screen_win = EndingScreen(screen, game_won=True)
    current_screen_state = "running"
    while current_screen_state == "running":
        current_screen_state, _ = ending_screen_win.handle_events()
        ending_screen_win.draw()
        clock.tick(30)
    print(f"Ending screen action: {current_screen_state}")

    pg.quit()