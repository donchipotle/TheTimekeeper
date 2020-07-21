#3rd party modules
import pygame
import tcod as libtcod
import math

#mport tcod

#necessary game files
import constants
import settings
#import toolbox


#import key_binds

#import asset catalogs
import environ_cat
import actors_cat
import misc_cat


#structures
class struc_Tile:
	def __init__(self, block_path): #add more variables like blocking projectiles, blocking sight, DoT, etc.
		self.block_path = block_path
		self.explored = False
		#maybe later replace with a 'light level' that accounts for actor size and potentially renders invisible if not in view?
		#light level falls off at a distance from light emitting actors?
		self.lit = False
		#for things like cages, fences, other permeable barriers
		self.transparent = False
		#used for comparing verticality - difference in elevation affects ranged weapon damage and maybe later sight
		self.elevation = 0

#class struc_Assets:
#objects
class obj_Actor:
	def __init__(self, x, y, name_object, sprite, creature = None, ai = None, container = None, item = None, 
		description = "No description for this actor."):
		#map addresses, later to be converted to pixel address
		self.x = x
		self.y = y
		self.name_object = name_object
		self.sprite = sprite
		self.IsInvulnerable = False
		self.description = description

		#replace sprite with letter/character, primary color and background color

		self.creature = creature
		if creature: 
			self.creature = creature
			self.creature.owner = self

		self.ai = ai
		if self.ai:
			#self.ai = ai
			self.ai.owner = self

		self.container = container
		if self.container:
			self.container.owner = self

		self.item = item
		if self.item:
			self.item.owner = self

	def draw(self):
		#is_visible = libtcod.map_is_in_fov(FOV_MAP, self.x, self.y)
		is_visible = libtcod.map_is_in_fov(FOV_MAP, self.x, self.y)

		if is_visible:
			SURFACE_MAIN.blit(self.sprite, (self.x*constants.CELL_WIDTH, self.y*constants.CELL_HEIGHT))
		#else 
		#takes in difference of x and difference of y

	def distance_to(self, other):
		delta_x = other.x - self.x
		delta_y = other.y - self.y
		return math.sqrt(delta_x ** 2 + delta_y ** 2)

	def move_towards(self, other):
		
		delta_x = other.x - self.x
		delta_y = other.y - self.y
		distance = math.sqrt(delta_x ** 2 + delta_y ** 2)

		delta_x = int(round(delta_x / distance))
		delta_y = int(round(delta_y/distance))

		#check later if this actually works or not
		#idk I'm actually pretty drunk right now so my judgment is probably off by a bit
		self.creature.move(delta_x, delta_y)
			
class obj_Game:
	def __init__(self):
		self.current_map = map_create()
		self.message_history = []
		self.current_objects = []

###############################################################################################################################
#components

class com_Creature:
	def __init__(self, name_instance, hp = 10, death_function = None, money = 0, gender = 0, base_xp = 15):
		self.name_instance = name_instance
		self.max_hp = hp
		self.current_hp = hp
		self.money = money
		self.death_function = death_function
		self.gender = gender
		self.base_xp = base_xp


		#add new damage types and stuff later
	def take_damage(self, damage):
		#game_message(self.name_instance +  "'s health is " + str(self.hp) + "/" + str(self.maxhp), constants.COLOR_RED)
		self.current_hp -= damage
		#print (self.name_instance + "'s health is " + str(self.hp) + "/" + str(self.maxhp))

		#possibly change later to include the name of the attacker
		if self.current_hp <= 0:

			if self.death_function is not None:
				self.death_function(self.owner)

		#else:
			#print (self.name_instance + "'s health is " + str(self.hp) + "/" + str(self.maxhp))
	def move(self, dx, dy):
		tile_is_wall = (GAME.current_map[self.owner.x + dx][self.owner.y + dy].block_path == True)

		target = map_check_for_creatures(self.owner.x + dx, self.owner.y + dy, self.owner)
		

		#possibly move this statement into loop above
		if target:
			#damage = (libtcod.random_get_int(self, 2, 4))
			damage = 4
			self.attack(target, damage)

		if not tile_is_wall and target is None:
			self.owner.x += dx
			self.owner.y += dy

	def attack(self, target, damage):
		game_message((self.name_instance + " attacks " + target.creature.name_instance + " and does " + str(damage) + " damage."), constants.COLOR_WHITE)
		target.creature.take_damage(damage)
	def heal(self, value):
		self.current_hp += value
		#include at a later date, the possibility of overhealing
		if self.current_hp > self.max_hp:
			self.current_hp = self.max_hp

class com_Container:
	def __init__(self, volume = 10.0, max_volume = 10.0,  inventory = []):
		self.inventory = inventory
		self.max_volume = volume
		self.volume = max_volume

		#names of everything in inventory
		#get volume within container
		@property 
		def volume(self):
			return 0.0


		#get weight of everything

class com_Item:
	def __init__(self, weight = 0.0, volume = 0.0, name = "foo", use_function = None, value = None):
		self.weight = weight
		self.volume = volume
		self.name = name
		self.value = value
		self.use_function = use_function

		#pick up this item
	def pick_up(self, actor):
		if actor.container:
			if (actor.container.volume + self.volume) > actor.container.max_volume:
				game_message("Not enough volume to pick up " + self.name + ".")

			else:
				game_message("Picked up " + self.name + ".")
				actor.container.inventory.append(self.owner)
				GAME.current_objects.remove(self.owner)
				self.container = actor.container
				#game_messge(self.name + " dropped.")
	def drop(self, new_x, new_y):
		GAME.current_objects.append(self.owner)
		self.container.inventory.remove(self.owner)

		self.owner.x = new_x
		self.owner.y = new_y

		#game_message("Item dropped.")


		#drop the item
		#use the item


		#active effects

		#consumables
	def use(self):
		if self.use_function:
			result = self.use_function(self.container.owner, self.value)
			#if result == "cancelled":
			if result is not None:
				print("use_function failed")
			else:
				self.container.inventory.remove(self.owner)

######################################################################################################################
#AI scripts
	#execute once per turn
class ai_Confuse:
	def __init__(self, old_ai, num_turns):
		self.old_ai = old_ai
		#number of turns remaining until AI script ends
		self.num_turns = num_turns

	def take_turn(self):
		if num_turns > 0:
		#script causes AI to move to random locations, remember for later (followers?)
			self.owner.creature.move(libtcod.random_get_int(0,-1, 1), libtcod.random_get_int(0, -1, 1))
			self.num_turns -= 1
		else:
			self.owner.ai = self.old_ai

class ai_Chase:
	#a basic ai script which chases and tries to harm the player
	#refactor later with target seleciton
	def take_turn(self):
		monster = self.owner

		if libtcod.map_is_in_fov(FOV_MAP, monster.x, monster.y):
			#move towards the player if far away (out of weapon reach)
			
			if monster.distance_to(PLAYER) >= 2:
				self.owner.move_towards(PLAYER)
			elif PLAYER.creature.current_hp > 0:
				monster.creature.attack(PLAYER, 3)

#class ai_Ranged_Assault:


#class ai_Ranged_Fall_Back:


#class ai_Retreat:

#class ai_Offensive_Spell:

#class ai_Crowd_Control:

class ai_ally_follow:
	def_take_turn(self):
		monster = self.owner

		if libtcod.map_is_in_fov(FOV_MAP, monster.x, monster.y):
		#move towards the player if far away (out of weapon reach)
			
			if monster.distance_to(PLAYER) >= 3:
				self.owner.move_towards(PLAYER)
		#maybe add in a script to wander in circles around the player
			elif:
				return


class com_AI:
	def take_turn(self):
		self.owner.creature.move(libtcod.random_get_int(0,-1, 1), libtcod.random_get_int(0, -1, 1))

class ai_Static:
	def take_turn(self):
		return

class ai_Player:
	def take_turn(self):
		return


def death_monster(monster):
	if monster.IsInvulnerable != True:
		#on death, most monsters stop moving
		#print (monster.creature.name_instance + " is killed!")
		
		game_message(monster.creature.name_instance + " is dead!", constants.COLOR_GRAY)
		monster.creature = None
		monster.ai = None
		#determine what to leave behind
	else:
		#print("Nice try. " + monster.creature.name_instance + " is invulnerable.")
		game_message("Nice try. " + monster.creature.name_instance + " is invulnerable.", constants.COLOR_GRAY)

###########################################################################################################################
#map functions

def map_create():
	new_map = [[ struc_Tile(False) for y in range(0, constants.MAP_HEIGHT)] for x in range (0, constants.MAP_WIDTH)]

	new_map[10][10].block_path = True
	new_map[10][15].block_path = True

	for x in range(constants.MAP_WIDTH):
		new_map[x][0].block_path = True
		new_map[x][constants.MAP_HEIGHT-1].block_path = True

	for y in range(constants.MAP_HEIGHT):
		new_map[0][y].block_path = True
		new_map[constants.MAP_WIDTH-1][y].block_path = True


	map_make_fov(new_map)

	return new_map


def draw_map(map_to_draw):
	for x in range(0, constants.MAP_WIDTH):
		for y in range(0,constants.MAP_HEIGHT):

			is_visible = libtcod.map_is_in_fov(FOV_MAP, x, y)

			if is_visible:

				map_to_draw[x][y].explored = True

				if map_to_draw[x][y].block_path == True:
					#draw wall
					SURFACE_MAIN.blit(environ_cat.S_WALL, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
				else:
					#draw floor
					SURFACE_MAIN.blit(environ_cat.S_FLOOR, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
			else:
				if map_to_draw[x][y].explored:
					if map_to_draw[x][y].block_path == True:
						#draw wall
						SURFACE_MAIN.blit(environ_cat.S_WALLEXPLORED, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))
					else:
						#draw floor
						SURFACE_MAIN.blit(environ_cat.S_FLOOREXPLORED, (x*constants.CELL_WIDTH, y*constants.CELL_HEIGHT))


#drawing functions

def draw_game():
	global SURFACE_MAIN, PLAYER #, GAME.current_map

	#clear the surface
	SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
	#draw the map
	draw_map(GAME.current_map)

	#draw all objects in the game
	for obj in GAME.current_objects:
		obj.draw()

	#fix at some point idk tho
	if settings.ENABLE_DEBUG == True:
		draw_debug()

	draw_messages()


	#game functions
	#add multiple colors for the House
	#def draw_text(display_surface, text_to_display, font, T_coords, text_color, back_color = None):
	#this function takes in some text and displays it on the desired surface
	
	#draw_text(SURFACE_MAIN, str(int(CLOCK.get_fps())), (0, 0), constants.COLOR_BLACK)
	#text_x, text_y = T_coords
	#T_coords = ((constants.TEXT_X_OVERRIDE * 3), (constants.TEXT_Y_OVERRIDE * 6))

def draw_text(display_surface, text_to_display, font, coords, text_color, back_color = None, center = False):
    # get both the surface and rectangle of the desired message
    text_surf, text_rect = helper_text_objects(text_to_display, font, text_color, back_color)
    
    if not center:
    	text_rect.topleft = coords

    else:
    	text_rect.center = coords

    # draw the text onto the display surface.

    display_surface.blit(text_surf, text_rect)
    #SURFACE_MAIN.blit(local_inventory_surface, (menu_x, menu_y))

def draw_debug():
	if settings.DISPLAY_FPS :
	    draw_text(SURFACE_MAIN,
              "fps: " + str(int(CLOCK.get_fps())),
              constants.FONT_DEBUG_MESSAGE,
              (0, 0),
              constants.COLOR_WHITE,
              constants.COLOR_BLACK)

def draw_messages():
	#include 'timer' for clearing message log, later



	#add last 4 messages to the queue
	if len(GAME.message_history) <= constants.NUM_MESSAGES:
		to_draw = GAME.message_history
	else:
		to_draw = GAME.message_history[-(constants.NUM_MESSAGES):]

	text_height = helper_text_height(constants.FONT_MESSAGE_TEXT)

	start_y = (((constants.MAP_HEIGHT * constants.CELL_HEIGHT) - (constants.NUM_MESSAGES * text_height)) - 20)

	#print(start_y)
    # get both the surface and rectangle of the desired message

	for i, (message, color) in enumerate(to_draw):
		draw_text(SURFACE_MAIN, 
			message, 
			constants.FONT_MESSAGE_TEXT, 
			(20, start_y + (i * text_height)), 
			color, constants.COLOR_BLACK)

def draw_tile_rect(coords, tile_color = None, tile_alpha = None, mark = None):
	x, y = coords

	#default tile colors
	if tile_color: local_color = tile_color
	else: local_color = constants.COLOR_WHITE

	#default alpha
	if tile_alpha: local_alpha = tile_alpha
	else: local_alpha = 150

	new_x = x * constants.CELL_WIDTH
	new_y = y * constants.CELL_HEIGHT

	new_surface = pygame.Surface((constants.CELL_WIDTH, constants.CELL_HEIGHT))

	new_surface.fill((tile_color))
	#new_surface.fill(misc_cat.S_SELECTED_DEFAULT)

	new_surface.set_alpha(local_alpha)

	if mark:
		#move the centering calculation elsewhere to prevent unnecessary calculations
		draw_text(new_surface, mark, font = constants.FONT_CURSOR_TEXT, 
				coords = (constants.CELL_WIDTH/2, constants.CELL_HEIGHT/2), 
				text_color = constants.COLOR_BLACK, center = True)

	SURFACE_MAIN.blit(new_surface, (new_x, new_y))

#factor into ballistic weapons and spells later, possibly move damage over to this function under 'handle projectiles'
def draw_projectile(ballistic_x, ballistic_y, projectile_color):
	print("Drawing projectiles on screen.")
	projectile_surface = pygame.Surface((constants.CELL_WIDTH, constants.CELL_HEIGHT))
	projectile_surface.fill(projectile_color)
	#new_surface.fill(misc_cat.S_SELECTED_DEFAULT)
	projectile_surface.set_alpha(150)

	#render ballistic
	SURFACE_MAIN.blit(projectile_surface, (ballistic_x * constants.CELL_WIDTH, ballistic_y * constants.CELL_HEIGHT))
	pygame.display.flip()
	#ballistic tick duration
	pygame.time.delay(settings.BALLISTIC_TICK_UPPER)
	#clear ballistic
	projectile_surface.fill((0, 0, 0))
	draw_game()
	pygame.display.flip()
	#time between ticks
	pygame.time.delay(settings.BALLISTIC_TICK_LOWER)
	#end after iterating



#allow blast to expand from center, at a later date
def draw_explosion(radius, blast_x, blast_y, color):
	print("This is a placeholder for when explosions and other AoE actions are properly taken care of.")
	
	#explosion_surface = pygame.Surface((constants.CELL_WIDTH, constants.CELL_HEIGHT))
	#explosion_surface.set_alpha(150)
	#explosion_surface.fill(color)

	area_effect = map_find_radius(valid_tiles[-1], radius)
	for (tile_x, tile_y) in area_effect:
			draw_tile_rect((tile_x, tile_y), color)

	#(ballistic_x * constants.CELL_WIDTH, ballistic_y * constants.CELL_HEIGHT))

	#SURFACE_MAIN.blit(explosion_surface, ((blast_x * constants.CELL_WIDTH), (blast_y * constants.CELL_HEIGHT)))
	#pygame.display.flip()
	#pygame.time.delay(settings.EXPLOSION_TICK_UPPER)

	#explosion_surface.fill((0, 0, 0))



	#draw_game()


###############################################################################################################
#helper functions

def helper_text_objects(incoming_text, incoming_font, incoming_color, incoming_bg):
    # if there is a background color, render with that.
    if incoming_bg:
        Text_surface = incoming_font.render(incoming_text,
                                            False,
                                            incoming_color,
                                            incoming_bg)

    else:  # otherwise, render without a background.
        Text_surface = incoming_font.render(incoming_text,
                                            False,
                                            incoming_color)

    return Text_surface, Text_surface.get_rect()

def helper_text_height(font):
	#font_object = font.render('a', False, (0, 0, 0))
	#font_rect = font_object.get_rect()
	font_rect = font.render('a', False, (0, 0, 0)).get_rect()

	#print(font_rect.height)
	return font_rect.height

def helper_text_width(font):
	#font_object = font.render('a', False, (0, 0, 0))
	#font_rect = font_object.get_rect()
	font_rect = font.render('a', False, (0, 0, 0)).get_rect()

	#print(font_rect.width)
	return font_rect.width

###############################################################################################################
#magic

def cast_heal(target, value):
	if target.creature.current_hp == target.creature.max_hp:
		game_message(target.creature.name_instance + " is already at full health.")
		return "cancelled"

	else:
		game_message(target.creature.name_instance + " the " + target.name_object + " healed for " + str(value) + " health.")
		target.creature.heal(value)

		if target.creature.current_hp >= target.creature.max_hp:
			game_message(target.creature.name_instance + " is now at full health.")
		print(target.creature.current_hp)
		
	return None

def cast_lightning():

	damage = 5
	
	player_location = (PLAYER.x, PLAYER.y)

	# prompt player for a tile
	point_selected = menu_tile_select(coords_origin = player_location, 
		max_range = 5, penetrate_walls = False)

	if point_selected:
	# convert that tile into a list of coordinates, A -> B
		list_of_tiles = map_find_line(player_location, point_selected)

		#cycle through list and damage everything found
		for i, (x, y) in enumerate(list_of_tiles):
			if settings.RENDER_BALLISTICS:
				draw_projectile(x, y, constants.COLOR_L_BLUE)
			target = map_check_for_creatures(x, y)
			if target: # and i != 0:
				game_message("The Mariner casts Alenko-Kharyalov Effect.")
				#check if spell uselessly hits wall
				#if (target.x, target.y)  
				target.creature.take_damage(damage)

				#if target.creature.name_instance:
				#	game_message(target.creature.name_instance + " takes " + str(damage) + " damage.")
		return "no-action"
	#later, render effect on each tile in sequence

def cast_fireball():
	#definitions, change later
	damage = 5
	local_radius = 2
	max_r = 10
	player_location = (PLAYER.x, PLAYER.y)


	#TODO get target tile
	point_selected = menu_tile_select(coords_origin = player_location, max_range = max_r,
		 penetrate_walls = False, 
		 pierce_creature = False, 
		 radius = local_radius)

	if point_selected:
		game_message(PLAYER.creature.name_instance + " casts Alenko-Kharyalov Conflagration.")
		#get sequence of tiles
		tiles_to_damage = map_find_radius(point_selected, local_radius)
		creature_hit = False

		

		#damage all creatures in tiles
		for (x, y) in tiles_to_damage:
			#add visual feedback to fireball, maybe even adding a trail to its destination later
			#draw_explosion(radius, x, y, constants.COLOR_ORANGE)

			creature_to_damage = map_check_for_creatures(x, y)
			if creature_to_damage: 
				creature_to_damage.creature.take_damage(damage)
				
				if creature_to_damage is not PLAYER:
					creature_hit = True

		if creature_hit:
			game_message("You hear the disgusting sizzling sound of burning flesh.", constants.COLOR_RED)

def cast_confusion():
	#select tile
	point_selected = menu_tile_select(max_range = 12)
				#radius = local_radius)

	#get target from that tile
	if point_selected:
		(tile_x, tile_y) = point_selected
		target = map_check_for_creatures(tile_x, tile_y)

		#temporarily confuse the target
		if target:
			oldai = target.ai

			target.ai = ai_Confuse(old_ai = oldai, num_turns = 5)
			target.ai.owner = target
			game_message(target.creature.name_instance + " is confused.", constants.COLOR_GREEN)
			#print(target.creature.name_instance + " is confused.")
			


	 



###############################################################################################################
#menus

def menu_pause():
	#this pauses the game and displays a simple message
	#probably gonna remove because I don't think I really even need this part, but that's for later
	menu_close = False

	#move this block into the init later
	window_width = constants.MAP_WIDTH * constants.CELL_WIDTH
	window_height = constants.MAP_HEIGHT * constants.CELL_HEIGHT
	
	menu_text = "PAUSED, press P to return to game or exit."
	menu_font = constants.FONT_DEBUG_MESSAGE
	
	text_height = helper_text_height(menu_font)
	text_width = (len(menu_text) * helper_text_width(menu_font))



	while not menu_close:
		events_list = pygame.event.get()
		for event in events_list:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_p:
					menu_close = True


		draw_text(SURFACE_MAIN, menu_text, constants.FONT_DEBUG_MESSAGE,
			 ((window_width / 2) - (text_width / 2), (window_height / 2) - (text_height / 2)), 
			  constants.COLOR_WHITE, constants.COLOR_BLACK)
		CLOCK.tick(constants.GAME_FPS)

		pygame.display.flip()

def menu_inventory():
	menu_close = False


	window_width = constants.MAP_WIDTH * constants.CELL_WIDTH
	window_height = constants.MAP_HEIGHT * constants.CELL_HEIGHT

	#include different parameters later for teh lulz
	menu_width = 900
	menu_height = 700
	menu_x = (window_width / 2) - (menu_width / 2)
	menu_y = (window_height / 2) - (menu_height / 2)


	menu_text_font = constants.FONT_MESSAGE_TEXT

	menu_text_height = helper_text_height(menu_text_font)

	#local_inventory_surface = pygame.Surface((menu_width, menu_height))
	local_inventory_surface = pygame.Surface((menu_width, menu_height))
	
	while not menu_close:
		#clear the menu by wiping it black
		local_inventory_surface.fill(constants.COLOR_BLACK)

		print_list = [obj.name_object for obj in PLAYER.container.inventory]

		#register changes
		events_list = pygame.event.get()


		mouse_x, mouse_y = pygame.mouse.get_pos()
		if settings.DEBUG_MOUSE_POSITON == True:
			print(mouse_x, mouse_y)

		delta_x = mouse_x - menu_x
		delta_y = mouse_y - menu_y

		mouse_in_window = (delta_x > 0 and 
						   delta_y > 0 and
						   delta_x < menu_width and
						   delta_y < menu_height)


		#replace conversation -> int function later
		mouse_line_selection = int(delta_y / menu_text_height)

		#if mouse_in_window == True:
			#temporarily commented out

			#print(mouse_line_selection)



		if settings.DEBUG_MOUSE_DELTA == True:
			if delta_x > 0 and delta_y > 0:
				print(delta_x, delta_y)

		for event in events_list:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_i:
					menu_close = True
					COLOR_GRAY = (100, 100, 100)

			if event.type == pygame.MOUSEBUTTONDOWN:
				#print(event.button) #gets the id of button clicked, returns int
				#if (event.button == 1 or 2 or 3):
				if (event.button == 1):

					if (mouse_in_window and 
						mouse_line_selection <= len(print_list) - 1):
						#PLAYER.container.inventory[mouse_line_selection].item.drop(PLAYER.x, PLAYER.y)
						PLAYER.container.inventory[mouse_line_selection].item.use()
						#print(True)


					

		for line, (name) in enumerate(print_list):
			if line == mouse_line_selection and mouse_in_window == True:
				draw_text(local_inventory_surface,
					name,
					menu_text_font,
					(0, 0 + (line * menu_text_height)), constants.COLOR_WHITE, constants.COLOR_GRAY)
			else:
				draw_text(local_inventory_surface,
					name,
					menu_text_font,
					(0, 0 + (line * menu_text_height)), constants.COLOR_WHITE)

		#display menu
		SURFACE_MAIN.blit(local_inventory_surface, (menu_x, menu_y))
			
		CLOCK.tick(constants.GAME_FPS)
		pygame.display.update()

def menu_tile_select(coords_origin = None, max_range = None, 
	radius = None, penetrate_walls = True, pierce_creature = True):
	#this menu lets the player select a tile 

	#this function pauses the game, produces an on screen rectangle and 
	#containing the map address

	menu_close = False

	while not menu_close:
		#get mouse postion
		mouse_x, mouse_y = pygame.mouse.get_pos()

		#get button clicks
		events_list = pygame.event.get()

		#mouse map selection
		map_coord_x = int(mouse_x / constants.CELL_WIDTH)
		map_coord_y = int(mouse_y/constants.CELL_HEIGHT)

		valid_tiles = []

		if coords_origin:
			full_list_of_tiles = map_find_line(coords_origin, (map_coord_x, map_coord_y))

			for i, (x, y) in enumerate(full_list_of_tiles):
				valid_tiles.append((x, y))
				#stop at max range
				if max_range and i == max_range:
					break
				#stop at wall
				if not penetrate_walls and GAME.current_map[x][y].block_path: 
					break
				#stop at creature
				if not pierce_creature and map_check_for_creatures(x, y):
					break

		else:
			valid_tiles = [(map_coord_x, map_coord_y)]

		#get map coords on  LMB
		for event in events_list:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_l:
					menu_close = True

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					return(valid_tiles[-1])
	
		draw_game()
		#draw rect at mouse position over game screen, marking tile targeted
		for (tile_x, tile_y) in valid_tiles:
			if (tile_x, tile_y) == valid_tiles[-1]:
				draw_tile_rect(tile_color = constants.COLOR_WHITE, coords = (tile_x, tile_y), mark = "X")
			else:
				draw_tile_rect(tile_color = constants.COLOR_BLACK, coords = (tile_x, tile_y))

		#draw theoretical blast radius of AoE spells
		if radius:
			area_effect = map_find_radius(valid_tiles[-1], radius)
			for (tile_x, tile_y) in area_effect:
				draw_tile_rect(coords = (tile_x, tile_y),
					tile_color = constants.COLOR_ORANGE,
					tile_alpha = 150)

		#draw rectangle at mouse position
		draw_tile_rect(tile_color = constants.COLOR_WHITE, coords = (map_coord_x, map_coord_y))

		pygame.display.flip()
		CLOCK.tick(constants.GAME_FPS)

###############################################################################################################
#map functions
def map_make_fov(incoming_map):
	global FOV_MAP

	#OV_MAP  = libtcod.map_new(constants.MAP_WIDTH, constants.MAP_HEIGHT)
	FOV_MAP = libtcod.map_new(constants.MAP_WIDTH, constants.MAP_HEIGHT)

	for y in range(constants.MAP_HEIGHT):
		for x in range(constants.MAP_WIDTH):
			libtcod.map_set_properties(FOV_MAP, x, y, 
				not incoming_map[x][y].block_path, not incoming_map[x][y].block_path)

def map_calculate_fov():
	global FOV_CALCULATE
	#global FOV_MAP
	#map_make_fov(incoming_map)

	if FOV_CALCULATE:
		FOV_CALCULATE = False
		libtcod.map_compute_fov(FOV_MAP, PLAYER.x, PLAYER.y, constants.TORCH_RADIUS, constants.FOV_LIGHT_WALLS, 
			constants.FOV_ALGO)

def map_objects_at_coords(coords_x, coords_y):
	object_options = [obj for obj in GAME.current_objects 
	if obj.x == coords_x and obj.y ==coords_y]

	return object_options

def map_check_for_creatures(x, y, exclude_object = None):
	target = None
	if exclude_object:
		#check objectlist to find creature at that location that isn't excluded
		#include check to determine if hostile or not
		for object in GAME.current_objects:
			if (object is not exclude_object and 										
				object.x == x and 
				object.y == y and 		
				object.creature):												
					target = object					
			if target:
				return target
	else:
		#check objectlist to find any creature at that location ???
		for object in GAME.current_objects:
			if (
			#ability to attack thin air? 										
				object.x == x and 
				object.y == y and 		
				object.creature):												
					target = object				
			if target:
				return target	

def map_find_line(startcoords, endcoords):
	#converts beginning/end point tuples (X, Y) into list of tiles between
	(start_x, start_y) = startcoords
	
	(end_x, end_y) = endcoords

	libtcod.line_init(start_x, start_y, end_x, end_y)

	calc_x, calc_y = libtcod.line_step()

	coord_list = []

	if (start_x == end_x) and (start_y == end_y):
		print("Spell targeting self.")
		return[(start_x, start_y)]

	while (not calc_x is None):
		coord_list.append((calc_x, calc_y))

		calc_x, calc_y = libtcod.line_step()
	return coord_list

def map_find_radius(coords, radius):
	center_x, center_y = coords

	tile_list = []

	#define the bounds of the spell blast radius
	start_x = center_x - radius
	end_x = center_x + radius + 1
	start_y = center_y - radius
	end_y = center_y + radius + 1

	#two dimensional iterator
	for x in range((start_x), (end_x)):
		for y in range((start_y), (end_y)):
			tile_list.append((x, y))
	return tile_list

def map_tile_query():
	print("Map tile query initialized.")
	menu_close = False

	while not menu_close:
		player_location = (PLAYER.x, PLAYER.y)

		#get mouse postion
		mouse_x, mouse_y = pygame.mouse.get_pos()

		#get button clicks
		events_list = pygame.event.get()

		#mouse map selection
		map_coord_x = int(mouse_x/constants.CELL_WIDTH)
		map_coord_y = int(mouse_y/constants.CELL_HEIGHT)

		draw_tile_rect((mouse_x, mouse_y))

		menu_tile_select(penetrate_walls = True)
	
		#get map coords on  LMB
		for event in events_list:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
						menu_close = True
						print("Map tile query terminated.")

################################################################################################################

#Main game loop, on tick
def game_main_loop():
	global TURNS_ELAPSED

	game_quit = False

	player_action = "no-action"

	while not game_quit:
		#player input
		
		#player_action = key_binds.game_handle_keys()
		player_action = game_handle_keys()

		#map_make_fov(incoming_map)

		map_calculate_fov()

		if player_action == "QUIT":
			game_quit = True

		if player_action != "no-action":
			for obj in GAME.current_objects:
				if obj.ai: # != None:
					obj.ai.take_turn()
			#increment player turn counter for speedrun purposes
			TURNS_ELAPSED += 1
			print(str(TURNS_ELAPSED) + " turns have elapsed so far")
		#render the game
		draw_game()

		#update the display
		pygame.display.flip()

		#tick the clock
		CLOCK.tick(constants.GAME_FPS)



	#quit the game
	game_quit_sequence()

#########################################################################################################
	#input updates 
		#remember, up/down is inverted and therefore confusing
		#move to a separate folder for organization's sake

def game_handle_keys():
	global FOV_CALCULATE
	events_list = pygame.event.get()
	for event in events_list:
		if event.type == pygame.QUIT:
			return "QUIT"	

		#TODO - activities like picking up items cost a turn on hardcore mode
		if event.type == pygame.KEYDOWN:
				#arrow bindings, probably redundant
				if event.key == pygame.K_UP:
					PLAYER.creature.move(0, -1)
				if event.key == pygame.K_DOWN:
					PLAYER.creature.move(0, 1)
				if event.key == pygame.K_LEFT:
					PLAYER.creature.move(-1, 0)
				if event.key == pygame.K_RIGHT:
					PLAYER.creature.move(1, 0)
				#numpad bindings
				if event.key == pygame.K_KP1:
					PLAYER.creature.move(-1, 1)
				if event.key == pygame.K_KP2:
					PLAYER.creature.move(0, 1)
				if event.key == pygame.K_KP3:
					PLAYER.creature.move(1, 1)
				if event.key == pygame.K_KP4:
					PLAYER.creature.move(-1, 0)
				#this one does literally nothing, just kinda sitting here till I feel like using it
				if event.key == pygame.K_KP5:
					PLAYER.creature.move(0, 0)
				if event.key == pygame.K_KP6:
					PLAYER.creature.move(1, 0)
				if event.key == pygame.K_KP7:
					PLAYER.creature.move(-1, -1)
				if event.key == pygame.K_KP8:
					PLAYER.creature.move(0, -1)
				if event.key == pygame.K_KP9:
					PLAYER.creature.move(1, -1)

				#non-movement, non turn-changing ?
				if event.key == pygame.K_COMMA:
					objects_at_player = map_objects_at_coords(PLAYER.x, PLAYER.y)
					for obj in objects_at_player:
						if obj.item:
							obj.item.pick_up(PLAYER)
							if settings.Mod2 == False:
								return "no-action"
								

				if event.key == pygame.K_d:
					if len(PLAYER.container.inventory) > 0:
						PLAYER.container.inventory[-1].item.drop(PLAYER.x, PLAYER.y)
						if settings.Mod2 == False:
							return "no-action"
							

				#open (and later toggle) inventory menu
				if event.key == pygame.K_p:
					menu_pause()


				if event.key == pygame.K_i:
					menu_inventory()
					if settings.Mod2 == False:
						return "no-action"
						#break

				if event.key == pygame.K_q:
					map_tile_query()
					if settings.Mod2 == False:
						return "no-action"
						#break

				#key L, turn on tile selection. change later as needed
				if event.key == pygame.K_l:
					#menu_tile_select()
					#cast_lightning(9)
					cast_confusion()

				FOV_CALCULATE = True
				return "player-moved"
	return "no-action"

def game_message(game_msg, msg_color = constants.COLOR_WHITE):
	GAME.message_history.append((game_msg, msg_color))

def game_quit_sequence():
	pygame.quit()
	pygame.font.quit()
	exit()

#'''initializing the main window and pygame'''
def game_initialize():

	global SURFACE_MAIN, GAME, CLOCK, FOV_CALCULATE, PLAYER, ENEMY, TURNS_ELAPSED

	pygame.init()

	if constants.PermitKeyHolding == True:
		pygame.key.set_repeat(constants.KeyDownDelay, constants.KeyRepeatDelay)

	#create the rendered window
	SURFACE_MAIN = pygame.display.set_mode((constants.MAP_WIDTH * constants.CELL_WIDTH, 
											constants.MAP_HEIGHT * constants.CELL_HEIGHT))

	GAME = obj_Game

	CLOCK = pygame.time.Clock()

	FOV_CALCULATE = True

	TURNS_ELAPSED = 0

	#map_make_fov(incoming_map)

	#creatures

	GAME.current_map = map_create()
	GAME.message_history = []

	#create the player
	container_com1 = com_Container()
	creature_com1 = com_Creature("Bob The Guy")    #player's creature component name
	PLAYER = obj_Actor(4, 6, "python", 
						actors_cat.S_PLAYER, 
						creature = creature_com1,
						container = container_com1
						)

	#spawn enemies

	#first enemy
	item_com1 = com_Item(value = 7, use_function = cast_heal, name = "Greater Nightcrawler carcass")  #FYI, pass function in as parameter without parentheses
								#name of enemy when alive
	creature_com2 = com_Creature("Greater Nightcrawler", death_function = death_monster) #the crab's creature name
	ai_com1 = ai_Chase()
							#name of item when picked up
	ENEMY = obj_Actor(5, 5, "Greater Nightcrawler carcass", actors_cat.S_ENEMY, 
		creature = creature_com2, ai = ai_com1, item = item_com1)

	#second enemy
	item_com2 = com_Item(value = 3, use_function = cast_heal, name = "Lesser Nightcrawler carcass")
								#name of enemy when alive
	creature_com3 = com_Creature("Lesser Nightcrawler", death_function = death_monster) #the crab's creature name
	ai_com2 = ai_Chase()
							#name of item when picked up
	ENEMY2 = obj_Actor(8, 9, "Lesser Nightcrawler carcass", actors_cat.S_ENEMY, 
		creature = creature_com3, ai = ai_com2, item = item_com2)


	#player listed last to be rendered on top of enemies
	GAME.current_objects = [ENEMY, ENEMY2, PLAYER]


if __name__ == '__main__':
	game_initialize()
	game_main_loop()	