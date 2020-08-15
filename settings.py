



#Camera follow speed
# Must be 0 < N <= 1: 1 snaps to player location instantly, 0 breaks camera
CAM_LERP_X = .05
CAM_LERP_Y = .05



#GRAPHICS
#toggle rendering ballistics (spells, projectiles, etc.), currently broken by camera refactor
RENDER_BALLISTICS = True
#ms elapsed before ballistic is cleared
BALLISTIC_TICK_UPPER = 50
#ms elapsed before next tick
BALLISTIC_TICK_LOWER = 50
#ms elapsed between explosion is cleared
EXPLOSION_TICK_UPPER = 50
#ms elapsed before animation ends
EXPLOSION_TICK_LOWER = 50


#use GZip to compress save files
SAVE_COMPRESSION = True





#render every tile with ASCII instead of bitmaps (legacy)
#RENDER_ASCII = True


	###game interface



	###menu


	###gameplay


#ASCI ICONS
scroll_icon = "ґ"
weapon_icon = ")"
armor_icon = "]"
food_icon = "ф"
potion_icon = "ї"
door_icon = "+"
chest_icon = "д"
guard_icon = "и"
human_icon = "@"
ammo_icon = "ю"
liquid_icon = "~"
consumable_icon = "%"
stairs_up_icon = ">"
stairs_down_icon = "<"


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



	###debug

ENABLE_DEBUG = True
DISPLAY_FPS = True

DEBUG_MOUSE_POSITON = False
DEBUG_MOUSE_DELTA = False
DEBUG_PRINT_TURNS = False



#Inventory
CLOSE_AFTER_USE = True