import pygame
from pygame.constants import QUIT,K_F11,WINDOWSIZECHANGED
from sys import exit
from Lines import Lines

pygame.init()

#pygame.system.get_pref_path("nnw-2","Game Shed") remember this for storage of settings etc

EVENTS_LIST = [QUIT,WINDOWSIZECHANGED]

pygame.event.set_blocked(None)
pygame.event.set_allowed(EVENTS_LIST)

# line = pygame.surface.Surface((10*self.x_scaler,1000*self.y_scaler))
# line.fill((255,255,255))
# self.win.blit(line,(300*self.x_scaler,0*self.y_scaler))
# pygame.display.flip()

class Game_Shed():
    def __init__(self):
        self.w , self.h = pygame.display.get_desktop_sizes()[0]
        self.w *= 0.5
        self.h *= 0.5
        self.win = pygame.display.set_mode((self.w,self.h),flags=pygame.RESIZABLE)
        self.x_scaler = self.w/1920
        self.y_scaler = self.h/1080
        Lines.x_scale = self.x_scaler
        Lines.y_scale = self.y_scaler
        self.Lines1 = [Lines((255,255,255),(10,100),(20,100)),
                       Lines((255,255,255),(10,100),(20,300))]

    def quit_func(self,event):
        pygame.quit()
        exit()

    def change_size_and_dest_of_lines(self,line_list):
        for line in line_list:
            line.change_line_size()
            line.change_line_dest()

    def win_size_change_func(self,event):
        self.w , self.h = event.dict["x"] , event.dict["y"]
        self.x_scaler = self.w/1920
        self.y_scaler = self.h/1080
        Lines.x_scale = self.x_scaler
        Lines.y_scale = self.y_scaler
        self.change_size_and_dest_of_lines(self.Lines1)
        self.line_blit(self.Lines1)
        pygame.display.flip()


    event_funcs = {
        QUIT : quit_func,
        WINDOWSIZECHANGED : win_size_change_func
    }

    def line_blit(self,lines):
        self.win.fill((0,0,0)) # i would want this to not be here but before where i will have everything get blitted. 
        for line in lines:
            self.win.blit(line.line,line.dest)

    def main(self):
        self.line_blit(self.Lines1)
        pygame.display.flip()
        while True:
            
            for event in pygame.event.get(EVENTS_LIST):
                self.event_funcs[event.type](self,event)

            if pygame.key.get_just_released()[K_F11]:
                pygame.display.toggle_fullscreen()
                pygame.event.clear()
                pygame.display.flip()
Game_Shed().main()

