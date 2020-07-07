#3rd party modules
import pygame
import tcod as libtcod
#mport tcod

#necessary game files
import constants
#figure out this nonsense later
#path.append('/catalogs')

#import key_binds
import environ_cat
import actors_cat


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
	def __init__(self, x, y, name_object, sprite, creature = None, ai = None, container = None, item = None):
		#map addresses, later to be converted to pixel address
		self.x = x
		self.y = y
		self.name_object = name_object
		self.sprite = sprite
		self.IsInvulnerable = False

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

class obj_Game:
	def __init__(self):
		self.current_map = map_create()
		self.message_history = []
		self.current_objects = []


###############################################################################################################################
#components

class com_Creature:
	def __init__(self, name_instance, hp = 10, death_function = None):
		self.name_instance = name_instance
		self.maxhp = hp
		self.hp = hp
		self.death_function = death_function


		#add new damage types and stuff later
	def take_damage(self, damage):
		#game_message(self.name_instance +  "'s health is " + str(self.hp) + "/" + str(self.maxhp), constants.COLOR_RED)
		self.hp -= damage
		#print (self.name_instance + "'s health is " + str(self.hp) + "/" + str(self.maxhp))

		#possibly change later to include the name of the attacker
		if self.hp <= 0:

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
	def __init__(self, weight = 0.0, volume = 0.0, name = "foo"):
		self.weight = weight
		self.volume = volume
		self.name = name

		#pick up this item
	def pick_up(self, actor):
		if actor.container:
			if (actor.container.volume + self.volume) > actor.container.max_volume:
				game_message("Not enough volume to pick up " + self.name + ".")

			else:
				game_message("Picked up" + self.name + ".")
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


######################################################################################################################
#AI scripts
	#execute once per turn
class ai_Test:
	def take_turn(self):
		#script causes AI to move to random locations, remember for later (followers?)
		self.owner.creature.move(libtcod.random_get_int(0,-1, 1), libtcod.random_get_int(0, -1, 1))

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
	#draw_debug()

	draw_messages()

	#update the display
	pygame.display.flip()



	#game functions

#add multiple colors for the House
def draw_text(display_surface, text_to_display, font, T_coords, text_color, back_color = None):
	#this function takes in some text and displays it on the desired surface
	
	#draw_text(SURFACE_MAIN, str(int(CLOCK.get_fps())), (0, 0), constants.COLOR_BLACK)
	#text_x, text_y = T_coords
	T_coords = ((constants.TEXT_X_OVERRIDE * 3), (constants.TEXT_Y_OVERRIDE * 6))

#arguments are incoming_text, incoming_font, incoming_color, incoming_bg
	text_surf, text_rect = helper_text_objects(text_to_display, font, text_color, back_color)

	text_rect.topleft = T_coords

	display_surface.blit(text_surf, text_rect)

def draw_debug():
	if constants.DISPLAY_FPS :
		draw_text(SURFACE_MAIN, str(CLOCK.get_fps() + " frames per second."), (0, 0), constants.COLOR_GRAY, constants.COLOR_BLACK)
		#draw_text(SURFACE_MAIN, str(int(CLOCK.get_fps())), (0, 0), constants.COLOR_GRAY)
		print("This is a placeholder so I don't get a flipping error.")

def draw_messages():


	#to_draw = GAME_MESSAGES[-(constants.NUM_MESSAGES)]

	#start_x = constants.MAP_HEIGHT*constants.CELL_HEIGHT - (constants.NUM_MESSAGES * constants.FONT_MESSAGE_TEXT)

	#draw last 4 messages in the list
	if len(GAME.message_history) <= constants.NUM_MESSAGES:
		to_draw = GAME.message_history
	else:
		to_draw = GAME.message_history[-(constants.NUM_MESSAGES):]

	text_height = helper_text_height(constants.FONT_MESSAGE_TEXT)
	#text_height = 10

	#start_y = (constants.MAP_HEIGHT * constants.CELL_HEIGHT - (constants.NUM_MESSAGES * text_height)) #- 5
	start_y = ((constants.MAP_HEIGHT * constants.CELL_HEIGHT) - (constants.NUM_MESSAGES * text_height))

	
	#i = 0
	#for i in range(constants.NUM_MESSAGES):
	#for message, color in to_draw:
	#	message, color = to_draw[i]

	
	#for message, color in to_draw:
		#draw_text(SURFACE_MAIN, message, (start_y + (i * text_height), 0), color, constants.COLOR_WHITE) #here you change the color of the text, I think?
	for i, (message, color) in enumerate(to_draw):
		draw_text(SURFACE_MAIN,
		 			message, 
		 			constants.FONT_MESSAGE_TEXT,
		 			(0, start_y + (i * text_height)), 
		 			constants.COLOR_BLACK, 
		 			constants.COLOR_WHITE) #here you change the color of the text, I think?
		#i += 1
		#print("looped successfully")




#########################################################################################################
#helper functions
def helper_text_objects(incoming_text, incoming_font, incoming_color, incoming_bg):
	if incoming_bg:
		Text_surface = constants.FONT_DEBUG_MESSAGE.render(incoming_text, 
															constants.TEXT_AA, 
															#(1, 1, 1, 0), 
															incoming_color,
															incoming_bg)
	else:
		Text_surface = constants.FONT_DEBUG_MESSAGE.render(incoming_text, 
															constants.TEXT_AA, 
															#(1, 1, 1, 0), 
															incoming_color)


	return Text_surface, Text_surface.get_rect()


def helper_text_height(font):
	#font_object = font.render('a', False, (0, 0, 0))
	#font_rect = font_object.get_rect()
	font_rect = font.render('a', False, (0, 0, 0)).get_rect()

	return font_rect.height

def helper_text_width(font):
	#font_object = font.render('a', False, (0, 0, 0))
	#font_rect = font_object.get_rect()
	font_rect = font.render('a', False, (0, 0, 0)).get_rect()

	return font_rect.width

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

		pygame.display.flip()


def menu_inventory():
	menu_close = False

	#include different parameters later for teh lulz
	menu_width = 400
	menu_height = 700

	window_width = constants.MAP_WIDTH * constants.CELL_WIDTH
	window_height = constants.MAP_HEIGHT * constants.CELL_HEIGHT

	menu_text_font = constants.FONT_MESSAGE_TEXT
	menu_text_height = helper_text_height(menu_text_font)


	local_inventory_surface = pygame.Surface((menu_width, menu_height))
	
	while not menu_close:
		#clear the menu by wiping it black
		local_inventory_surface.fill(constants.COLOR_BLACK)

		print_list = [obj.name_object for obj in PLAYER.container.inventory]

		#register changes
		events_list = pygame.event.get()
		for event in events_list:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_i:
					menu_close = True

		#draw list
		for i, (name) in enumerate(print_list):
			draw_text(local_inventory_surface,
						name,
						menu_text_font,
						(0, 0 + (i * menu_text_height)),
						constants.COLOR_WHITE, constants.COLOR_BLACK

						)

		#display menu
		SURFACE_MAIN.blit(local_inventory_surface, 
				 ((window_width / 2) - (menu_width / 2),
				 (window_height / 2) - (menu_height / 2))
				)
			#(0, 0))
		pygame.display.update()
		

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
		#report framerate
		#remove/change parameter to change framerate limit
		CLOCK.tick(constants.GAME_FPS)

	#quit the game
	game_quit_sequence()
	
	#input updates have an artificial lag to prevent unnecessary movement, to be fixed later
		#remember, up/down is inverted and therefore confusing
		#move to a separate folder for organization's sake\

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
							if constants.HARDCORE_MODE == False:
								return "no-action"
								break

				if event.key == pygame.K_d:
					if len(PLAYER.container.inventory) > 0:
						PLAYER.container.inventory[-1].item.drop(PLAYER.x, PLAYER.y)
						if constants.HARDCORE_MODE == False:
							return "no-action"
							break

				#open (and later toggle) inventory menu
				if event.key == pygame.K_p:
					menu_pause()


				if event.key == pygame.K_i:
					menu_inventory()
					if constants.HARDCORE_MODE == False:
							return "no-action"
							break

				#pygame.time.wait(constants.ArtificialLag)




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

	container_com1 = com_Container()
	creature_com1 = com_Creature("The Mariner")    #player's creature component name
	PLAYER = obj_Actor(4, 6, "python", 
						actors_cat.S_PLAYER, 
						creature = creature_com1,
						container = container_com1)

	#spawn enemies

	#first enemy
	item_com1 = com_Item()
								#name of enemy when alive
	creature_com2 = com_Creature("Greater Nightcrawler", death_function = death_monster) #the crab's creature name
	ai_com1 = ai_Test()
							#name of item when picked up
	ENEMY = obj_Actor(5, 5, "Greater Nightcrawler carcass", actors_cat.S_ENEMY, 
		creature = creature_com2, ai = ai_com1, item = item_com1)

	#second enemy
	item_com2 = com_Item()
								#name of enemy when alive
	creature_com3 = com_Creature("Lesser Nightcrawler", death_function = death_monster) #the crab's creature name
	ai_com2 = ai_Test()
							#name of item when picked up
	ENEMY2 = obj_Actor(8, 9, "Lesser Nightcrawler carcass", actors_cat.S_ENEMY, 
		creature = creature_com3, ai = ai_com2, item = item_com2)


	#player listed last to be rendered on top of enemies
	GAME.current_objects = [ENEMY, ENEMY2, PLAYER]


if __name__ == '__main__':
	game_initialize()
	game_main_loop()	