import pygame
from pygame.constants import QUIT,K_F11,VIDEORESIZE,WINDOWFOCUSLOST,WINDOWFOCUSGAINED , K_a , K_d
from sys import exit
from UI import UI,Lines,Lines_Alpha,Images,Colour_Changing_Images
import os
import json

pygame.init()

EVENTS_LIST = [QUIT,VIDEORESIZE,WINDOWFOCUSLOST,WINDOWFOCUSGAINED]
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

pygame.event.set_blocked(None)
pygame.event.set_allowed(EVENTS_LIST)


class Game_Shed():
    def __init__(self):
        self.pref_path = pygame.system.get_pref_path("nnw-2","Game Shed")
        self.settings_path = os.path.join(self.pref_path,"settings.json")
        self.settings = self.load_settings()

        self.line_colour = self.settings["line_colour"]
        self.icon_colour = self.settings["icon_colour"]
        self.background_colour = self.settings["background_colour"]

        self.w , self.h = pygame.display.get_desktop_sizes()[0]
        self.w = int(self.w * 0.5)
        self.h = int(self.h * 0.5)

        self.win_actual = pygame.Window("Game Shed",(self.w,self.h),resizable=True)
        self.win_actual.set_icon(pygame.image.load(os.path.join(BASE_PATH,"Images","icon.png")))
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

        # scroll bars probably going to be a low opacity line with a slightly higher opacity line on top 
        #the smaller higher opacity line will change size depending on how many games or things there are (if more then line smaller)
        self.Scroll_Bar_Lines1 = pygame.sprite.Group() # scroll bar for menu on left
        self.Scroll_Bar_Lines2 = pygame.sprite.Group() # scroll bar for the games
        
        #implement a group for the games and the file management stuff.
        #when scrolling through determine if something should/shouldn't be rendered based on height on screen
        #for all of the elements in the sprite group check their position and if they are in wanted range add them to a temp
        #sprite group and render that temp sprite group, for all the sprites in the main group when scrolling update their positions
        #but only render the ones in the temp sprite group

        Lines(self.line_colour,(1920,7),(0,120),self.Lines1)
        Lines(self.line_colour,(7,960),(180,120),self.Lines1)

        Colour_Changing_Images(os.path.join(BASE_PATH,"Images","cog.png"),self.icon_colour,(50,50),(20,20),self.Images1,self.Colour_Changing_Imgs)
        Colour_Changing_Images(os.path.join(BASE_PATH,"Images","icon.png"),self.icon_colour,(100,100),(500,500),self.Images1,self.Colour_Changing_Imgs) # this one is just for testing
        
        Images(os.path.join(BASE_PATH,"Images","icon.png"),(100,100),(700,700),self.Images1,self.Const_Colour_Imgs)

        Lines_Alpha(self.line_colour,100,(7,960),(166,120),self.Scroll_Bar_Lines1)

    def load_settings(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, "r") as settings_f:
                return json.load(settings_f)

        return {
            "line_colour" : (255,255,255),
            "icon_colour" : (255,255,255),
            "background_colour" : (0,0,0)
        }

    def save_settings(self):
        with open(self.settings_path, "w") as settings_f:
            json.dump(self.settings, settings_f, indent=4)

    def quit_func(self,event):
        self.win_actual.destroy()
        pygame.quit()
        self.save_settings()
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
        self.Scroll_Bar_Lines1.update(window_changed_size=True)

        self.render()

    def focus_lost_func(self,event):
        self.fps = 1
    
    def focus_gained_func(self,event):
        self.fps = 30

    def render(self):
        self.win.fill(self.background_colour) 
        #in future when I allow an image for a background keep the win.fill(self.background_colour) so the
        #background light can be customised if they want the opacity of the image to be lower
        self.Lines1.draw(self.win)
        self.Images1.draw(self.win)
        self.Scroll_Bar_Lines1.draw(self.win)
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
                self.Scroll_Bar_Lines1.update(colour_change=(0,0,255),alpha_change=255)

                self.render()
            if pygame.key.get_just_released()[K_d]:
                self.Colour_Changing_Imgs.update(colour_change=(0,255,0))
                self.Lines1.update(colour_change=(0,255,0))
                self.Scroll_Bar_Lines1.update(colour_change=(0,255,0),alpha_change=70)

                self.render()

            self.clock.tick(self.fps)
Game_Shed().main()
