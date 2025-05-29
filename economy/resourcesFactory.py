import pygame as pg
import os
import constants as con

class Factory:
    def __init__(self, position, resource_type, production_rate_per_wave, image_path=None):
        self.position = position
        self.resource_type = resource_type
        self.production_rate = production_rate_per_wave
        self.image = None
        if image_path:
            try:
                self.image = pg.image.load(image_path).convert_alpha()
            except pg.error as e:
                print(f"Error loading factory image {image_path}: {e}")
                self.image = pg.Surface((40, 40))
                self.image.fill((100, 100, 100))
        else:
            self.image = pg.Surface((40, 40))
            self.image.fill((100,100,100))

    def update(self, delta_time, manager):
        pass  # Reserved for future per-frame updates

    def get_wave_payout(self):
        """Return resource type and amount produced per wave."""
        return self.resource_type, self.production_rate

    def draw(self, surface):
        x, y = self.position

        if self.image:
            surface.blit(self.image, (x, y))
            w, h = self.image.get_size()
        else:
            pg.draw.rect(surface, (100, 100, 100), (x, y, 40, 40)) 
        pg.draw.rect(surface, (255, 255, 255), (x, y, w, h), width=2, border_radius=4)


