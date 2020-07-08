import pygame
import libtcodpy as libtcod

pygame.init()

# game resolution
GAME_WIDTH = 1920
GAME_HEIGHT = 1080
CELL_WIDTH = 32
CELL_HEIGHT = 32

#gameplay
HARDCORE_MODE = False
#HC changes are:
	#	inventory actions cost a turn
	#	


#map vars
MAP_WIDTH = 55
MAP_HEIGHT = 30


#color definitions
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (100, 100, 100)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)

#game color palette
COLOR_DEFAULT_BG = COLOR_GRAY

#items


#FOV settings, multiple options to consider
FOV_ALGO = libtcod.FOV_SHADOW 
#FOV_ALGO = libtcod.FOV_BASIC
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 18

#fonts
FONT_DEBUG_MESSAGE = pygame.font.Font('fonts/RoseFlinch.ttf', 35)
FONT_MESSAGE_TEXT = pygame.font.Font('fonts/RoseFlinch.ttf', 35)
FONT_INVENTORY_TEXT = pygame.font.Font('fonts/RoseFlinch.ttf', 20)

#MISC
ArtificialLag = 75
#artificial limiter
GAME_FPS = 60

ENABLE_DEBUG = True

DISPLAY_FPS = False


#message console
NUM_MESSAGES = 4
TEXT_AA = True
TEXT_X_OVERRIDE = 10
TEXT_Y_OVERRIDE = 10
TEXT_HEIGHT = 20

