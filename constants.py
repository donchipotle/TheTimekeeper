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

#spawns
items_per_room = 3
enemies_per_room = 3

#map limitations
MAP_WIDTH = 60
MAP_HEIGHT = 60
MAP_MAX_NUM_ROOMS = 20
MAP_NUM_LEVELS = 2 #max depth of dungeon

#color definitions
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_D_GRAY = (20, 20, 20)
COLOR_GRAY = (100, 100, 100)
COLOR_L_GRAY = (192, 192, 192)
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_L_BLUE = (149, 202, 255)
COLOR_ORANGE = (255, 128, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BROWN = (139,69,19)
COLOR_L_BROWN = (205,133,63)
COLOR_YINZER = (212, 175, 55)

#Window background
COLOR_DEFAULT_BG = COLOR_D_GRAY

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
FONT_STATS = pygame.font.Font('fonts/Lekton-Regular.ttf', 40)
FONT_CURSOR_TEXT = pygame.font.Font('fonts/Lekton-Regular.ttf', CELL_HEIGHT)
FONT_MESSAGE_TEXT = pygame.font.Font('fonts/Lekton-Regular.ttf', 35)
FONT_INVENTORY_TEXT = pygame.font.Font('fonts/Lekton-Regular.ttf', 20)

#MISC
#ArtificialLag = 75					#deprecated, should not be needed but will be left in for now
PermitKeyHolding = True
KeyDownDelay = 200
KeyRepeatDelay = 70
#artificial limiter
GAME_FPS = 60

#used for num prompts
NUMPAD_KEYS = {pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4, pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9}

#message console
NUM_MESSAGES = 4
TEXT_AA = True
TEXT_X_OVERRIDE = 10
TEXT_Y_OVERRIDE = 10
TEXT_HEIGHT = 10

#text prompts
PROMPT_BORDER_THICKNESS = 4
PROMPT_OFFSET_X = 1
PROMPT_OFFSET_Y = 1
PROMPT_DEFAULT_WIDTH = 150



#generating maps


#town - kazany
KAZANY_BUILDING_MAX_HEIGHT = 7 
KAZANY_BUILDING_MIN_HEIGHT = 5
KAZANY_BUILDING_MAX_WIDTH = 8
KAZANY_BUILDING_MIN_WIDTH = 4

HOUSE_INTERIOR_MAX_HEIGHT = 40
HOUSE_INTERIOR_MIN_HEIGHT = 30
HOUSE_INTERIOR_MAX_WIDTH = 50
HOUSE_INTERIOR_MIN_WIDTH = 30

#room limitations
ROOM_MAX_HEIGHT = 10
ROOM_MIN_HEIGHT = 4
ROOM_MAX_WIDTH = 12
ROOM_MIN_WIDTH = 4