import pygame
from pygame.constants import QUIT,K_F11,VIDEORESIZE,WINDOWFOCUSLOST,WINDOWFOCUSGAINED , K_a , K_d
from sys import exit
from UI import UI,Lines,Lines_Alpha,Images,Colour_Changing_Images,Collections
import os
import json
from Files import Save_Load

pygame.init()

EVENTS_LIST = [QUIT,VIDEORESIZE,WINDOWFOCUSLOST,WINDOWFOCUSGAINED]
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

pygame.event.set_blocked(None)
pygame.event.set_allowed(EVENTS_LIST)

FILES = Save_Load()

class Game_Shed():
    def __init__(self):
        self.line_colour = FILES.settings["line_colour"]
        self.icon_colour = FILES.settings["icon_colour"]
        self.background_colour = FILES.settings["background_colour"]

        self.ordered_collection_list = sorted(FILES.game_collections.keys(),key=str.lower)
        self.ordered_exe_list = sorted(FILES.executables.keys(),key=str.lower)
        self.collection_template = pygame.surface.Surface((170,50))
        self.collection_template.fill(self.line_colour)
        self.collection_template.set_alpha(120)

        self.collection_slice_start = 0
        self.collection_slice_end = 16 if len(self.ordered_collection_list) >= 16 else len(self.ordered_collection_list) #noramlly be slice start + ... but since i know its 0 do this
        self.collection_slice_objects = self.ordered_collection_list[0:self.collection_slice_end]
        #I want to dynamically add and remove the things in these lists to a group and that group gets displayed.
        #based on the dimensions of the window and the length of the lists above should determine how much 
        #through the list to move based on the position of the scroll bar

        #how large each thing will be so I know how to calc this:
        #170 , 50 with a gap of 10 inbetween, starts at 140, 20 gap at the bottom of window
        #1920 1080 window collections between 140 and 1060   15.3 can fit so 16 collections at a time (only part of one at bottom)


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

        # self.Collection_Group = pygame.sprite.Group().add(self.collection_slice_objects)
        self.Exe_Group = pygame.sprite.Group()
        
        self.Lines1 = pygame.sprite.Group()
        self.Images1 = pygame.sprite.Group()
        self.Const_Colour_Imgs = pygame.sprite.Group()
        self.Colour_Changing_Imgs = pygame.sprite.Group()

        # scroll bars probably going to be a low opacity line with a slightly higher opacity line on top 
        #the smaller higher opacity line will change size depending on how many games or things there are (if more then line smaller)
        self.Scroll_Bar_Lines1 = pygame.sprite.Group() # scroll bar for menu on left
        self.Scroll_Bar_Lines2 = pygame.sprite.Group() # scroll bar for the games

        Lines(self.line_colour,(1920,7),(0,120),self.Lines1)
        Lines(self.line_colour,(7,960),(200,120),self.Lines1)

        Colour_Changing_Images(os.path.join(BASE_PATH,"Images","cog.png"),self.icon_colour,(50,50),(20,33),self.Images1,self.Colour_Changing_Imgs)
        Colour_Changing_Images(os.path.join(BASE_PATH,"Images","icon.png"),self.icon_colour,(100,100),(500,500),self.Images1,self.Colour_Changing_Imgs) # this one is just for testing
        
        Images(os.path.join(BASE_PATH,"Images","icon.png"),(100,100),(700,700),self.Images1,self.Const_Colour_Imgs)

        Lines_Alpha(self.line_colour,100,(10,954),(192,127),self.Scroll_Bar_Lines1)
        Lines_Alpha(self.line_colour,120,(10,93),(192,127),self.Scroll_Bar_Lines1)

        Lines_Alpha(self.line_colour,100,(10,954),(1911,127),self.Scroll_Bar_Lines2)
        Lines_Alpha(self.line_colour,120,(10,93),(1911,127),self.Scroll_Bar_Lines2)

        # Lines_Alpha(self.line_colour,120,(170,50),(10,140),self.Lines1) #the dimensions and rgba for collection group
        # Lines_Alpha(self.line_colour,120,(170,50),(10,200),self.Lines1)

        #testing Collections class in UI
        Collections(self.collection_template,"hello",(300,300),self.Lines1)

    def quit_func(self,event):
        self.win_actual.destroy()
        pygame.quit()
        FILES.save(settings=True)
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
        self.Scroll_Bar_Lines2.update(window_changed_size=True)

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
        self.Scroll_Bar_Lines2.draw(self.win)
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
