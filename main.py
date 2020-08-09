#3rd party modules
import pygame
import tcod as libtcod
import math

#import tcod

#necessary game files
import constants
import settings
#import toolbox


#for dice rolls, move when that function is moved too
import random


#import key_binds

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
	def __init__(self, x, y,

		name_object,
		creature = None, 
		ai = None, 

		container = None, 
		item = None, 
		description = "No description for this actor.", 

		num_turns = 0, 
		icon = "x", 
		icon_color = constants.COLOR_WHITE,
		equipment = None,
		interact_function = None
		):

		#map addresses, later to be converted to pixel address
		self.x = x
		self.y = y
		self.name_object = name_object
		self.IsInvulnerable = False
		self.description = description

		self.icon = icon
		self.icon_color = icon_color

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

		self.equipment = equipment
		if self.equipment:
			self.equipment.owner = self

			self.item = com_Item()
			self.item.owner = self

	@property
	def display_name(self):
		if self.creature:
			return(self.creature.name_instance + " the " + self.name_object)

		if self.item:
			if self.equipment and self.equipment.equipped:
				return (self.name_object + "(" + self.equipment.slot + ")") 
			else:
				return self.name_object

	def draw(self):
		#is_visible = libtcod.map_is_in_fov(FOV_MAP, self.x, self.y)
		is_visible = libtcod.map_is_in_fov(FOV_MAP, self.x, self.y)

		if is_visible:
			draw_text(SURFACE_MAP, text_to_display = self.icon, font = constants.FONT_RENDER_TEXT, 
				coords = ((self.x * constants.CELL_WIDTH) + 16 , (self.y * constants.CELL_HEIGHT) + 16), 
				text_color = self.icon_color, 
				center = True)

			#SURFACE_MAIN.blit(self.sprite, (self.x*constants.CELL_WIDTH, self.y*constants.CELL_HEIGHT))
			
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
		#self.current_map = map_create()
		self.message_history = []
		self.current_objects = []

	#this is a rectangle that lives on the map
class obj_Room:
	def __init__(self, coords, size): #coords are upper left corner location 
		self.x1, self.y1 = coords
		self.w, self.h = size

		self.x2 = self.x1 + self.w
		self.y2 = self.y1 + self.h

	@property
	def center(self):
		center_x = ((self.x1 + self.x2) // 2)
		center_y = ((self.y1 + self.y2) // 2)

		return (center_x, center_y)

	def intersect(self, other):
		#return true if another obj intersects with this one
		objects_intersect = (self.x1 <= other.x2 and self.x2 >= other.x1 and
                             self.y1 <= other.y2 and self.y2 >= other.y1)

		#return objects_intersect
		return objects_intersect

class obj_Camera:
	def __init__(self):
		self.width = constants.CAM_WIDTH
		self.height = constants.CAM_HEIGHT
		self.x, self.y = (0,0)

	def update(self): #include some code to move along with the selection cursor

		target_x = PLAYER.x * constants.CELL_WIDTH + constants.CELL_HALF_WIDTH
		target_y = PLAYER.y * constants.CELL_HEIGHT + constants.CELL_HALF_HEIGHT

		distance_x, distance_y = self.map_dist((target_x, target_y))

		self.x += int(distance_x * settings.CAM_LERP_X)
		self.y += int(distance_y * settings.CAM_LERP_Y)

	@property
	def rectangle(self):
		pos_rect = pygame.Rect((0,0), (constants.CAM_WIDTH, constants.CAM_HEIGHT))
		pos_rect.center = (self.x, self.y)

		return pos_rect

	@property 
	def map_address(self):
		map_x = self.x / constants.CELL_WIDTH
		map_y = self.y / constants.CELL_HEIGHT
		return (map_x, map_y)

	def map_dist(self, coords):
		new_x, new_y = coords
		dist_x = new_x - self.x
		dist_y = new_y - self.y

		return(dist_x, dist_y)

	def cam_dist(self, coords):
		win_x, win_y = coords
		dist_x = win_x - (self.width / 2)
		dist_y = win_y - (self.height / 2)

		return (dist_x, dist_y)

	def win_to_map(self, coords):  #
		
		target_x, target_y = coords
		#convert window coords -> distance from camera
		cam_d_x, cam_d_y = self.cam_dist((target_x, target_y))

		#distance from cam -> map coord

		map_p_x = self.x + cam_d_x
		map_p_y = self.y + cam_d_y

		return((map_p_x, map_p_y))




###############################################################################################################################
#components

class com_Creature:
	def __init__(self, name_instance, 
		hp = 10, base_attack = 5, base_defense = 5, 
		death_function = None, money = 0, gender = 0, base_xp = 15):
		self.name_instance = name_instance
		self.max_hp = hp
		self.current_hp = hp
		self.money = money
		self.death_function = death_function
		self.gender = gender
		self.base_xp = base_xp
		self.base_attack = base_attack
		self.base_defense = base_defense

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

			self.attack(target, 3)

		if not tile_is_wall and target is None:
			self.owner.x += dx
			self.owner.y += dy

	def attack(self, target, damage):

		damage_dealt = self.power - target.creature.defense

		if (damage_dealt < 0):
			game_message(self.name_instance + " fails to do any damage " + target.creature.name_instance + " at all.")

		else:
			game_message((self.name_instance + " attacks " + target.creature.name_instance + " and does " + str(damage_dealt) + " damage."), constants.COLOR_WHITE)
			target.creature.take_damage(damage_dealt)

	def heal(self, value):
		self.current_hp += value
		#include at a later date, the possibility of overhealing
		if self.current_hp > self.max_hp:
			self.current_hp = self.max_hp

	@property
	def power(self):
		total_power = self.base_attack
		object_bonuses = []
		if self.owner.container:
			object_bonuses = [obj.equipment.attack_bonus 
			for obj in self.owner.container.equipped_items]

		for bonus in object_bonuses:
			if bonus:
				total_power += bonus

		return total_power

	@property
	def defense(self):
		total_defense = self.base_defense

		object_bonuses = []
		if self.owner.container:
			object_bonuses = [obj.equipment.defense_bonus
								for obj in self.owner.container.equipped_items]
		for bonus in object_bonuses:
			if bonus:
				total_defense += bonus

		return total_defense

class com_Container:
	def __init__(self, volume = 10.0, max_volume = 10.0,  inventory = []):
		self.inventory = inventory
		self.max_volume = volume
		#self.volume = max_volume

		#names of everything in inventory
		#get volume within container
	@property 
	def volume(self):
		return 0.0

	@property
	def equipped_items(self):
		list_of_equipped_items = [obj for obj in self.inventory 
									if obj.equipment and obj.equipment.equipped ]
		return list_of_equipped_items

		#get weight of everything

class com_Item:
	def __init__(self, weight = 0.0, volume = 0.0, name = "foo", use_function = None, value = None, slot = None):
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
				print("Can't pick up.")

			else:
				print("Picked up.")
				game_message("Picked up " + self.name + ".")
				print("item picked up is " + self.name)
				actor.container.inventory.append(self.owner)
				GAME.current_objects.remove(self.owner)
				#self.container = actor.container
				self.current_container = actor.container
				#game_messge(self.name + " dropped.")
	def drop(self, new_x, new_y):
		GAME.current_objects.append(self.owner)
		self.current_container.inventory.remove(self.owner)

		self.owner.x = new_x
		self.owner.y = new_y

		#game_message("Item dropped.")


		#drop the item
		#use the item


		#active effects

		#consumables
	def use(self):
		if self.owner.equipment:
			self.owner.equipment.toggle_equip()
			return
		#else: 
		#	print("Equipment's not working. Typical.")
		

		if self.use_function:
			result = self.use_function(self.current_container.owner, self.value)
			#result = self.use_function(self.container.owner, self.value)
			#if result == "canceled":
			if result is not None:
				print("use_function failed")
			else:
				self.current_container.inventory.remove(self.owner)

#add more bonuses later
class com_Equipment:
	def __init__(self, attack_bonus = None, defense_bonus = None, slot = None, name = None):
		self.attack_bonus = attack_bonus
		self.defense_bonus = defense_bonus

		self.slot = slot
		self.equipped = False


	def toggle_equip(self):
		print("Equip toggle function called.")
		if self.equipped:
			self.unequip()

		else:
			self.equip()

	def equip(self):
		#toggle self.equipped

	
		all_equipped_items = self.owner.item.current_container.equipped_items
		

		for item in all_equipped_items:
			#if item.equipment.slot and (item.equipment.slot != self.slot):
			if item.equipment.slot and (item.equipment.slot == self.slot):
				game_message(self.slot + " is already occupied.", constants.COLOR_RED)
					#ynaq prompt?
				return
		self.equipped = True
		print("Equipped successfully")
		game_message("Equipped in " + (str(self.slot)) + ".")
			
	#toggle self.equipped
	def unequip(self):
		print("Unequip function called.")	
		self.equipped = False
		#game_message(self.item.equipment.slot + " is now empty.")
		game_message("Unequipped.")


######################################################################################################################
#AI scripts
	#execute once per turn
class ai_Confuse:
	def __init__(self, old_ai, num_turns):
		self.old_ai = old_ai
		#number of turns remaining until AI script ends

		self.num_turns = num_turns

	def take_turn(self):
		#print("Hi.")		

		#I really hope that plugging self into this is a final fix to this stupid bug
		if self.num_turns > 0:
		#script causes AI to move to random locations, remember for later (bored/idle followers?)
			self.owner.creature.move(libtcod.random_get_int(0,-1, 1), libtcod.random_get_int(0, -1, 1))
			self.num_turns -= 1
		else:
			self.owner.ai = self.old_ai

			game_message(self.owner.display_name + " pauses and turns back to face you.")

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

#fire ranged until entering melee range. sustain fire at all times
#class ai_Ranged_Assault:
#	print("Placeholder.")

#ranged only, retreating from target while attacking
#class ai_Ranged_Fall_Back:
#	print("Placeholder.")

#run from target
#class ai_Retreat:
#	print("Placeholder.")

#cast offensive spell
#class ai_Offensive_Spell:
#	print("Placeholder.")

#cast suppressive spell
#class ai_Crowd_Control:
#	print("Placeholder.")

#follow ally, idling when too close
#class ai_ally_follow:
#	print("Placeholder.")
#	def_take_turn(self):
#		monster = self.owner

#		if libtcod.map_is_in_fov(FOV_MAP, monster.x, monster.y):
		#move towards the player if far away (out of weapon reach)
			
#			if monster.distance_to(PLAYER) >= 3:
#				self.owner.move_towards(PLAYER)
		#maybe add in a script to wander in circles around the player
#			elif:
#				return


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
def map_random_walk():
	print("Placeholder. (map gen)")
	
def map_create():
	#initialize empty map, flooded with unwalkable tiles
	new_map = [[struc_Tile(True) for y in range(0, constants.MAP_HEIGHT)]  
									for x in range (0, constants.MAP_WIDTH)]

	# generate new room
	list_of_rooms = []
	num = 0
	for num in range(constants.MAP_MAX_NUM_ROOMS):
		w = libtcod.random_get_int(0, constants.ROOM_MIN_WIDTH, 
										constants.ROOM_MAX_WIDTH)
		h = libtcod.random_get_int(0,constants.ROOM_MIN_HEIGHT, 
										constants.ROOM_MAX_HEIGHT)

		x = libtcod.random_get_int(0, 2, constants.MAP_WIDTH - w - 2)

		y = libtcod.random_get_int(0, 2, constants.MAP_HEIGHT - h - 2)



		#print(w, h, x, y)
		#create room
		new_room = obj_Room((x, y), (w, h))

		failed = False

		#check for interference (overlapping with any others)
		for other_room in list_of_rooms:
			#if new_room.intersect(other_room):
			if other_room.intersect(new_room):
				failed = True
				#print("This dumb thing failed.")
				break

		if not failed:
			#place room
			map_create_room(new_map, new_room)
			current_center = new_room.center
			center_x, center_y = new_room.center

			#put player in the first room
			if len(list_of_rooms) == 0:
				gen_player(current_center)
				print("Player (supposed to be) spawned.")

			else: 			
				##dig tunnels (from center to center?
				#prev_index = len(list_of_rooms) - 1
				#previous_center = list_of_rooms[prev_index].center
				previous_center = list_of_rooms[-1].center
				map_create_tunnels(current_center, previous_center, new_map)
				#print("idk bro")
			list_of_rooms.append(new_room)	

	#create FOV map		
	map_make_fov(new_map)
	print("map creation finished")
	#finalize
	return new_map

def map_create_room(new_map, new_room):
	for x in range(new_room.x1, new_room.x2):
		for y in range(new_room.y1, new_room.y2):
			new_map[x][y].block_path = False

def map_create_tunnels(coords1, coords2, new_map):
	#coin_flip = (libtcod.random_get_int(0, 0, 1) == 1)
	coin_flip = 0

	x1, y1 = coords1
	x2, y2 = coords2

	if coin_flip:
		for x in range(int(min(int(x1), int(x2))), int(max(int(x1), int(x2)) + 1)):
			new_map[int(x)][int(y1)].block_path = False
		for y in range(min(y1, y2), max(y1, y2) + 1):
			new_map[int(x2)][int(y)].block_path = False
	else:
		for y in range(min(int(y1), int(y2)), max(int(y1), int(y2)) +1):
			new_map[int(x1)][int(y)].block_path = False
		for x in range(min(int(x1), int(x2)), max(x1, x2) +1):

			new_map[x][y2].block_path = False

	if coin_flip:
		for x in range(min(int(x1), int(x2)), max(int(x1), int(x2)) +1):
			new_map[int(x)][int(y1)].block_path = False
		for y in range(min(int(y1), int(y2)), max(int(y1), int(y2)) +1):
			new_map[int(x1)][int(y)].block_path = False
	else: 
		for y in range(min(int(y1), int(y2)), max(int(y1), int(y2)) +1):
			new_map[int(x1)][int(y1)].block_path = False
		for x in range(min(int(x1), int(x2)), max(int(x1), int(x2)) +1):
			new_map[int(x)][int(y1)].block_path = False


def draw_map(map_to_draw):
	#camera visibility culling
	cam_x, cam_y = CAMERA.map_address
	display_map_width = constants.CAM_WIDTH / constants.CELL_WIDTH
	display_map_height = constants.CAM_HEIGHT / constants.CELL_HEIGHT

	render_w_min = int(cam_x - (display_map_width / 2))
	render_w_max = int(cam_x + (display_map_width / 2))
	render_h_min = int(cam_y - (display_map_height / 2))
	render_h_max = int(cam_y + (display_map_height / 2))

	#crudely clamp values
	if render_w_min < 0: render_w_min = 0
	if render_h_min < 0: render_h_min = 0
	if render_w_max > constants.MAP_WIDTH: render_w_max = constants.MAP_WIDTH
	if render_h_max > constants.MAP_HEIGHT: render_h_max = constants.MAP_HEIGHT

	#loop through every tile that is visible to the camera
	for x in range(render_w_min, render_w_max):
		for y in range(render_h_min, render_h_max):

			is_visible = libtcod.map_is_in_fov(FOV_MAP, x, y)

			#tiles that are currently visible
			if is_visible:
				map_to_draw[x][y].explored = True

					#draw visible wall tiles
				if map_to_draw[x][y].block_path == True:
					#draw wall, switch to actor walls instead of hardcoded ones
					draw_text(
						SURFACE_MAP, text_to_display = " # ", font = constants.FONT_RENDER_TEXT, 
						coords = (((x * constants.CELL_WIDTH) + 16), ((y * constants.CELL_HEIGHT)+ 16)), 
						text_color = constants.COLOR_L_BROWN, back_color = constants.COLOR_BLACK,
						center = True)
				else:
					#draw visible floor tiles
						draw_text(
						SURFACE_MAP, text_to_display = " . ", font = constants.FONT_RENDER_TEXT, 
						coords = (((x * constants.CELL_WIDTH) + 16), ((y * constants.CELL_HEIGHT)+ 16)), 
						text_color = constants.COLOR_WHITE, back_color = constants.COLOR_BLACK,
						center = True)	

			#tiles that have already been rendered but are no longer visible
			else:
				#draw explored but not visible wall tiles
				if map_to_draw[x][y].explored:
					if map_to_draw[x][y].block_path == True:
						#draw wall
						draw_text(
							SURFACE_MAP, text_to_display = " # ", font = constants.FONT_RENDER_TEXT, 
							coords = (((x * constants.CELL_WIDTH) + 16), ((y * constants.CELL_HEIGHT)+ 16)), 
							text_color = constants.COLOR_BROWN, back_color = constants.COLOR_BLACK,
							center = True)
					else:
						#draw explored floor but not visible wall tiles
						draw_text(
							SURFACE_MAP, text_to_display = " .  ", font = constants.FONT_RENDER_TEXT, 
							coords = (((x * constants.CELL_WIDTH) + 16), ((y * constants.CELL_HEIGHT)+ 16)), 
							text_color = constants.COLOR_GRAY, back_color = constants.COLOR_BLACK,
							center = True)

#drawing functions

def draw_game():
	global GAME
	global SURFACE_MAIN, PLAYER #, GAME.current_map

	#clear the display surface
	SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
	SURFACE_MAP.fill(constants.COLOR_BLACK)

	CAMERA.update()

	#draw the map
	draw_map(GAME.current_map)

	#draw all objects in the game
	for obj in GAME.current_objects:
		obj.draw()

								#these numbers are the starting offset, for left/top padding
	SURFACE_MAIN.blit(SURFACE_MAP, (0, 0), CAMERA.rectangle)
					

	#fix at some point idk tho
	if settings.ENABLE_DEBUG == True:
		draw_debug()

	draw_messages()

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

	start_y = ((constants.CAM_HEIGHT
				- (constants.NUM_MESSAGES * text_height)) - 20)

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
			coords = ((constants.CELL_WIDTH), (constants.CELL_HEIGHT)), 
			        text_color = constants.COLOR_BLACK, center = True)

	SURFACE_MAP.blit(new_surface, (new_x + 16, new_y + 16))

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

def helper_dice(upper_bound, bias):
	dice_roll = random.randint(1, upper_bound) + bias #simulates a dice roll from 1 to n, with a +/- bias.
	return dice_roll


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

def cast_lightning(caster, T_damage_maxrange):

	damage, m_range = T_damage_maxrange

	#damage = helper_dice(5, 6)
	#m_range = 6

	player_location = (PLAYER.x, PLAYER.y)

	# prompt player for a tile
	point_selected = menu_tile_select(coords_origin = player_location, 
		max_range = m_range, penetrate_walls = False)

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

				game_message("You smell ozone.")

				#if target.creature.name_instance:
				#	game_message(target.creature.name_instance + " takes " + str(damage) + " damage.")
		return "no-action"
	#later, render effect on each tile in sequence

def cast_fireball(caster, T_damage_radius_range):
	#definitions, change later
	damage, local_radius, max_r = T_damage_radius_range
	caster_location = (caster.x, caster.y)

	#TODO get target tile
	point_selected = menu_tile_select(coords_origin = caster_location, max_range = max_r,
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
			game_message("You smell the repugnant stench of burning flesh.", constants.COLOR_RED)

def cast_confusion(caster, effect_duration):
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

			target.ai = ai_Confuse(old_ai = oldai, num_turns = effect_duration)
			target.ai.owner = target
			game_message(target.creature.name_instance + " stumbles around in circles.", constants.COLOR_GREEN)
			#print(target.creature.name_instance + " is confused.")		
#print("Ranged attack placeholder..")
def ranged_attack(caster, ranged_weapon, target, ammo_count):
	if (ammo_count > 0 and target and ranged_weapon):
		print("Ranged attack placeholder..")


###############################################################################################################
#menus

def menu_pause():
	menu_close = False

	#move this block into the init later
	window_width = constants.CAM_WIDTH
	window_height = constants.CAM_HEIGHT
	
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

#really messy, clean up later
def menu_inventory():
	menu_close = False


	window_width = constants.CAM_WIDTH
	window_height = constants.CAM_HEIGHT

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

		#print_list = [obj.name_object for obj in PLAYER.container.inventory]
		print_list = [obj.display_name for obj in PLAYER.container.inventory]

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
						
						if settings.CLOSE_AFTER_USE == True: menu_close


					
		#draw every line in the list
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


		#render game 
		draw_game()


		#display menu
		SURFACE_MAIN.blit(local_inventory_surface, (int(menu_x), int(menu_y)))
			
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
		mapx_pixel, mapy_pixel = CAMERA.win_to_map((mouse_x, mouse_y))

		map_coord_x = int(mapx_pixel / constants.CELL_WIDTH)
		map_coord_y = int(mapy_pixel / constants.CELL_HEIGHT)

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

		#draw_game()
			SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
			SURFACE_MAP.fill(Constants.COLOR_BLACK)

			CAMERA.update()

			draw_map(GAME.current_map)

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
					#raw_tile_rect(tile_color = constants.COLOR_WHITE, coords = (map_coord_x, map_coord_y))

										#these numbers are the starting offset, for left/top padding
			SURFACE_MAIN.blit(SURFACE_MAP, (0, 0), CAMERA.rectangle)				

			if settings.ENABLE_DEBUG == True:
				draw_debug()

			draw_messages()
			#update display
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
	global FOV_CALCULATE, PLAYER
	#global FOV_MAP
	#map_make_fov(incoming_map)

	if FOV_CALCULATE:
		FOV_CALCULATE = False
		libtcod.map_compute_fov(FOV_MAP, 
								PLAYER.x, PLAYER.y, 
								constants.TORCH_RADIUS, constants.FOV_LIGHT_WALLS, 
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
##########################################################################################################
#procedural generators


#note - possibly include 'special function' in items?
#to allow additional behaviors in items such as pickaxes


#items
#use better solution later
def gen_item(coords): #random scrolls
	global GAME

	random_num = helper_dice(6, 0)
	if random_num == 1: new_item = gen_scroll_lightning(coords)
	elif random_num == 2: new_item = gen_scroll_fireball(coords)
	elif random_num == 3:  new_item = gen_scroll_confusion(coords)
	elif random_num == 4:  new_item = gen_weapon_sword(coords)
	elif random_num == 5:  new_item = gen_armor_leather(coords)
	elif random_num == 6:  new_item = gen_weapon_sword(coords)
	#elif random_num == 6:  new_item = gen_consumable_potion(coords)
	
	GAME.current_objects.insert(0, new_item)
	#GAME.current_objects.append(new_item)

def gen_scroll_lightning(coords):
	x, y = coords

	damage = helper_dice(5, 6)
	m_range = 8

	item_com = com_Item(use_function = cast_lightning, value = (damage, m_range))#not going to worry about weight or volume yet

	return_object =obj_Actor(x, y, "Scroll of Lightning", item = item_com, 
							icon = settings.scroll_icon, icon_color = constants.COLOR_WHITE)

	return return_object

def gen_scroll_fireball(coords):
	x, y = coords

	damage = helper_dice(7, 7)
	local_radius = 2
	max_r = 9

	item_com = com_Item(use_function = cast_fireball, value = (damage, local_radius, max_r))#not going to worry about weight or volume yet

	return_object =obj_Actor(x, y, "Scroll of Fireball", item = item_com, 
							icon = settings.scroll_icon, icon_color = constants.COLOR_ORANGE)

	return return_object

def gen_scroll_confusion(coords):
	x, y = coords

	effect_duration = helper_dice(3, 3)

	item_com = com_Item(use_function = cast_confusion, value = (effect_duration))#not going to worry about weight or volume yet

	return_object =obj_Actor(x, y, "Scroll of Confusion", item = item_com, 
							icon = settings.scroll_icon, icon_color = constants.COLOR_GRAY)

	return return_object

def gen_weapon_sword(coords):
	x, y = coords

	#bonus = libtcod.random_get_int(0, 1 , 2)
	equipment_com = com_Equipment(attack_bonus = 18, defense_bonus = 1, slot = "Main Hand")

	return_object = obj_Actor(x, y, "Longsword",
					icon = settings.weapon_icon, icon_color = constants.COLOR_L_BLUE,
					equipment = equipment_com)
	return return_object

def gen_weapon_pickaxe(coords):
	x, y = coords

	#bonus = libtcod.random_get_int(0, 1 , 2)
	equipment_com = com_Equipment(attack_bonus = 4, defense_bonus = 1, slot = "Main Hand")

	return_object = obj_Actor(x, y, "Pickaxer",
					icon = settings.weapon_icon, icon_color = constants.COLOR_L_BLUE,
					equipment = equipment_com)
	return return_object

def gen_armor_leather(coords):
	x, y = coords

	#bonus = libtcod.random_get_int(0, 1 , 2)
	equipment_com = com_Equipment(defense_bonus = 4, slot = "Armor")

	return_object = obj_Actor(x, y, "Leather Armor",
					icon = settings.armor_icon, icon_color = constants.COLOR_L_BLUE,
					equipment = equipment_com)
	return return_object

def gen_consumable_potion(coords):
	x, y = coords
	item_com = com_Item(value = 5)
	return_object = obj_Actor(x, y, "Bottle of Beer",
					icon = settings.potion_icon, icon_color = constants.COLOR_BROWN,
					item = item_com )

#player
def gen_player(coords):
	global PLAYER

	x, y = coords
	#create the player
	container_com = com_Container()
	creature_com = com_Creature("Bob The Guy", 
								base_attack = 5, base_defense = 2) #player's creature component name
	PLAYER = obj_Actor(x, y, "python",  
						creature = creature_com,
						container = container_com,
						icon = " Я ", icon_color = constants.COLOR_WHITE
						)
	PLAYER_SPAWNED = True

	GAME.current_objects.append(PLAYER)
	print("Player Spawn function called.")
	

#enemies
def gen_enemy(coords):
	global GAME

	random_num = helper_dice(100, 0)
	if random_num  <= 30 : new_enemy = gen_nightcrawler_greater(coords)
	else:					 new_enemy = gen_nightcrawler_lesser(coords)
	#elif random_num >= 31 : new_enemy = gen_nightcrawler_lesser(coords)

	#elif random_num == 6:  new_item = gen_consumable_potion(coords)
	
	
	GAME.current_objects.insert(-1, new_enemy)

def gen_nightcrawler_lesser(coords):
	x, y = coords

	item_com = com_Item(value = 3, use_function = cast_heal, name = "Lesser Nightcrawler carcass") 
	creature_com = com_Creature("Lesser Nightcrawler", death_function = death_monster,
								hp = 12,
								base_attack = (helper_dice(3, 5)),
								base_defense = (helper_dice(3, 3))
	) 
	ai_com = ai_Chase()
							#name of item when picked up
	ENEMY = obj_Actor(20, 19, "Lesser Nightcrawler carcass",
		creature = creature_com, ai = ai_com, item = item_com,
		icon = " ж ", icon_color = constants.COLOR_GRAY)
	return ENEMY

def gen_nightcrawler_greater(coords):
	item_com = com_Item(value = 5, use_function = cast_heal, name = "Greater Nightcrawler carcass")								#name of enemy when alive
	creature_com = com_Creature("Greater Nightcrawler", death_function = death_monster,
								hp = 15,
								base_attack = (helper_dice(4, 9)),
								base_defense = (helper_dice(4, 4))
	) 
	#the crab's creature name
	ai_com = ai_Chase()
							#name of item when picked up
	ENEMY = obj_Actor(10, 15, "Greater Nightcrawler carcass", 
		creature = creature_com, ai = ai_com, item = item_com, icon = "Ж", icon_color = constants.COLOR_GRAY)

	return ENEMY

################################################################################################################

#Main game loop, on tick
def game_main_loop():
	global TURNS_ELAPSED, PLAYER

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
			if settings.DEBUG_PRINT_TURNS == True:
				print(str(TURNS_ELAPSED) + " turns have elapsed so far")
		#render the game
		draw_game()

		#update information displays

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
					print("A useless function, for the time being.")
					#menu_tile_select()
					#cast_lightning(9)
					#cast_confusion()
					#cast_fireball(PLAYER, 2)

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
	global SURFACE_MAIN, SURFACE_MAP, GAME, CLOCK, FOV_CALCULATE
	global CAMERA, PLAYER, ENEMY, TURNS_ELAPSED, PLAYER_SPAWNED


	PLAYER_SPAWNED = False

	pygame.init()
	#print("Init began.")

	if constants.PermitKeyHolding == True:
		pygame.key.set_repeat(constants.KeyDownDelay, constants.KeyRepeatDelay)

	#create the rendered window
#	SURFACE_MAIN = pygame.display.set_mode((constants.MAP_WIDTH * constants.CELL_WIDTH, 
#											constants.MAP_HEIGHT * constants.CELL_HEIGHT))

	SURFACE_MAIN = pygame.display.set_mode((constants.CAM_WIDTH, constants.CAM_HEIGHT))

	SURFACE_MAP = pygame.Surface((constants.MAP_WIDTH * constants.CELL_WIDTH,
									constants.MAP_HEIGHT * constants.CELL_HEIGHT))	

	#side panel
	#SURFACE_SIDE = pygame.display.set_mode((constants.MAP_WIDTH * constants.CELL_WIDTH * ( 1.3), 
	#										constants.MAP_HEIGHT * constants.CELL_HEIGHT))


	CAMERA = obj_Camera()


	#create GAME object to track progress
	GAME = obj_Game()
	#print("Game Object created.")
	GAME.current_objects = []

	#print("map_create function called.")
	
	GAME.current_map = map_create()
	"""
	GAME.current_map, GAME.current_rooms = map_create()
	"""

	#print("map_create SUPPOSED to be complete")

	#player listed last to be rendered on top of enemies

	
	#GAME.current_objects.append(PLAYER)

	CLOCK = pygame.time.Clock()

	FOV_CALCULATE = True

	TURNS_ELAPSED = 0

	#map_make_fov(incoming_map)

	#GAME.current_map = map_create()
	GAME.message_history = []

if __name__ == '__main__':
	game_initialize()
	game_main_loop()	