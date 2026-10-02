import pygame
pygame.init() #moved here for elipsis_surf in UI to not cause error
from pygame.constants import QUIT,K_F11,VIDEORESIZE,WINDOWFOCUSLOST,WINDOWFOCUSGAINED,MOUSEMOTION,MOUSEBUTTONDOWN,MOUSEBUTTONUP , K_a , K_d
from sys import exit
from UI import UI,Lines,Lines_Alpha,Images,Colour_Changing_Images,Collections
import os
import json
from Files import Save_Load

EVENTS_LIST = [QUIT,VIDEORESIZE,WINDOWFOCUSLOST,WINDOWFOCUSGAINED,MOUSEMOTION,MOUSEBUTTONDOWN,MOUSEBUTTONUP]
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

pygame.event.set_blocked(None)
pygame.event.set_allowed(EVENTS_LIST)

FILES = Save_Load()

class Game_Shed():
    def __init__(self):
        self.line_colour = FILES.settings["line_colour"]
        self.icon_colour = FILES.settings["icon_colour"]
        self.background_colour = FILES.settings["background_colour"]

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

        self.is_left_click_down = False

        self.Collection_Group = pygame.sprite.Group()
        self.Exe_Group = pygame.sprite.Group()

        self.ordered_collection_list = sorted(FILES.game_collections.keys(),key=str.lower)
        self.ordered_exe_list = sorted(FILES.executables.keys(),key=str.lower)
        self.collection_template = pygame.surface.Surface((170,50))
        self.collection_template.fill(self.line_colour)
        self.collection_template.set_alpha(120)

        self.collection_slice_start = 0
        self.collection_slice_end = 16 if len(self.ordered_collection_list) >= 16 else len(self.ordered_collection_list) #noramlly be slice start + ... but since i know its 0 do this
        self.collection_slice_objects:list[Collections] = []
        self.add_collection_slice_objects(self.ordered_collection_list[0:self.collection_slice_end])
        #I want to dynamically add and remove the things in these lists to a group and that group gets displayed.
        #based on the dimensions of the window and the length of the lists above should determine how much 
        #through the list to move based on the position of the scroll bar

        #how large each thing will be so I know how to calc this:
        #170 , 50 with a gap of 10 inbetween, starts at 140, 20 gap at the bottom of window
        #1920 1080 window collections between 140 and 1060   15.3 can fit so 16 collections at a time (only part of one at bottom)
        
        self.Lines1 = pygame.sprite.Group()
        self.Images1 = pygame.sprite.Group()
        self.Const_Colour_Imgs = pygame.sprite.Group()
        self.Colour_Changing_Imgs = pygame.sprite.Group()

        # scroll bars probably going to be a low opacity line with a slightly higher opacity line on top 
        #the smaller higher opacity line will change size depending on how many games or things there are (if more then line smaller)
        self.Scroll_Bar_Lines1 = pygame.sprite.Group() # scroll bar for menu on left
        self.Scroll_Bar_Lines2 = pygame.sprite.Group() # scroll bar for the games

        Lines(self.line_colour,(1920,7),(0,120),self.Lines1)
        Lines(self.line_colour,(7,960),(205,120),self.Lines1)

        Colour_Changing_Images(os.path.join(BASE_PATH,"Images","cog.png"),self.icon_colour,(50,50),(20,33),self.Images1,self.Colour_Changing_Imgs)
        Colour_Changing_Images(os.path.join(BASE_PATH,"Images","icon.png"),self.icon_colour,(100,100),(500,500),self.Images1,self.Colour_Changing_Imgs) # this one is just for testing
        
        Images(os.path.join(BASE_PATH,"Images","icon.png"),(100,100),(700,700),self.Images1,self.Const_Colour_Imgs)

        Lines_Alpha(self.line_colour,100,(15,954),(192,127),self.Scroll_Bar_Lines1)
        self.scroll_box = Lines_Alpha(self.line_colour,120,(15,93),(192,127),self.Scroll_Bar_Lines1)
        self.already_in_scroll_box1 = False


        Lines_Alpha(self.line_colour,100,(15,954),(1905,127),self.Scroll_Bar_Lines2)
        Lines_Alpha(self.line_colour,120,(15,93),(1905,127),self.Scroll_Bar_Lines2)

    def add_collection_slice_objects(self,collection_names:list[str]|str):
        if type(collection_names) == list:
            for i in range(len(collection_names)):
                shift = 60 * i
                self.collection_slice_objects.append(Collections(self.collection_template,collection_names[i],(10,140+shift),self.Collection_Group))
        else:
            self.collection_slice_objects.append(Collections(self.collection_template,collection_names,(10,self.collection_slice_objects[-1].rect.topleft[1] +60),self.Collection_Group))

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
        self.Collection_Group.update(window_changed_size=True)

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
        self.Collection_Group.draw(self.win)
        self.win_actual.flip()

    def mouse_button_up_func(self,event):
        # print(event)
        if event.button == 1:
            self.is_left_click_down = False

    def mouse_button_down_func(self,event):
        # print(event)
        if event.button == 1:
            self.is_left_click_down = True

    def moving_scroll_bar(self,y_change):
        self.scroll_box.change_initial_dest_y(y_change)
        self.scroll_box.change_dest()
        self.render()

    #as scrolling counts as mouse button up/down events do that part of the collision in the above funcs
    def mouse_collision(self,event):
        # print(event)
        if self.scroll_box.rect.collidepoint(event.pos):
            if not self.already_in_scroll_box1:
                pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND))
                self.scroll_box.change_alpha(180) #120 default alpha
                self.render()
                self.already_in_scroll_box1 = True
            if self.is_left_click_down:
                self.moving_scroll_bar(event.pos[1] / self.y_scaler)
        elif self.already_in_scroll_box1:
            if not self.is_left_click_down:
                pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW))
                self.scroll_box.change_alpha(120)
                self.render()
                self.already_in_scroll_box1 = False
            else:
                self.moving_scroll_bar(event.pos[1] / self.y_scaler)

        # event.buttons[0] will be 1 if left click is held down while mouse is moving
        # I want to keep track of if left clicked the scroll box and have held mouse since.
        # I can't confirm that from just mousemotion event I also need mouse button events
        # as it will stay as 1 if I let go while not moving mouse then re click and drag again which it shouldn't 

    event_funcs = {
        QUIT : quit_func,
        VIDEORESIZE : win_size_change_func,
        WINDOWFOCUSLOST : focus_lost_func,
        WINDOWFOCUSGAINED : focus_gained_func,
        MOUSEMOTION : mouse_collision,
        MOUSEBUTTONUP : mouse_button_up_func,
        MOUSEBUTTONDOWN : mouse_button_down_func
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
                self.Scroll_Bar_Lines1.update(window_changed_size=True)
                self.Scroll_Bar_Lines2.update(window_changed_size=True)
                self.Collection_Group.update(window_changed_size=True)
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
