import pygame as pg
# Use package-relative imports, with a fallback for direct execution
try:
    from . import constants as con
    from .Button import Button
except ImportError:
    import constants as con
    from Button import Button

class EndingScreen:
    def __init__(self, screen, game_won=False, next_level_available=False):
        self.screen = screen
        self.game_won = game_won
        self.next_level_available = next_level_available
        self.font = pg.font.Font(None, 74)

        button_width = 220
        button_height = 50
        button_spacing = 20
        
        # Determine number of buttons to display
        num_buttons = 3 if self.game_won and self.next_level_available else 2
        
        total_buttons_height = (num_buttons * button_height) + ((num_buttons - 1) * button_spacing if num_buttons > 1 else 0)
        # Vertically center buttons, then shift down for title space
        button_y_start = (con.SCREEN_HEIGHT // 2) - (total_buttons_height // 2) + 70

        current_y = button_y_start

        self.next_level_button = None
        if self.game_won and self.next_level_available:
            self.next_level_button = Button(
                con.SCREEN_WIDTH // 2 - button_width // 2,
                current_y,
                None,
                text="Next Level",
                text_color=(255, 255, 255),
                font_size=30,
                width=button_width,
                height=button_height,
                color=(0, 150, 50)
            )
            current_y += button_height + button_spacing

        play_again_text = "Replay Level" if self.game_won else "Try Again"
        self.play_again_button = Button(
            con.SCREEN_WIDTH // 2 - button_width // 2,
            current_y,
            None,
            text=play_again_text,
            text_color=(255, 255, 255),
            font_size=30,
            width=button_width,
            height=button_height,
            color=(0, 100, 150)
        )
        current_y += button_height + button_spacing
        
        self.main_menu_button = Button(
            con.SCREEN_WIDTH // 2 - button_width // 2,
            current_y,
            None,
            text="Level Select",
            text_color=(255, 255, 255),
            font_size=30,
            width=button_width,
            height=button_height,
            color=(150, 100, 0)
        )

    def draw(self):
        self.screen.fill((30, 30, 30))

        # Display appropriate title based on win/loss
        if self.game_won:
            title_text = self.font.render("Victory!", True, (0, 255, 0))
        else:
            title_text = self.font.render("Game Over", True, (255, 0, 0))

        title_rect = title_text.get_rect(center=(con.SCREEN_WIDTH // 2, con.SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(title_text, title_rect)

        if self.next_level_button:
            self.next_level_button.draw(self.screen)
        self.play_again_button.draw(self.screen)
        self.main_menu_button.draw(self.screen)

        pg.display.flip()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "quit", None
            # Handle left mouse click on buttons
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                if self.next_level_button and self.next_level_button.is_clicked(mouse_pos):
                    return "next_level", None
                if self.play_again_button.is_clicked(mouse_pos):
                    return "replay_current_level", None
                if self.main_menu_button.is_clicked(mouse_pos):
                    return "main_menu", None
        return "running", None

# Test usage for different ending scenarios
if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode((con.SCREEN_WIDTH, con.SCREEN_HEIGHT))
    pg.display.set_caption("Ending Screen Test")
    clock = pg.time.Clock()

    # Test case 1: Player won, next level available
    print("Test 1: Won, next level available")
    ending_screen_win_next = EndingScreen(screen, game_won=True, next_level_available=True)
    current_screen_state = "running"
    while current_screen_state == "running":
        current_screen_state, _ = ending_screen_win_next.handle_events()
        ending_screen_win_next.draw()
        clock.tick(30)
    print(f"Ending screen action: {current_screen_state}")

    # Test case 2: Player won, no next level
    print("\nTest 2: Won, no next level")
    ending_screen_win_no_next = EndingScreen(screen, game_won=True, next_level_available=False)
    current_screen_state = "running"
    while current_screen_state == "running":
        current_screen_state, _ = ending_screen_win_no_next.handle_events()
        ending_screen_win_no_next.draw()
        clock.tick(30)
    print(f"Ending screen action: {current_screen_state}")

    # Test case 3: Player lost
    print("\nTest 3: Lost")
    ending_screen_lose = EndingScreen(screen, game_won=False, next_level_available=False)
    current_screen_state = "running"
    while current_screen_state == "running":
        current_screen_state, _ = ending_screen_lose.handle_events()
        ending_screen_lose.draw()
        clock.tick(30)
    print(f"Ending screen action: {current_screen_state}")

    pg.quit()
