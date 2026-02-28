import pygame

class Lines():
    x_scale:int|float = ...
    y_scale:int|float = ...
    def __init__(self,colour:tuple[int,int,int], initial_size:tuple[int,int], destination:tuple[int,int]):
        self.initial_dest = destination
        self.dest:list = list(destination)
        self.colour = colour
        self.initial_size = initial_size
        self.line = ...
        self.change_line_size()
        self.change_line_dest()
        self.line.fill(colour)
        
    def change_line_size(self):
        self.line = pygame.surface.Surface((self.initial_size[0] * Lines.x_scale , self.initial_size[1] * Lines.y_scale))
        self.line.fill(self.colour)

    def change_line_dest(self):
        self.dest[0] = self.initial_dest[0] * Lines.x_scale
        self.dest[1] = self.initial_dest[1] * Lines.y_scale

    def change_line_colour(self,colour):
        self.colour = colour

    