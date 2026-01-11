import pygame
from pygame.constants import QUIT,K_F11,WINDOWSIZECHANGED
from sys import exit
from Lines import Lines

pygame.init()

#pygame.system.get_pref_path("nnw-2","Game Shed") remember this for storage of settings etc

pygame.event.set_blocked(None)
pygame.event.set_allowed([QUIT,WINDOWSIZECHANGED])

# line = pygame.surface.Surface((10*x_scaler,1080*y_scale))
# line.fill((255,255,255))
# win.blit(line,(300*x_scaler,0))
# pygame.display.flip()

class Game_Shed():
    def __init__(self):
        self.w , self.h = pygame.display.get_desktop_sizes()[0]
        self.win = pygame.display.set_mode((self.w*0.5,self.h*0.5),flags=pygame.SCALED|pygame.RESIZABLE)
        self.x_scaler = self.w/1920
        self.y_scaler = self.h/1080
        self.line_dests = ((),())

    def size_change_func(self,event):
        self.w , self.h = event.dict["x"] , event.dict["y"]
        self.x_scaler = self.w/1920
        self.y_scaler = self.h/1080

    event_funcs = {
        WINDOWSIZECHANGED : size_change_func
    }

    def line_blit(self,lines):
        self.win.fill((0,0,0)) # i would want this to not be here but before where i will have everything get blitted. 
        for line,dest in zip(lines,self.line_dests):
            self.win.blit(line,dest)  # the lines can be from a class in diff module or class in this idk

    def main(self):
        while True:
            if pygame.event.peek(QUIT):
                pygame.quit()
                exit()
            for event in pygame.event.get(WINDOWSIZECHANGED):
                self.event_funcs[event.type](self,event)

            if pygame.key.get_just_released()[K_F11]:
                pygame.display.toggle_fullscreen()
                pygame.event.clear()
                pygame.display.flip()
Game_Shed().main()