import pygame
from pygame.constants import QUIT,K_F11,VIDEORESIZE
from sys import exit
from UI import UI,Lines

pygame.init()

#pygame.system.get_pref_path("nnw-2","Game Shed") remember this for storage of settings etc

EVENTS_LIST = [QUIT,VIDEORESIZE]

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
        UI.x_scale = self.x_scaler
        UI.y_scale = self.y_scaler
        self.Lines1 = pygame.sprite.Group()

        Lines((255,255,255),(960,540),(0,0),self.Lines1)

    def quit_func(self,event):
        pygame.quit()
        exit()

    def win_size_change_func(self,event):
        self.w , self.h = event.w , event.h
        self.x_scaler = self.w/1920
        self.y_scaler = self.h/1080
        UI.x_scale = self.x_scaler
        UI.y_scale = self.y_scaler

        self.Lines1.update(window_changed_size=True)

        self.render()
        
    def render(self):
        self.win.fill((0,0,0)) # want to change to fill based on a background var in future or have the win be an image

        self.Lines1.draw(self.win)

        pygame.display.flip()

    event_funcs = {
        QUIT : quit_func,
        VIDEORESIZE : win_size_change_func
    }

    def main(self):
        self.render()
        while True:
            
            for event in pygame.event.get(EVENTS_LIST):
                self.event_funcs[event.type](self,event)

            if pygame.key.get_just_released()[K_F11]:
                pygame.display.toggle_fullscreen()
                pygame.event.clear()

                self.w, self.h = self.win.get_size()
                
                self.x_scaler = self.w / 1920
                self.y_scaler = self.h / 1080
                UI.x_scale = self.x_scaler
                UI.y_scale = self.y_scaler
                
                self.Lines1.update(window_changed_size=True)
                self.render()

Game_Shed().main()



# I want to move to using pygame.Window instead of display setmode