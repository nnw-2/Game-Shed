import pygame
from pygame.constants import QUIT,K_F11
from sys import exit

pygame.init()

#pygame.system.get_pref_path("nnw-2","Game Shed") remember this for storage of settings etc
w ,h = pygame.display.get_desktop_sizes()[0]
win = pygame.display.set_mode((w*0.5,h*0.5),flags=pygame.SCALED|pygame.RESIZABLE) # when setting window width and height
# use sizes lower than the users resolution or resizing bugs out (can't size window smaller than sizes input in set mode)

while True:
    if pygame.event.peek(QUIT):
        pygame.quit()
        exit()
    if pygame.key.get_just_released()[K_F11]:
        pygame.display.toggle_fullscreen()
        pygame.event.clear()
    pygame.display.flip()
