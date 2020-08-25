import pygame
import libtcodpy as libtcod

pygame.init()

#########################################################################################
#										WARNING!!!!										#
#																						#
#	These parameters are probably best left alone. 										#
#	Toying with them causes bad things to happen. 										#
#	Do not cause bad things to happen. 													#
#	Bad things are bad. kthxbye															#
#										-sincerely, yo boi Big Chug						#
#																						#
#########################################################################################



# screen resolution
GAME_WIDTH = 1920
GAME_HEIGHT = 1080

CAM_WIDTH = 1920
CAM_HEIGHT = 1080

CELL_WIDTH = 32
CELL_HEIGHT = 32

CELL_HALF_WIDTH = CELL_WIDTH / 2
CELL_HALF_HEIGHT = CELL_HEIGHT / 2



#gameplay
HARDCORE_MODE = False
#HC changes are:
	#	inventory actions cost a turn



#spawns
items_per_room = 3
enemies_per_room = 3

#map limitations
MAP_WIDTH = 80
MAP_HEIGHT = 80
MAP_MAX_NUM_ROOMS = 20

#room limitations
ROOM_MAX_HEIGHT = 10
ROOM_MIN_HEIGHT = 4
ROOM_MAX_WIDTH = 15
ROOM_MIN_WIDTH = 4

#color definitions
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (100, 100, 100)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_L_BLUE = (149, 202, 255)
COLOR_ORANGE = (255, 128, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BROWN = (139,69,19)
COLOR_L_BROWN = (205,133,63)

#game color palette
COLOR_DEFAULT_BG = COLOR_GRAY

#items

#FOV settings, multiple options to consider
FOV_ALGO = libtcod.FOV_SHADOW 
#FOV_ALGO = libtcod.FOV_BASIC
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 18

#fonts
#font for rendering the entire screen
#FONT_RENDER_TEXT = pygame.font.Font('fonts/Montserrat-Regular.ttf', 35)
FONT_RENDER_TEXT = pygame.font.Font('fonts/Azoft Sans.otf', 35)


FONT_TITLE_SCREEN1 = pygame.font.Font('fonts/Lekton-Regular.ttf', 70)
FONT_TITLE_SCREEN2 = pygame.font.Font('fonts/Lekton-Regular.ttf', 40)
FONT_DEBUG_MESSAGE = pygame.font.Font('fonts/RoseFlinch.ttf', 35)
FONT_CURSOR_TEXT = pygame.font.Font('fonts/RoseFlinch.ttf', CELL_HEIGHT)
FONT_MESSAGE_TEXT = pygame.font.Font('fonts/Lekton-Regular.ttf', 35)
FONT_INVENTORY_TEXT = pygame.font.Font('fonts/Lekton-Regular.ttf', 20)

#MISC
#ArtificialLag = 75					#deprecated, should not be needed but will be left in for now
PermitKeyHolding = True
KeyDownDelay = 200
KeyRepeatDelay = 70
#artificial limiter
GAME_FPS = 60

#message console
NUM_MESSAGES = 4
TEXT_AA = True
TEXT_X_OVERRIDE = 10
TEXT_Y_OVERRIDE = 10
TEXT_HEIGHT = 10

