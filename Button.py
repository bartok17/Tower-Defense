import pygame as pg

class Button():
  def __init__(self, x, y, image, label=None, text="", text_color=(0,0,0), font_size=24,
               font_name=None, width=None, height=None, color=(200,200,200),
               click_and_hold=False):

    self.x = x
    self.y = y
    self.click_and_hold = click_and_hold
    self.clicked = False 
    self.hover_progress = 0.0
    self.hover_speed = 0.1
    self.label = label
    # Determine the final image for the button
    if image:
        self.image = image
        if width is not None and height is not None:
            self.image = pg.transform.scale(self.image, (width, height))
    else:
        current_width = width
        current_height = height

        if current_width is None or current_height is None:
            # If dimensions are not provided, try to auto-size from text
            if text:
                if not pg.font.get_init(): 
                    pg.font.init() # Ensure Pygame font module is initialized
                temp_font = pg.font.Font(font_name, font_size)
                text_render_temp = temp_font.render(text, True, text_color)
                if current_width is None: 
                    current_width = text_render_temp.get_width() + 20 
                if current_height is None: 
                    current_height = text_render_temp.get_height() + 10 
            else:
                raise ValueError("Button without image needs width and height, or text for auto-sizing.")

        self.image = pg.Surface((current_width, current_height))
        self.image.fill(color) 

        if text:
            if not pg.font.get_init(): 
                pg.font.init() 
            current_font = pg.font.Font(font_name, font_size) 
            text_surface = current_font.render(text, True, text_color)
            text_rect = text_surface.get_rect(center=(current_width // 2, current_height // 2))
            self.image.blit(text_surface, text_rect)

    self.rect = self.image.get_rect()
    self.rect.topleft = (x, y)

  def draw(self, surface):
    action = False
    pos = pg.mouse.get_pos()

    if self.rect.collidepoint(pos):
      if pg.mouse.get_pressed()[0] == 1: # Left mouse button is pressed
        if not self.clicked: # If not already in 'clicked' state for this press sequence
          action = True
          if self.click_and_hold:
            self.clicked = True
      # else: # Mouse button not pressed (or not button 0)
    # else: # Mouse is not colliding with the button
        pass

    if pg.mouse.get_pressed()[0] == 0:
      self.clicked = False

    surface.blit(self.image, self.rect)

    return action

  def is_clicked(self, pos):
    """
    Checks if the given position (e.g., mouse position) is within the button's bounds.
    This method is used by EndingScreen in its event handling loop,
    typically after a MOUSEBUTTONDOWN event has been detected.
    """
    return self.rect.collidepoint(pos)
  def update_hover(self, is_hovered):
    if is_hovered:
        self.hover_progress = min(1.0, self.hover_progress + self.hover_speed)
    else:
        self.hover_progress = max(0.0, self.hover_progress - self.hover_speed)
