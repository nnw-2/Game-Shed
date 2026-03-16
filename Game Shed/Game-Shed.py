import pygame
from pygame.constants import QUIT,K_F11,VIDEORESIZE,WINDOWFOCUSLOST,WINDOWFOCUSGAINED , K_a , K_d
from sys import exit
from UI import UI,Lines,Images,Colour_Changing_Images
import os
import json

pygame.init()

#pygame.system.get_pref_path("nnw-2","Game Shed") remember this for storage of settings etc

EVENTS_LIST = [QUIT,VIDEORESIZE,WINDOWFOCUSLOST,WINDOWFOCUSGAINED]
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

pygame.event.set_blocked(None)
pygame.event.set_allowed(EVENTS_LIST)


class Game_Shed():
    def __init__(self):
        self.w , self.h = pygame.display.get_desktop_sizes()[0]
        self.w = int(self.w * 0.5)
        self.h = int(self.h * 0.5)

        self.win_actual = pygame.Window("Game Shed",(self.w,self.h),resizable=True)
        self.win_actual.set_icon(pygame.image.load(BASE_PATH + "/Images/icon.png"))
        self.win = self.win_actual.get_surface()
        self.clock = pygame.Clock()
        self.fps = 30
        self.is_fullscreen = False
        self.x_scaler = self.w/1920
        self.y_scaler = self.h/1080
        UI.x_scale = self.x_scaler
        UI.y_scale = self.y_scaler
        self.Lines1 = pygame.sprite.Group()
        self.Images1 = pygame.sprite.Group()
        self.Const_Colour_Imgs = pygame.sprite.Group()
        self.Colour_Changing_Imgs = pygame.sprite.Group()

        Lines((255,255,255),(1920,10),(0,120),self.Lines1)
        Lines((255,255,255),(10,1080),(100,0),self.Lines1)
        Colour_Changing_Images(BASE_PATH + "/Images/icon.png",(0,0,255),(100,100),(500,500),self.Images1,self.Colour_Changing_Imgs) # this one is just for testing
        Images(BASE_PATH + "/Images/icon.png",(100,100),(700,700),self.Images1,self.Const_Colour_Imgs)


    def quit_func(self,event):
        self.win_actual.destroy()
        pygame.quit()
        exit()

    def win_size_change_func(self,event):
        self.w , self.h = event.w , event.h
        self.win = self.win_actual.get_surface()
        self.x_scaler = self.w/1920
        self.y_scaler = self.h/1080
        UI.x_scale = self.x_scaler
        UI.y_scale = self.y_scaler

        self.Lines1.update(window_changed_size=True)
        self.Images1.update(window_changed_size=True)

        self.render()

    def focus_lost_func(self,event):
        self.fps = 1
    
    def focus_gained_func(self,event):
        self.fps = 30

    def render(self):
        self.win.fill((0,0,0)) # want to change to fill based on a background var in future or have the win be an image
        self.Lines1.draw(self.win)
        self.Images1.draw(self.win)
        self.win_actual.flip()

    event_funcs = {
        QUIT : quit_func,
        VIDEORESIZE : win_size_change_func,
        WINDOWFOCUSLOST : focus_lost_func,
        WINDOWFOCUSGAINED : focus_gained_func
    }

    def main(self):
        self.render()
        while True:
            
            for event in pygame.event.get(): #don't put EVENTS_LIST back in the get, it messes with windowfocus stuff
                if self.event_funcs.get(event.type):
                    self.event_funcs[event.type](self,event)

            if pygame.key.get_just_released()[K_F11]:
                self.is_fullscreen = not self.is_fullscreen
                
                if self.is_fullscreen:
                    self.win_actual.set_fullscreen(True)
                else:
                    self.win_actual.set_windowed()
                    
                pygame.event.clear()

                self.w, self.h = self.win_actual.size
                self.win = self.win_actual.get_surface()
                
                self.x_scaler = self.w / 1920
                self.y_scaler = self.h / 1080
                UI.x_scale = self.x_scaler
                UI.y_scale = self.y_scaler
                
                self.Lines1.update(window_changed_size=True)
                self.Images1.update(window_changed_size=True)
                self.render()
            if pygame.key.get_just_released()[K_a]:
                self.Colour_Changing_Imgs.update(colour_change=(0,0,255))
                self.Lines1.update(colour_change=(255,0,0))
                self.render()
            if pygame.key.get_just_released()[K_d]:
                self.Colour_Changing_Imgs.update(colour_change=(0,255,0))
                self.Lines1.update(colour_change=(0,255,0))
                self.render()

            self.clock.tick(self.fps)
Game_Shed().main()
