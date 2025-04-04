import pygame as pg

class Button():
  def __init__(self, x, y, image, click_and_hold= False):
    self.image = image
    self.rect = self.image.get_rect()
    self.rect.topleft = (x, y)
    self.clicked = False
    self.click_and_hold = click_and_hold

  def draw(self, surface):
    action = False
    #get mouse position
    pos = pg.mouse.get_pos()


    if self.rect.collidepoint(pos):
      if pg.mouse.get_pressed()[0] == 1 and self.clicked == False:
        action = True
        if self.click_and_hold:
          self.clicked = True

    if pg.mouse.get_pressed()[0] == 0:
      self.clicked = False


    surface.blit(self.image, self.rect)

    return action