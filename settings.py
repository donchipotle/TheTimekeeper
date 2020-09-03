import pygame

#GRAPHICS

#draw background image
DRAW_MENU_BACKGROUND = True

#toggle rendering ballistics (spells, projectiles, etc.), currently broken by camera refactor
RENDER_BALLISTICS = True

BALLISTIC_TICK_UPPER = 50	#ms elapsed before ballistic is cleared
BALLISTIC_TICK_LOWER = 50	#ms elapsed before next tick
EXPLOSION_TICK_UPPER = 50	#ms elapsed between explosion is cleared
EXPLOSION_TICK_LOWER = 50	#ms elapsed before animation ends

#Camera follow speed
# Must be 0 < N <= 1: 1 snaps to player location instantly, 0 breaks camera
CAM_LERP_X = .05
CAM_LERP_Y = .05

SAVE_COMPRESSION = True		#use GZip to compress save files, should make no difference
GEN_LEGACY_FILE = True		#dump message log text to .txt file, optional

#Inventory
CLOSE_AFTER_DROP = False	#quit inv menu after dropping item

CLOSE_AFTER_USE = True


#ASCII ICONS
scroll_icon = "ґ"
weapon_icon = ")"
armor_icon = "]"
food_icon = "ф"
potion_icon = "ї"

carcass_icon = "%"
ammo_icon = "ю"
liquid_icon = "~"
misc_icon = "*"

human_icon = "@"
guard_icon = "и"
player_icon = "Я"
game_animal_icon = "Ч"
eldritch_icon = "Ж"
draconic_icon = "Д"

consumable_icon = "%"
stairs_up_icon = ">"
stairs_down_icon = "<"
projectile_icon = "*"
portal_icon = "О"
door_open_icon = "|"
door_closed_icon = "+"
chest_icon = "П"



	###difficulty modifiers, see modifiers.txt for descriptions

#NOSING AROUND 
Mod1 = False
#DISORGANIZED 
Mod2 = False
#BAD LUCK
Mod3 = False
#YOU AND WHAT ARMY?
Mod4 = False
#ALL ABOARD THE PAIN TRAIN
Mod5 = False
#YOU DONE GOOFED
Mod6 = False
#WHERE'S THE ZIPPER?
Mod7 = False
#ARACHNOPHOBIA
Mod8 = False
#STEEL CITY, REPRESENT!
Mod9 = False
#
Mod10 = False




	###debug

ENABLE_DEBUG = True
DISPLAY_FPS = False

DEBUG_MOUSE_POSITON = False
DEBUG_MOUSE_DELTA = False
DEBUG_PRINT_TURNS = False
DEBUG_MOUSE_IN_INVENTORY = False

#background image for the main menu _ optionally remove
MAIN_MENU_BG_IMAGE = pygame.image.load("stars-in-the-night-sky.jpg")



