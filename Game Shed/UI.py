from typing import Any

import pygame

class UI(pygame.sprite.Sprite):
    x_scale:int|float = ...
    y_scale:int|float = ...
    def __init__(self,initial_size:tuple[int,int], destination:tuple[int,int], *sprite_groups) -> None:
        super().__init__(*sprite_groups)
        self.initial_dest = destination
        self.initial_size = initial_size
        self.image:pygame.Surface = pygame.Surface((1,1))
        self.rect:pygame.Rect = pygame.Rect(destination,initial_size)
    
    def change_dest(self):
        self.rect.topleft = (int(self.initial_dest[0] * UI.x_scale),
                             int(self.initial_dest[1] * UI.y_scale))
    
    def change_size(self):
        ...

    def change_colour(self,colour):
        ...

    def update(self, **kwargs):
        if kwargs.get("window_changed_size", False):
            self.change_dest()
            self.change_size()
        if kwargs.get("colour_change", False):
            self.change_colour(kwargs.get("colour_change"))

class Lines(UI):
    def __init__(self,colour:tuple[int,int,int], initial_size:tuple[int,int], destination:tuple[int,int], *sprite_groups):
        super().__init__(initial_size,destination,*sprite_groups)
        self.colour = colour
        self.change_size()
        self.change_dest()
        
    def change_size(self):
        self.image = pygame.Surface((int(self.initial_size[0] * UI.x_scale),
                                     int(self.initial_size[1] * UI.y_scale)))
        self.image.fill(self.colour)
        self.rect.size = self.image.get_size()

    def change_colour(self,colour):
        self.colour = colour
        self.image.fill(self.colour)

class Images(UI):
    def __init__(self,image:str, initial_size:tuple[int,int], destination:tuple[int,int], *sprite_groups):
        super().__init__(initial_size,destination,*sprite_groups)
        self.initial_image = pygame.image.load(image).convert_alpha()

        self.change_size()
        self.change_dest()

    def change_size(self):
        self.image = pygame.transform.smoothscale(self.initial_image, (int(self.initial_size[0] * UI.x_scale),
                                                                       int(self.initial_size[1] * UI.y_scale))).convert_alpha()
        self.rect.size = self.image.get_size()

class Colour_Changing_Imgaes(Images):
    def __init__(self, image: str, colour:tuple[int,int,int], initial_size: tuple[int, int], destination: tuple[int, int], *sprite_groups):
        self.colour = colour
        super().__init__(image, initial_size, destination, *sprite_groups)
        self.image:pygame.Surface = pygame.Surface((1,1),pygame.SRCALPHA)

        self.change_size()
        self.change_dest()

    def change_size(self):
        super().change_size()
        self.change_colour(self.colour)

    def change_colour(self,colour):
        self.colour = colour
        scaled_white_image = pygame.transform.smoothscale(self.initial_image, self.image.get_size())
        self.image.fill((colour[0], colour[1], colour[2], 255))
        self.image.blit(scaled_white_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)