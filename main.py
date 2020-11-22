#3rd party modules
import pygame
import tcod as libtcod
import math
#import cpickle as pickle
import pickle
import gzip
import datetime
import os.path

#necessary game files
import constants
import settings
import helpers

#for 'dice' rolls, move when that function is moved too
import random
#for generating random crap for map keys
import string

#structures
class struc_Tile:
	def __init__(self, block_path): #add more variables like blocking projectiles, blocking sight, DoT, etc.
		self.block_path = block_path
		self.explored = False
		#for things like cages, fences, other permeable barriers
		self.transparent = False


class struc_Map:
	def __init__(self, 
		player_X = 0, player_Y = 0, 
		current_key = "", 
		map_tiles = [],
		map_rooms = [],
		map_objects = [],
		x_dimension = constants.MAP_WIDTH,
		y_dimension = constants.MAP_HEIGHT):

		self.player_X = player_X
		self.player_Y = player_Y
		self.current_key = current_key
		self.map_tiles = map_tiles
		self.map_rooms = map_rooms
		self.map_objects = map_objects

#class struc_Abilities:
#	def __init__(self, celerity = ):


class struc_Direction:
	def __init__(self, x = 0, y = 0):
		self.x = x,
		self.y = y


class obj_Actor:
	def __init__(self, x, y, 
		name_object,
		creature = None, 
		ai = None, 

		container = None, 
		item = None, 
		description = "No description for this actor.", 
		state = None,

		num_turns = 0, 
		icon = "x", 
		icon_color = constants.COLOR_WHITE,
		equipment = None,
		interact_function = None,
		stairs = None,
		exitportal = None,
		static = False,		
		discovered = False,
		exit_point = False,
		doorcom = None,
		allegiance_com = None
		):

		self.x = x
		self.y = y
		self.name_object = name_object
		self.is_invulnerable = False
		self.description = description

		self.icon = icon
		self.icon_color = icon_color

		self.static = static

		self.discovered = discovered

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

		self.stairs = stairs
		if self.stairs:
			self.stairs.owner = self

		self.exitportal = exitportal
		if self.exitportal:
			self.exitportal.owner = self

		self.state = state   		#potentially legacy

		self.exit_point = exit_point
		if self.exit_point:
			self.exit_point.owner = self

		self.doorcom = doorcom
		if self.doorcom:
			self.doorcom.owner = self

		self.allegiance_com = allegiance_com
		if self.allegiance_com:
			self.allegiance_com.owner = self

		


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
		is_visible = libtcod.map_is_in_fov(FOV_MAP, self.x, self.y)

		if is_visible:
			draw_text(SURFACE_MAP, text_to_display = self.icon, font = constants.FONT_RENDER_TEXT, 
				coords = ((self.x * constants.CELL_WIDTH) + 16 , (self.y * constants.CELL_HEIGHT) + 16), 
				text_color = self.icon_color, 
				center = True)
			if self.static: 
				self.discovered = True

		elif self.static and self.discovered:
			draw_text(SURFACE_MAP, text_to_display = self.icon, font = constants.FONT_RENDER_TEXT, 
				coords = ((self.x * constants.CELL_WIDTH) + 16 , (self.y * constants.CELL_HEIGHT) + 16), 
				text_color = self.icon_color, 
				center = True)
	

	def distance_to(self, other):
		delta_x = other.x - self.x
		delta_y = other.y - self.y
		return math.sqrt(delta_x ** 2 + delta_y ** 2)

	def move_towards(self, other):
		
		delta_x = other.x - self.x
		delta_y = other.y - self.y
		distance = math.sqrt(delta_x ** 2 + delta_y ** 2)

		#delta_x = int((delta_x / distance))
		#delta_y = int((delta_y/distance))
		delta_x = int(round(delta_x / distance))
		delta_y = int(round(delta_y / distance))

		self.creature.move(delta_x, delta_y)

	def move_away(self, other):
		
		delta_x = self.x - other.x 
		delta_y = self.y - other.y 
		distance = math.sqrt(delta_x ** 2 + delta_y ** 2)

		delta_x = int(round(delta_x / distance))
		delta_y = int(round(delta_y / distance))

		self.creature.move(delta_x, delta_y)

class struc_item:
	def __init__(self):
		coords = (0, 0), 
		phys_outgoing = 0, 
		equip_slot = "", 
		item_name = "", 
		item_icon = "", 
		item_icon_color = constants.COLOR_WHITE

class struc_actor:
	def __init__(self):
		coords = (0, 0),
		actor_icon = ""
		actor_icon_color = constants.COLOR_WHITE


#massive structure that stores game state data 		
class obj_Game:
	def __init__(self):
		self.turns_elapsed = 0
		self.message_history = []
		self.first_map = True

		self.current_objects = []
		#TODO - list of AI-possessing actors to iterate over rather than every actor in the map
		self.current_map, self.current_rooms, self.next_map_x, self.next_map_y = map_create()

		self.existing_maps =  {}      #dictionary used for new map loading system, replace with tree later
		self.this_map_key = ""
		self.new_key = ""
		self.next_map_type = "dungeon"
		self.current_map_x = constants.MAP_WIDTH
		self.current_map_y = constants.MAP_HEIGHT
		
	def transition(self):
		global FOV_CALCULATE
		GAME.first_map = False	#bool to start spawning 'up' staircases, when this function is called, automatically false

		list_of_objects = map_objects_at_coords(PLAYER.x, PLAYER.y)	#get exit point the player is standing on
		for obj in list_of_objects:
			if obj.exit_point:
			#if the exit point leads to another map, load the map
				if obj.exit_point.next_map_key != "": 
					print("This exit point's key is " + obj.exit_point.next_map_key)

					(PLAYER.x, PLAYER.y, self.current_map, self.current_rooms, self.current_objects) = self.existing_maps[obj.exit_point.next_map_key]
					#get the dimensions of the next map (recursive list) and feed it to the FOV
					self.next_map_x, self.next_map_y = helper_2d_list_dimensions(self.current_map)
				
					map_make_fov(self.current_map, self.next_map_x, self.next_map_y) #, self.current_map.x_dimension, self.current_map.y_dimension)


				else:						#if the exit point has no key, create a new map and key, then load it
					##################################################################################################
					#create new key for the map to unload and new map
					GAME.current_key = helper_gen_random_key(settings.MAP_KEY_LENGTH)		
					GAME.new_key = helper_gen_random_key(settings.MAP_KEY_LENGTH)

					list_of_objects = map_objects_at_coords(PLAYER.x, PLAYER.y)
					#set the exit point key to point to the new map
					for obj in list_of_objects:	
						if obj.exit_point: 
							obj.exit_point.next_map_key = GAME.new_key
							if obj.exit_point.target_map_type: 
								self.next_map_type = obj.exit_point.target_map_type
								print(str(self.next_map_type))
							break
						print("Exit point set to the new map.")
						
					#save current map to self.existing_maps
					map_to_save = (PLAYER.x, PLAYER.y, self.current_map, self.current_rooms, self.current_objects)
					self.existing_maps[GAME.current_key] = map_to_save
					print("Saved first map at key " + GAME.current_key)


					#----------------------create new map with that key   -------------------------------------------------
					self.current_objects = [PLAYER] 
					if self.next_map_type == "dungeon": 
						self.current_map, self.current_rooms, self.next_map_x, self.next_map_y = map_create()
						map_place_objects(self.current_rooms, is_first_map = GAME.first_map)	

					if self.next_map_type == "house": 
						self.current_map, self.current_rooms = map_create_house_interior()
						#self.next_map_x, self.next_map_y = helper_2d_list_dimensions(self.current_map)

					if self.next_map_type == "cave":
						self.current_map, self.next_map_x, self.next_map_y = map_random_walk()
						#map_place_objects_dungeon()

						#self.next_map_x, self.next_map_y = helper_2d_list_dimensions(self.current_map)
						map_tryplace_player(map_x_in = self.next_map_x, map_y_in = self.next_map_y)
						gen_exit_point_stairs((PLAYER.x, PLAYER.y), downwards = False)
						
					self.next_map_x, self.next_map_y = helper_2d_list_dimensions(self.current_map)
					

		
					#set the first exit point in the new map (where the player is located) to point back to the old one
					list_of_objects = map_objects_at_coords(PLAYER.x, PLAYER.y)
					for obj in list_of_objects:	
						if obj.exit_point: 
							obj.exit_point.next_map_key = GAME.current_key
							print("Exit point set to previous map.")
					
					map_to_save = (PLAYER.x, PLAYER.y, self.current_map, self.current_rooms, self.current_objects)
			
					self.existing_maps[GAME.new_key] = map_to_save
					print("Saved second map at key " + GAME.new_key)
					print("Number of maps saved is " + str(len(GAME.existing_maps)))
				
		map_make_fov(self.current_map, fov_x = self.next_map_x, fov_y = self.next_map_y)
		FOV_CALCULATE = True

#this is a rectangle that lives on the map
class obj_Room:
	def __init__(self, coords, size): #coords are upper left corner location 
		self.x1, self.y1 = coords
		self.w, self.h = size

		self.x2 = self.x1 + self.w
		self.y2 = self.y1 + self.h

	@property
	def center(self):
		center_x = int(((self.x1 + self.x2) // 2))
		center_y = int(((self.y1 + self.y2) // 2))

		return (center_x, center_y)

	def intersect(self, other):
		#return true if another obj intersects with this one
		objects_intersect = (self.x1 <= other.x2 and self.x2 >= other.x1 and
                             self.y1 <= other.y2 and self.y2 >= other.y1)

		return objects_intersect

#object that is spawned in towns
class obj_Building:
	def __init__(self, coords, size): #coords are upper left corner location 
		self.x1, self.y1 = coords
		self.w, self.h = size

		self.x2 = self.x1 + self.w
		self.y2 = self.y1 + self.h

	def intersect(self, other):
		#return true if another obj intersects with this one
		objects_intersect = (self.x1 <= other.x2 and self.x2 >= other.x1 and
                             self.y1 <= other.y2 and self.y2 >= other.y1)

		#return objects_intersect
		return objects_intersect

	#the center of each building
	@property
	def center(self):
		center_x = ((self.x1 + self.x2) // 2)
		center_y = ((self.y1 + self.y2) // 2)

		return (center_x, center_y)

#the player's viewport - level is spatially mapped to it
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
		hp = 10, 
		base_damage = 2, base_armor_phys = 0, 
		death_function = None, money = 0,

		damage_phys_base = 1,
		resist_phys_base = 1,
		base_dodge_chance = 10,
		base_hit_chance = 10,

		resist_fire_base = 1,

		gender = 0, base_xp = 1, xp_on_death = 10):
		self.name_instance = name_instance
		self.max_hp = hp
		self.current_hp = hp
		self.money = money
		self.death_function = death_function
		self.gender = gender
		self.base_xp = base_xp
		self.xp_on_death = xp_on_death
		self.current_xp = base_xp

		#combat stats
		self.damage_phys_base = damage_phys_base
		self.resist_phys_base = resist_phys_base

		self.dodge_chance_base = base_dodge_chance
		self.hit_chance_base = base_hit_chance

		self.resist_fire_base = resist_fire_base

		#base_dodge_chance
		#base_hit_chance
		#bonus_defense
		#bonus_accuracy
		#base_critical_chance
		#bonus_critical

		#add new damage types and stuff later
	def take_damage(self, damage_received, attacker):
		self.current_hp -= damage_received

		#possibly change later to include the name of the attacker
		if self.current_hp <= 0:
			if self.death_function is not None:
				self.death_function(self.owner)
				if attacker == PLAYER:
					PLAYER.creature.current_xp += self.xp_on_death

	def move(self, dx, dy):
		new_x = self.owner.x
		new_y = self.owner.y

		next_x = self.owner.x + dx
		next_y = self.owner.y + dy

		#check if creature is trying to move off the map
		if next_x >= 0 and next_x <= (GAME.current_map_x - 1):
			if next_y >= 0 and next_y < (GAME.current_map_y - 1):
				tile_is_wall = (GAME.current_map[self.owner.x + dx][self.owner.y + dy].block_path == True)
				target = map_check_for_creatures(self.owner.x + dx, self.owner.y + dy, self.owner)

				if target:
					print("Attacker has a target.")
					#prompt to check for hostility
					if self.owner.allegiance_com and target.allegiance_com:
						print("Attacker and target have allegiance components.")
						#check if attacker's category equals the target's category - do not attack
						if str(self.owner.allegiance_com.category) == str(target.allegiance_com.category):
							print("Attacker and target have the same category. No attacking.")
							#return

						print("target allegiance category = " + str(target.allegiance_com.category))
						print("self hostile list = " + str(self.owner.allegiance_com.hostile_list))

						#check if target's category is in the list of hostile categories, if so, attack
						for i in self.owner.allegiance_com.hostile_list:
							if str(target.allegiance_com.category) == self.owner.allegiance_com.hostile_list:
								self.attack(target)
						else: 
							print("Target is not hostile, not attacking.")
							#a hacky hotfix for the bug above
							#the list search isn't working, because of course it isn't
							if self.owner == PLAYER:
								self.attack(target)
					else:
						print("One or both actors does not have an allegiance component.")

				if not tile_is_wall and target is None:
					self.owner.x += dx
					self.owner.y += dy

					#if there are items at the player's tile, print them to the message log
					#collapse this into a function later?
					if self.owner == PLAYER:

						objects_at_player_tile = map_objects_at_coords(self.owner.x, self.owner.y, exclude_player = True)

						if len(objects_at_player_tile) == 1:
							for obj in objects_at_player_tile:
									if obj.item:
										game_message("You see here " + obj.item.name)
									if obj.equipment:
										game_message("You see here " + obj.equipment.name)

						elif len(objects_at_player_tile) > 1:
							game_message("You see here multiple objects.")

	def attack(self, target):
		damage_dealt = self.damage_physical - target.creature.resist_physical
		print(damage_dealt)

		if (damage_dealt < 0):
			game_message(self.name_instance + " fails to do any damage " + target.creature.name_instance + " at all.")

		else:
			game_message((self.name_instance + " attacks " + target.creature.name_instance + " and does " + str(damage_dealt) + " damage."), constants.COLOR_WHITE)
			target.creature.take_damage(damage_dealt, attacker = self.owner)

	def heal(self, value):
		self.current_hp += value
		#include at a later date, the possibility of overhealing
		if self.current_hp > self.max_hp:
			self.current_hp = self.max_hp

	@property
	def accuracy(self):
		accuracy = self.base_hit_chance
		object_bonuses = []
		if self.owner.container:
			object_bonuses = [obj.equipment.accuracy_bonus 
			for obj in self.owner.container.equipped_items]

		for bonus in object_bonuses:
			if bonus:
				dodge += bonus

		return dodge

	@property
	def dodge(self):
		dodge = self.base_dodge_chance
		object_bonuses = []
		if self.owner.container:
			object_bonuses = [obj.equipment.dodge_bonus 
			for obj in self.owner.container.equipped_items]

		for bonus in object_bonuses:
			if bonus:
				dodge += bonus

		return dodge

	@property
	def damage_physical(self):
		physical_damage = self.damage_phys_base
		object_bonuses = []

		if self.owner.container:
			object_bonuses = [obj.equipment.damage_phys_bonus 
			for obj in self.owner.container.equipped_items]

		for damage_phys_bonus in object_bonuses:
			if damage_phys_bonus:
				physical_damage += damage_phys_bonus

		return physical_damage

	@property
	def resist_physical(self):
		physical_resistance = self.resist_phys_base

		object_bonuses = []
		if self.owner.container:
			object_bonuses = [obj.equipment.resist_phys_bonus
								for obj in self.owner.container.equipped_items]

		for resist_phys_base in object_bonuses:
			if resist_phys_base:
				physical_resistance += resist_phys_base

		return physical_resistance


	@property 
	def resist_fire(self):
		fire_resistance = self.resist_fire_base

		object_bonuses = []
		if self.owner.container:
			object_bonuses = [obj.equipment.resist_fire_bonus
								for obj in self.owner.container.equipped_items]
		for resist_fire_base in object_bonuses:
			if resist_fire_base:
				fire_resistance += resist_fire_base
		return fire_resistance

class com_Container:
	def __init__(self, volume = 10.0, max_volume = 10.0,  inventory = None):
		self.inventory = inventory
		self.max_volume = volume
		if inventory: self.inventory = inventory
		else: self.inventory = []
		
	@property 
	def volume(self):
		return 0.0

	@property
	def equipped_items(self):
		list_of_equipped_items = [obj for obj in self.inventory 
									if obj.equipment and obj.equipment.equipped ]
		return list_of_equipped_items


class com_Item:
	def __init__(self, weight = 0.0, volume = 0.0, name = "foo", category = "misc", 
		use_function = None, value = None, slot = None):
		self.weight = weight
		self.volume = volume
		self.name = name
		self.value = value
		self.use_function = use_function

		#pick up this item
	def pick_up(self, actor):
		if actor.container:

			if self.owner.equipment: item_name = self.owner.equipment.name
			elif self.name: item_name = self.owner.item.name
			elif self.name_object: item_name = self.name_object
			game_message(actor.creature.name + " picked up " + item_name + ".")

			actor.container.inventory.append(self.owner)
			GAME.current_objects.remove(self.owner)
				
			self.current_container = actor.container
		
	def drop(self, new_x, new_y):
		GAME.current_objects.append(self.owner)
		self.current_container.inventory.remove(self.owner)
		#place object at the coords at which it was dropped
		self.owner.x = new_x
		self.owner.y = new_y

		if self.owner.equipment: item_name = self.owner.equipment.name
		elif self.name: item_name = self.owner.item.name
		elif self.name_object: item_name = self.name_object
		game_message(self.current_container.owner.creature.name + " drops " + item_name + ".")

	def use(self):
		if self.owner.equipment:
			self.owner.equipment.toggle_equip()
			return
		else: 
			print("This item cannot be equipped.")
		
		if self.use_function:
			result = self.use_function(self.current_container.owner, self.value)
		
			if result is not None:
				print("use_function failed")
			else:
				self.current_container.inventory.remove(self.owner)

#add more bonuses later
class com_Equipment:
	def __init__(self, 
		damage_phys_bonus = 0, resist_phys_bonus = 0,
		damage_fire_bonus = 0, resist_fire_bonus = 0, 
		slot = None, name = None):
		self.damage_phys_bonus = damage_phys_bonus
		self.resist_phys_bonus = resist_phys_bonus

		self.damage_fire_bonus = damage_fire_bonus
		self.resist_fire_bonus = resist_fire_bonus

		self.name = name
		self.slot = slot
		self.equipped = False

	def toggle_equip(self):
		if self.equipped:
			self.unequip()

		else:
			self.equip()

	def equip(self):
		all_equipped_items = self.owner.item.current_container.equipped_items
		
		for item in all_equipped_items:
			if item.equipment.slot and (item.equipment.slot == self.slot):
				game_message(self.slot + " is already occupied.", constants.COLOR_RED)
					#ynaq prompt to replace?
				return
		self.equipped = True
		game_message("Equipped in " + (str(self.slot)) + ".")

	def unequip(self):
		self.equipped = False

#LEGACY - remove later
class com_Stairs:
	def __init__(self, downwards = True):
		self.downwards = downwards
		static = True
	
	#include parameter for prompting the player before moving?
	

	def use(self):
		print("Stairs.use called")
		if self.downwards:
			GAME.transition_next()
			game_message("You descend the staircase.")

		else:
			GAME.transition_previous()
			game_message("You ascend the staircase.")

#LEGACY - remove later
class com_Exit_Portal:			
	def __init__(self):
		self.open_icon = settings.portal_icon
		self.closed_icon = settings.door_closed_icon
		self.color = constants.COLOR_YINZER

	def update(self):
		#flag initialization

		found_mcguffin = False
		#check conditions
		portal_open = self.owner.state == "OPEN"
		for obj in PLAYER.container.inventory:
			if obj.name_object == "The McGuffin":	#if the player has the mcguffin 
				found_mcguffin = True 	#shouldn't this be under the player? idk

		if found_mcguffin and not portal_open: #if lamp found but portal not yet open
			self.owner.state = "OPEN"
			self.owner.icon = settings.door_open_icon
			print("Portal open")

		if not found_mcguffin and portal_open: #if lamp found but portal not yet open
			self.owner.state = "CLOSED"
			self.owner.icon = settings.door_closed_icon
			print("Portal closed")

	def use(self):
		print("Using portal or something idk")
		#if self.owner.state == "OPEN":
		game_message("You won!")
		PLAYER.state = "STATUS_WIN"
		SURFACE_MAIN.fill(constants.COLOR_BLACK)
		x = (constants.CAM_WIDTH/2)
		y = (constants.CAM_HEIGHT/2)

		screen_open = True

		while screen_open:
			if settings.Mod9: 
				draw_text(SURFACE_MAIN, "I owe yinz an Arn Ciddy and some pierogies. Good job.",
						constants.FONT_TITLE_SCREEN1,
						(x, y),
						constants.COLOR_YINZER, center = True)

				draw_text(SURFACE_MAIN, "Press F to return to the main menu.",
							constants.FONT_TITLE_SCREEN2,
							(x, y + 75),
							constants.COLOR_YINZER, center = True)

			else: 
				draw_text(SURFACE_MAIN, "You won. Congratulations.",
						constants.FONT_TITLE_SCREEN1,
						(x, y),
						constants.COLOR_WHITE, center = True)

				draw_text(SURFACE_MAIN, "Press F to return to the main menu.",
						constants.FONT_TITLE_SCREEN2,
						(x, y + 75),
						constants.COLOR_WHITE, center = True)


			for event in pygame.event.get():
					if event.type == pygame.KEYDOWN:
						screen_open = False


			pygame.display.update()
			pygame.time.wait(1000)

			if settings.GEN_LEGACY_FILE:
				filename = (PLAYER.creature.name_instance +"_winner" + "." 
							+ datetime.date.today().strftime("%Y%B%d") #get the date 
							+ ".txt") 	

			if os.path.isfile(filename):
				#legacy file
				legacy_file = open(filename, 'a+')

				for message, color in GAME.message_history:
					legacy_file.write(message + "\n")
		pygame.display.update()

class com_Exit_Point:
	def __init__(self, require_input, next_map_key = "", static = True, target_map_type = "dungeon"):
		self.require_input = require_input,
		self.next_map_key = next_map_key
		self.static = True
		self.target_map_type = target_map_type

	def use(self):
		GAME.transition()

#physical door that can be opened or closed
class com_Door:
	def __init__(self, is_destructable = True, 
		is_locked = False, default_locked = False,
		is_closed = False, default_closed = False,
		door_interaction_message = ""):

		self.is_destructable = is_destructable,
		self.default_locked = default_locked,
		self.default_closed = default_closed,

		self.is_locked = default_locked,
		self.is_closed = default_closed,
		self.door_interaction_message = door_interaction_message

	def interact(self):
		print("com_Door.interact() called")

		#if the door is closed and unlocked, open it
		if self.is_closed == False:
			if self.is_locked == False:
				self.is_closed = False
				self.door_interaction_message = "You open the door."
				self.icon = settings.door_open_icon
			else:
				self.door_interaction_message = "You try to turn the knob - it is still locked."

		else: #self.is_closed == True:
			self.is_closed == False
			self.door_interaction_message = "You close the door."
			self.icon = settings.door_closed_icon
		#if the door is open, close it
		game_message(self.door_interaction_message)

	def lock_unlock():
		#add a line or two to check if the door is closed first. you can't lock and open door
		if is_locked:
			is_locked = False
			door_interaction_message = "You unlock the door."
		else:
			is_locked = True
			door_interaction_message = "You lock the door."

		game_message(door_interaction_message, msg_color = constants.COLOR_WHITE)

	print("Placeholder")

class com_Allegiance:
	def __init__(self, category = "undefined", protect_list = "", hostile_list = {""}, docile = True):
		#list of targets whose attackers the npc will attack
		self.category = category,
		self.protect_list = protect_list,
		#list of categories which the npc will not
		self.hostile_list = hostile_list,
		#npc has not yet been provoked into attacking
		self.docile = docile



######################################################################################################################
#AI scripts
	#execute once per turn
class ai_Confuse:
	def __init__(self, old_ai, num_turns = 5):
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
	#add target selection and prioritizaiton later
	def take_turn(self):
		monster = self.owner
		if libtcod.map_is_in_fov(FOV_MAP, monster.x, monster.y):
			#move towards the player if far away (out of weapon reach)		
			# move towards the player if far away
			if monster.distance_to(PLAYER) >= 2:
				self.owner.move_towards(PLAYER)
			# if close enough, attack player
			elif PLAYER.creature.current_hp > 0:
				monster.creature.attack(PLAYER) # monster.creature.power)

class ai_Flee:
	def take_turn(self):
		monster = self.owner
		if libtcod.map_is_in_fov(FOV_MAP, monster.x, monster.y):
			self.owner.move_away(PLAYER)

class ai_Townfolk_Wander:
	def take_turn(self):
		#print("Townfolk taking turn")
		self.owner.creature.move(libtcod.random_get_int(0,-1, 1), libtcod.random_get_int(0, -1, 1))
		
#fire ranged until entering melee range. sustain fire at all times
#class ai_Ranged_Assault:
#	print("Placeholder.")

#ranged only, retreating from target while attacking
#class ai_Ranged_Fall_Back:
#	print("Placeholder.")

#cast offensive spell
#class ai_Offensive_Spell:
#	print("Placeholder.")

#cast suppressive spell
#class ai_Crowd_Control:
#	print("Placeholder.")

class com_AI:
	def take_turn(self):
		self.owner.creature.move(libtcod.random_get_int(0,-1, 1), libtcod.random_get_int(0, -1, 1))

#follow ally, idling when too close. edit later to include attacking enemies
class ai_Ally_Follow:
	print("Placeholder.")
	def take_turn(self):
		monster = self.owner
		if libtcod.map_is_in_fov(FOV_MAP, monster.x, monster.y):

			if monster.distance_to(PLAYER) >= 5:
				self.owner.move_towards(PLAYER)
			else:
				self.owner.creature.move(libtcod.random_get_int(0,-1, 1), libtcod.random_get_int(0, -1, 1))
			#move towards the player if far away (out of weapon reach)

class ai_Static:
	def take_turn(self):
		return

class ai_Player:
	def take_turn(self):
		return

#engage with AKC at range then attack
class ai_Dragon:
	def take_turn(self):
		monster = self.owner
		target_coords = PLAYER.x, PLAYER.y
		if libtcod.map_is_in_fov(FOV_MAP, monster.x, monster.y):
			#move towards the player if far away (out of spell reach)		
			# move towards the player if far away
			if monster.distance_to(PLAYER) >= 8:
				self.owner.move_towards(PLAYER)
			#if target is alive, attack
			elif PLAYER.creature.current_hp > 0:
				#cast fireball
				if monster.distance_to(PLAYER) > 3:
					cast_fireball(caster = self.owner, T_damage_radius_range = (13, 3, 8))
					#(PLAYER.x, PLAYER.y)

				else: # if within blast radius, engage in melee
					if monster.distance_to(PLAYER) < 2:
						monster.creature.attack(PLAYER)

					if monster.distance_to(PLAYER) < 3:
						self.owner.move_towards(PLAYER)	

def death_monster(monster):
	if monster.is_invulnerable != True:
		#on death, most monsters stop moving
		#print (monster.creature.name_instance + " is killed!")
		
		game_message(monster.creature.name_instance + " is dead!", constants.COLOR_GRAY)
		monster.creature = None
		monster.ai = None
		monster.icon = settings.consumable_icon
		#determine what to leave behind
	else:
		#print("Nice try. " + monster.creature.name_instance + " is invulnerable.")
		game_message("Nice try. " + monster.creature.name_instance + " is invulnerable.", constants.COLOR_GRAY)

def death_player(player):
	player.state = "STATUS_DEAD"
	SURFACE_MAIN.fill(constants.COLOR_BLACK)
	x = (constants.CAM_WIDTH/2)
	y = (constants.CAM_HEIGHT/2)

	screen_open = True

	while screen_open:
		if settings.Mod9: 
			draw_text(SURFACE_MAIN, "Yinz done goofed. Go back to Cleveland, ya jagoff",
				constants.FONT_TITLE_SCREEN1,
				(x, y),
				constants.COLOR_YINZER, center = True)

			draw_text(SURFACE_MAIN, "Press F to return to the main menu.",
					constants.FONT_TITLE_SCREEN2,
					(x, y + 75),
					constants.COLOR_YINZER, center = True)


		else: 
			draw_text(SURFACE_MAIN, "You have died.",
				constants.FONT_TITLE_SCREEN1,
				(x, y),
				constants.COLOR_WHITE, center = True)

			draw_text(SURFACE_MAIN, "Press F to return to the main menu.",
				constants.FONT_TITLE_SCREEN2,
				(x, y + 75),
				constants.COLOR_WHITE, center = True)


		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				screen_open = False


		pygame.display.update()
	pygame.time.wait(1000)

	if settings.GEN_LEGACY_FILE:
		filename = (PLAYER.creature.name_instance +"_legacy" + "." 
					+ datetime.date.today().strftime("%Y%B%d") #get the date 
					+ ".txt") 	

		#legacy file
		legacy_file = open(filename, 'a+')

		for message, color in GAME.message_history:
			legacy_file.write(message + "\n")

###############################################################################################################
#map functions
def map_random_walk(dungeon_x = constants.MAP_WIDTH, dungeon_y = constants.MAP_HEIGHT, walk_nodes = 6, steps_per_node = 1000):
	#initialize empty map, flooded with unwalkable tiles
	new_map = [[struc_Tile(True) for y in range(1, dungeon_x)]  
									for x in range (1, dungeon_y)]

	x_l_bound = int(dungeon_x * .35)
	x_u_bound = int(dungeon_x * .55)
	y_l_bound = int(dungeon_y * .45)
	y_u_bound = int(dungeon_y * .55)

	first_node = True

	#random walk that propagates out from assigned nodes
	for n in range(walk_nodes):

		#if first_node:
		#point_x = int(dungeon_x/2)
		#point_y = int(dungeon_y/2)
		#	first_node = False
			#print("First node.")
	#	else:
		point_x = random.randint(x_l_bound, x_u_bound)
		point_y = random.randint(y_l_bound, y_u_bound)
		print("Node #" + str(n))

		for i in range(steps_per_node):
			r = helper_dice(4, -1)

			if r == 0: 
				point_x += 1
			if r == 1: 
				point_x -= 1
			if r == 2: 
				point_y += 1
			if r == 3: 
				point_y -= 1

			#print("drawing tile at " + str(point_x) + "," + str(point_y))
			if point_x > 2 and point_x < (dungeon_x -2):
				if point_y > 2 and point_y < (dungeon_y - 2):
					new_map[point_x][point_y].block_path = False
		print("Random walk from node " + str(n) + " completed.")

	map_make_fov(new_map, fov_x = dungeon_x -1, fov_y = dungeon_y -1)

	map_tryplace_stairs(map_in = new_map, map_x_in = dungeon_x -1, map_y_in = dungeon_y -1)
	print("map creation finished")
	return (new_map, dungeon_x, dungeon_y)


def map_create(dungeon_x = constants.MAP_WIDTH, dungeon_y = constants.MAP_HEIGHT, total_rooms = constants.MAP_MAX_NUM_ROOMS):

	#initialize empty map, flooded with unwalkable tiles
	new_map = [[struc_Tile(True) for y in range(0, dungeon_x)]  
									for x in range (0, dungeon_y)]

	# generate new room
	list_of_rooms = []
	num = 0
	for num in range(total_rooms):
		w = libtcod.random_get_int(0, constants.ROOM_MIN_WIDTH,  
										constants.ROOM_MAX_WIDTH)
		h = libtcod.random_get_int(0,constants.ROOM_MIN_HEIGHT, 
										constants.ROOM_MAX_HEIGHT)

		x = libtcod.random_get_int(0, 2, dungeon_x - w - 2)

		y = libtcod.random_get_int(0, 2, dungeon_y - h - 2)

		#create room
		new_room = obj_Room((x, y), (w, h))
		failed = False

		#check for interference (overlapping with any others)
		for other_room in list_of_rooms:
			if other_room.intersect(new_room):
				failed = True
				break

		if not failed:
			#place room
			map_create_room(new_map, new_room)
			current_center = new_room.center
			center_x, center_y = new_room.center

			#put player in the first room
			if len(list_of_rooms) != 0:
				previous_center = list_of_rooms[-1].center
				##dig tunnels
				map_create_tunnels(current_center, previous_center, new_map)

			list_of_rooms.append(new_room)	

	#create FOV map		
	map_make_fov(new_map)
	print("map creation finished")
	return (new_map, list_of_rooms, dungeon_x, dungeon_y)

def map_create_town():
	#initialize empty map, flooded with empty tiles
	new_map = [[struc_Tile(False) for y in range(0, constants.MAP_HEIGHT)]  
									for x in range (0, constants.MAP_WIDTH)]

	#create borders of town
	for i in range(0, constants.MAP_WIDTH):
		new_map[i][0].block_path = True
		new_map[i][constants.MAP_HEIGHT -1].block_path = True

	for i in range(0, constants.MAP_HEIGHT):
		new_map[0][i].block_path = True
		new_map[constants.MAP_WIDTH -1][i].block_path = True

	
	#for i in range(new_map[0]):
	#	struc_Tile(False)

	#function to add borders to town

	# generate new builds
	list_of_buildings = []
	num = 0
	#create random buildings
	for num in range(constants.MAP_MAX_NUM_ROOMS):
		w = libtcod.random_get_int(0, constants.KAZANY_BUILDING_MIN_WIDTH,  
										constants.KAZANY_BUILDING_MAX_WIDTH)
		h = libtcod.random_get_int(0,constants.KAZANY_BUILDING_MIN_HEIGHT, 
										constants.KAZANY_BUILDING_MAX_HEIGHT)

		x = libtcod.random_get_int(0, 2, constants.MAP_WIDTH - w - 2)

		y = libtcod.random_get_int(0, 2, constants.MAP_HEIGHT - h - 2)

		#create room
		new_building = obj_Building((x, y), (w, h))

		failed = False

		#check for interference (overlapping with any others)
		for other_building in list_of_buildings:
			if other_building.intersect(new_building):
				failed = True
				break

		if not failed:
			#place room
			map_create_building(new_map, new_building)
			current_center = new_building.center
			center_x, center_y = new_building.center

			#put player in the first room
			if len(list_of_buildings) != 0:
				previous_center = list_of_buildings[-1].center
				##dig tunnels
				#map_create_tunnels(current_center, previous_center, new_map)

			list_of_buildings.append(new_building)



	#create FOV map		
	map_make_fov(new_map)
	print("map creation finished")
	return (new_map, list_of_buildings)

def map_create_house_interior(house_x = constants.HOUSE_INTERIOR_MIN_WIDTH, house_y = constants.HOUSE_INTERIOR_MIN_HEIGHT):
	#initialize empty map, flooded with empty tiles

	new_map = [[struc_Tile(False) for y in range(0, house_y)]  
									for x in range (0, house_x)]
	#top/bottom
	for i in range(0, house_x):
		new_map[i][1].block_path = True
		new_map[i][house_y - 1].block_path = True
	#left/right
	for i in range(0, house_y - 1):
		new_map[0][i].block_path = True
		new_map[house_x -1][i].block_path = True

	#putting this here so the flippin interpreter doesn't whine at me about stuff idk man
	list_of_buildings = []

	map_place_door_on_walls(x = house_x, y = house_y, map_in = new_map)

	#create FOV map		
	map_make_fov(new_map, fov_x = house_x, fov_y = house_x)
	print("map creation finished")
	return (new_map, list_of_buildings)

def map_tryplace_player(map_x_in = constants.MAP_WIDTH, map_y_in = constants.MAP_HEIGHT):
	for i in range(1, 2000):
		
		x = random.randint(1, map_x_in - 2)
		y = random.randint(1, map_y_in - 2)
		print("Attempt #" + str(i) + " to to place player at " + str(x) + "," + str(y))

		if GAME.current_map[x][y].block_path == False:
			PLAYER.x, PLAYER.y = x, y
			 		
			break	

def map_tryplace_stairs(map_in, map_x_in = constants.MAP_WIDTH, map_y_in = constants.MAP_HEIGHT, in_key = None): #add key or something later idk tho
	#I don't even know what is real anymore

	for i in range (0, 1000):
		x = random.randint(1, map_x_in - 2)
		y = random.randint(1, map_y_in - 2)
		#check if there is already an exit point at the given location
		#map_objects_at_coords
		if map_in[x][y].block_path == False: 
			gen_exit_point_stairs((x, y), downwards = True)
			print("Stairs successfully placed after " + str(i) + " tries.")
			break

def map_place_objects(room_list, is_first_map = None):
	for room in room_list:
		first_room = (room ==  room_list[0])
		second_room = (room ==  room_list[1])
		last_room = (room == room_list[-1])

		#put the player in the first room
		if first_room: PLAYER.x, PLAYER.y = room.center

		if first_room: 
			if is_first_map == False:
				gen_exit_point_stairs(room.center, downwards = False)	#create stairs back up to last map
			else:
				gen_weapon_sword(room.center)
	
		if last_room:
			gen_exit_point_stairs(room.center, downwards = True)
			
		#generated items and enemies
		x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1) #only add +1/-1 later if issues arise
		y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1) #ditto
		gen_item((x,y))
		
		x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1) #only add +1/-1 later if issues arise
		y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1) #ditto
		gen_creature((x,y))

def map_place_objects_town(building_list, is_first_map = False):
	PLAYER.x, PLAYER.y = (3, 3)

	map_tryplace_player()

	for i in range (0, 10):
		x = libtcod.random_get_int(0, 1, constants.MAP_WIDTH - 1)
		y = libtcod.random_get_int(0, 1, constants.MAP_HEIGHT - 1)
		if GAME.current_map[x][y].block_path == False:
			weapon = gen_weapon_sword((x, y))
			armor = gen_armor_leather((x, y))
			GAME.current_objects.insert(0, weapon)
			GAME.current_objects.insert(0, armor)

			print("Player's kit spawned after " + str(i) + " tries.")
			break
			
	#gen_exit_point_door((5, 4), target_type = "dungeon")
	gen_exit_point_door((5, 4))
	gen_exit_point_door((8, 10))


	i = 0
	successful_townsfolk_spawns = 0
	for i in range(0, 100):
		x = libtcod.random_get_int(0, 1, constants.MAP_WIDTH - 1)
		y = libtcod.random_get_int(0, 1, constants.MAP_HEIGHT - 1)

		if GAME.current_map[x][y].block_path == False:
			gen_town_folk((x, y))

			successful_townsfolk_spawns += 1
	print(str(successful_townsfolk_spawns) + " townsfolk successfully spawned.")

	i = 0
	successful_tree_spawns = 0
	for i in range(0, 120):
		x = libtcod.random_get_int(0, 1, constants.MAP_WIDTH - 1)
		y = libtcod.random_get_int(0, 1, constants.MAP_HEIGHT - 1)

		if GAME.current_map[x][y].block_path == False:
			gen_tree((x, y))

			successful_tree_spawns += 1
	print(str(successful_tree_spawns) + " trees successfully spawned.")

def map_place_objects_dungeon():
	#map_tryplace_stairs()
	print("Placeholder to place stuff in the dungeon.")
	
#place a door on the walls of a building interior
def map_place_door_on_walls(x = 0, y = 0, map_in = None):
	side = helper_dice(4, 0)
	if side == 1: #top?
		door_x_pos = round((0 + x) /2)
		door_y_pos = 1
	if side == 2: #bottom?
		door_x_pos = round((0 + x) / 2)
		door_y_pos = y -1 
	if side == 3: #left?
		door_y_pos = round((0 + y) /2)
		door_x_pos = 1
	if side == 4: #right?
		door_y_pos = round((0 + y) / 2)
		door_x_pos = x -1 

	map_in[door_x_pos][door_y_pos].block_path = False
	gen_exit_point_door(coords = (door_x_pos, door_y_pos), target_key = GAME.current_key)
	PLAYER.x, PLAYER.y = (door_x_pos, door_y_pos)

def map_create_overworld():
	print("Placeholder")

def map_create_room(new_map, new_room):
	for x in range(new_room.x1, new_room.x2):
		for y in range(new_room.y1, new_room.y2):
			new_map[x][y].block_path = False

def map_create_building(new_map, new_building, has_door = True):
	for x in range(new_building.x1, new_building.x2):
		for y in range(new_building.y1, new_building.y2):
			new_map[x][y].block_path = True

	if has_door:
		gen_building_door(new_map, new_building)

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

def map_make_fov(incoming_map, fov_x = constants.MAP_WIDTH, fov_y = constants.MAP_HEIGHT):
	global FOV_MAP
	FOV_MAP = libtcod.map.Map(fov_x, fov_y)

	for y in range(int(fov_y)):
		for x in range(int(fov_x)):
			libtcod.map_set_properties(FOV_MAP, x, y, 
				not incoming_map[int(x)][int(y)].block_path, not incoming_map[int(x)][int(y)].block_path)

def map_calculate_fov():
	global FOV_CALCULATE, PLAYER
	if FOV_CALCULATE:
		FOV_CALCULATE = False
		libtcod.map_compute_fov(FOV_MAP, 
								PLAYER.x, PLAYER.y, 
								constants.TORCH_RADIUS, constants.FOV_LIGHT_WALLS, 
								constants.FOV_ALGO)

def map_objects_at_coords(coords_x, coords_y, exclude_player = False):
	object_options = [obj for obj in GAME.current_objects 
	if obj.x == coords_x and obj.y == coords_y]

	if exclude_player:
		for obj in object_options:
			if obj == PLAYER:
				object_options.remove(obj)

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

#drawing functions
def draw_game():
	global GAME
	global SURFACE_MAIN, PLAYER, SURFACE_WINDOW, SURFACE_BOTTOM_PANEL

	#clear the display surface
	SURFACE_WINDOW.fill(constants.COLOR_D_GRAY)
	SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
	SURFACE_MAP.fill(constants.COLOR_BLACK)
	SURFACE_BOTTOM_PANEL.fill(constants.COLOR_BLACK)

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
	draw_stat_panel()

def draw_text(display_surface, text_to_display, font, coords, text_color, back_color = None, center = False):
    # get both the surface and rectangle of the desired message
    text_surf, text_rect = helper_text_objects(text_to_display, font, text_color, back_color)
    
    if not center:
    	text_rect.topleft = coords

    else:
    	text_rect.center = coords

    # draw the text onto the display surface.
    display_surface.blit(text_surf, text_rect)
   
def draw_debug():
	if settings.DISPLAY_FPS :
	    draw_text(SURFACE_MAIN,
              "fps: " + str(int(CLOCK.get_fps())),
              constants.FONT_DEBUG_MESSAGE,
              (0, 0),
              constants.COLOR_WHITE,
              constants.COLOR_BLACK)

def draw_stat_panel():
	global SURFACE_BOTTOM_PANEL, PLAYER
	start_y = (int((constants.CAM_HEIGHT + 20) * .85))

	stats = ("Health = " + str(PLAYER.creature.current_hp) + "/" + str(PLAYER.creature.max_hp) + 
			", Damage / hit = " + str(PLAYER.creature.damage_physical) +
			", vs Physical = " + str(PLAYER.creature.resist_physical) +
			", vs Fire = " + str(PLAYER.creature.resist_fire) + 
			", XP/LVL = 1/" + str(PLAYER.creature.current_xp))
	text_height = 0

	draw_text(SURFACE_BOTTOM_PANEL, 
		stats, 
		constants.FONT_STATS, 
		(20, start_y + (text_height)), 
		constants.COLOR_WHITE, constants.COLOR_BLACK)

def draw_messages():
	#include 'timer' for clearing message log, later

	#add last 4 messages to the queue
	if len(GAME.message_history) <= constants.NUM_MESSAGES:
		to_draw = GAME.message_history
	else:
		to_draw = GAME.message_history[-(constants.NUM_MESSAGES):]

	text_height = helper_text_height(constants.FONT_MESSAGE_TEXT)

	start_y = ((constants.CAM_HEIGHT
				- (constants.NUM_MESSAGES * text_height)) - 20) * .85

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
	if tile_alpha: local_alpha = tile_alpha
	else: local_alpha = 150

	new_x = x * constants.CELL_WIDTH - 16
	new_y = y * constants.CELL_HEIGHT  -16

	new_surface = pygame.Surface((constants.CELL_WIDTH, constants.CELL_HEIGHT))

	new_surface.fill((tile_color))

	new_surface.set_alpha(local_alpha)

	if mark:
		#move the centering calculation elsewhere to prevent unnecessary calculations
		draw_text(new_surface, mark, font = constants.FONT_CURSOR_TEXT, 
			coords = ((constants.CELL_WIDTH - 16), (constants.CELL_HEIGHT - 16)), 
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
	
	explosion_surface = pygame.Surface((constants.CELL_WIDTH, constants.CELL_HEIGHT))
	explosion_surface.set_alpha(150)
	explosion_surface.fill(color)

	area_effect = map_find_radius(valid_tiles[-1], radius)
	for (tile_x, tile_y) in area_effect:
			draw_tile_rect((tile_x, tile_y), color)

	#(ballistic_x * constants.CELL_WIDTH, ballistic_y * constants.CELL_HEIGHT))

	#SURFACE_MAIN.blit(explosion_surface, ((blast_x * constants.CELL_WIDTH), (blast_y * constants.CELL_HEIGHT)))
	#pygame.display.flip()
	#pygame.time.delay(settings.EXPLOSION_TICK_UPPER)

	#explosion_surface.fill((0, 0, 0))



	#draw_game()

def draw_map(map_to_draw):
	#camera visibility culling
	cam_x, cam_y = CAMERA.map_address
	display_map_width = int(constants.CAM_WIDTH / constants.CELL_WIDTH * 1)
	display_map_height = int(constants.CAM_HEIGHT / constants.CELL_HEIGHT * .7)

	render_w_min = int(cam_x - (display_map_width / 2))
	render_w_max = int(cam_x + (display_map_width / 2))
	render_h_min = int(cam_y - (display_map_height / 2))
	render_h_max = int(cam_y + (display_map_height / 2))

	#crudely clamp values
	if render_w_min < 0: render_w_min = 0
	if render_h_min < 0: render_h_min = 0

	x, y = helper_2d_list_dimensions(GAME.current_map)
	
	#previously used GAME.current_map_x and y instead of x/y
	if render_w_max > x: render_w_max = x
	if render_h_max > y: render_h_max = y

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
						SURFACE_MAP, text_to_display = "#", font = constants.FONT_RENDER_TEXT, 
						coords = (((x * constants.CELL_WIDTH) + 16), ((y * constants.CELL_HEIGHT)+ 16)), 
						text_color = constants.COLOR_L_BROWN, back_color = constants.COLOR_BLACK,
						center = True)
				else:
					#draw visible floor tiles
						draw_text(
						SURFACE_MAP, text_to_display = ".", font = constants.FONT_RENDER_TEXT, 
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
							SURFACE_MAP, text_to_display = "#", font = constants.FONT_RENDER_TEXT, 
							coords = (((x * constants.CELL_WIDTH) + 16), ((y * constants.CELL_HEIGHT) + 16)), 
							text_color = constants.COLOR_BROWN, back_color = constants.COLOR_BLACK,
							center = True)
					else:
						#draw explored floor but not visible wall tiles
						draw_text(
							SURFACE_MAP, text_to_display = ".", font = constants.FONT_RENDER_TEXT, 
							coords = (((x * constants.CELL_WIDTH) + 16), ((y * constants.CELL_HEIGHT) + 16)), 
							text_color = constants.COLOR_GRAY, back_color = constants.COLOR_BLACK,
							center = True)





###############################################################################################################
#helper functions

###############################################################################################################
#magic

def cast_heal(caster, value):
	if caster.creature.current_hp == caster.creature.max_hp:
		game_message(caster.creature.name_instance + " is already at full health.")
		return "cancelled"

	else:
		game_message(caster.creature.name_instance + " healed for " + str(value) + " health.")
		caster.creature.heal(value)

		if caster.creature.current_hp >= caster.creature.max_hp:
			game_message(caster.creature.name_instance + " is now at full health.")
		
	return None

def cast_lightning(caster, T_damage_maxrange):
	damage, m_range = T_damage_maxrange

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
				game_message(caster.creature.name_instance + " casts Alenko-Kharyalov Effect.")
				#check if spell uselessly hits wall
				target.creature.take_damage(damage, attacker = caster)

				game_message("You smell ozone.")

		
	
def cast_fireball(caster, T_damage_radius_range):
	#definitions, change later
	damage, local_radius, max_r = T_damage_radius_range
	caster_location = (caster.x, caster.y)
	#TODO get target tile
	if caster == PLAYER:
		point_selected = menu_tile_select(coords_origin = caster_location, max_range = max_r,
			 penetrate_walls = False, 
			 pierce_creature = False, 
			 radius = local_radius)
	else:
		point_selected = PLAYER.x, PLAYER.y

	if point_selected:
		game_message(caster.creature.name_instance + " casts Conflagration.")#" casts Alenko-Kharyalov Conflagration.")
		#get sequence of tiles
		tiles_to_damage = map_find_radius(point_selected, local_radius)
		creature_hit = False

		#damage all creatures in tiles
		for (x, y) in tiles_to_damage:
			#add visual feedback to fireball, maybe even adding a trail to its destination later
			#draw_explosion(local_radius, PLAYER.x, PLAYER.y, constants.COLOR_ORANGE)

			creature_to_damage = map_check_for_creatures(x, y)
			if creature_to_damage: 
				damage -= creature_to_damage.creature.resist_fire
				creature_to_damage.creature.take_damage(damage, attacker = caster)
				if creature_to_damage is not PLAYER:
					creature_hit = True

		if creature_hit:
			game_message("You smell the repugnant stench of burning flesh.", constants.COLOR_RED)

def cast_confusion(caster, effect_duration):
	#select tile
	point_selected = menu_tile_select(max_range = 12)
				

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

def fire_projectile(source, ranged_weapon, target, ammo_count):
	if (ammo_count > 0 and target and ranged_weapon):
		print("Ranged attack placeholder..")

################################################################################
#UI stuff
class ui_Button:
	def __init__(self, surface, button_text, size, center_coords, font = constants.FONT_MESSAGE_TEXT,
					color_box_hovered = constants.COLOR_GRAY, 
					color_box_default = constants.COLOR_L_GRAY,
					color_text_hovered = constants.COLOR_BLACK,
					color_text_default = constants.COLOR_BLACK):

		self.surface = surface
		self.button_text = button_text
		self.size = size
		self.center_coords = center_coords

		self.c_box_ho = color_box_hovered
		self.c_box_default = color_box_default
		self.c_text_ho = color_text_hovered
		self.c_text_default = color_text_default
		self.current_c_box = color_box_default
		self.current_c_text = color_text_default

		self.rect = pygame.Rect((0, 0), size)
		self.rect.center = center_coords

		self.font = font

	def update(self, player_input):
		local_events, local_mousepos = player_input
		mouse_x, mouse_y = local_mousepos
		mouse_clicked = False
		mouse_over = 	(mouse_x >= self.rect.left and 
						mouse_x <= self.rect.right and
						mouse_y >= self.rect.top and 
						mouse_y <= self.rect.bottom)

		for event in local_events:
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1: mouse_clicked = True

		if mouse_over:  #change colors and potentially accept mouse input
			self.current_c_box = self.c_box_ho
			self.current_c_text = self.c_text_ho
			if mouse_clicked:
				return True
		else:	#reset
			self.current_c_box = self.c_box_default
			self.current_c_text = self.c_text_default

	def draw(self):
		pygame.draw.rect(self.surface, self.current_c_box, self.rect)

		draw_text(self.surface, 
			self.button_text, 
			constants.FONT_MESSAGE_TEXT, 
			self.center_coords,
			self.current_c_text, 
			center = True)

#helpers 
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
	font_rect = font.render('a', False, (0, 0, 0)).get_rect()
	return font_rect.height

def helper_text_width(font):
	font_rect = font.render('a', False, (0, 0, 0)).get_rect()
	return font_rect.width

def helper_dice(upper_bound = 6, bias = 0):
	dice_roll = random.randint(1, upper_bound) + bias #simulates a dice roll from 1 to n, with a +/- bias.
	return dice_roll

def helper_text_prompt(background_fill = True, message = "", player_can_exit = True):
	global SURFACE_MAIN
	#draw rect in desired area of the screen with blinking cursor
	prompt_close = False
	user_text = ""

	question_rect = pygame.Rect(200, 200, 140, 32)		#where the question is posed
	input_rect = pygame.Rect(200, 200, 140, 32)			#where the player's input is displayed
	
	while not prompt_close:
		if background_fill:		#blot out entire background for the duration of the prompt
			SURFACE_MAIN.fill(constants.COLOR_BLACK)

		#get keypresses and stuff
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

			if event.type == pygame.KEYDOWN:		
				if event.key == pygame.K_ESCAPE:
					prompt_close = False
					user_text = ""
					return user_text
					
				if event.key == pygame.K_RETURN:
					prompt_close = False
					return user_text
					
				if event.key == pygame.K_BACKSPACE:
					user_text = user_text[:-1]

				elif user_text != pygame.K_RETURN:
					user_text += event.unicode

		question_surface = constants.FONT_MESSAGE_TEXT.render(message,
						constants.TEXT_AA, constants.COLOR_WHITE)

		question_rect.w = max(constants.PROMPT_DEFAULT_WIDTH, question_surface.get_width() + constants.PROMPT_OFFSET_X)
	

		text_surface = constants.FONT_MESSAGE_TEXT.render(user_text, 
					constants.TEXT_AA, constants.COLOR_WHITE)

		#dynamic scaling of textbox
		input_rect.w = max(constants.PROMPT_DEFAULT_WIDTH,
							text_surface.get_width() + constants.PROMPT_OFFSET_X)

		#rect that displays the player's input
		pygame.draw.rect(SURFACE_MAIN, constants.COLOR_GRAY, input_rect,
						constants.PROMPT_BORDER_THICKNESS)

		#display menu
		SURFACE_MAIN.blit(text_surface, 
			(input_rect.x + constants.PROMPT_OFFSET_X,
			input_rect.y + constants.PROMPT_OFFSET_Y)
			)

		pygame.display.flip()
		CLOCK.tick(constants.GAME_FPS)

def helper_gen_random_key(length):
	letters = string.ascii_lowercase
	result_str = ''.join(random.choice(letters) for i in range(length))
	return result_str

#this helper function attempts to place an actor at a tile, randomly finding a new place until it succeeds
def helper_try_place():
	print("Placeholder")

#gets the dimensions of an array, particularly maps
def helper_2d_list_dimensions(array):
  return [len(array)]+helper_2d_list_dimensions(array[0]) if(type(array) == list) else []


def ynq_prompt(): #prompt the player to select Yes, No or Quit
	print("Placeholder.")
###############################################################################################################
#menus

def open_door_prompt(in_event):

	global SURFACE_MAIN, PLAYER
	prompt_close = False

	while not prompt_close:
		#get keypresses and stuff
		draw_text(SURFACE_MAIN, 
			"Open door in which direction?", 
			constants.FONT_MESSAGE_TEXT, (100, 100), constants.COLOR_WHITE, back_color = constants.COLOR_BLACK, 
			center = False)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

			if event.type == pygame.KEYDOWN:	
				if event.key in constants.NUMPAD_KEYS:
					print("SHOULD have called the attempt open function")
					adjusted = game_direction_prompt(event_in = in_event)
					#adjusted = attempt_to_open_door(event_in = in_event)
					if adjusted != (0,0):
						prompt_close = True

				if event.key == pygame.K_ESCAPE or pygame.K_o:
					prompt_close = True
					game_message("You decide not to open anything.")
					#return 
				


		pygame.display.flip()
		CLOCK.tick(constants.GAME_FPS)

#def lock_prompt(in_event):

def menu_main():
	game_initialize()

	#create GAME object to store progress
	GAME = obj_Game()

	#draw title
	button_y = constants.CAM_HEIGHT * (2 / 5)
	button_x = constants.CAM_WIDTH / 3

	button_offset = 100

	title_y = constants.CAM_HEIGHT / 3
	title_x = constants.CAM_WIDTH / 2
	title_text = "The Timekeeper"

	menu_running = True

	new_game_button = ui_Button(SURFACE_MAIN, 
					"Begin your journey...", 
					(600, 75),
					(button_x, button_y),
					font = constants.FONT_TITLE_SCREEN2)

	continue_game_button = ui_Button(SURFACE_MAIN, 
					"Continue your journey...", 
					(600, 75),
					(button_x, button_y + button_offset),
					font = constants.FONT_TITLE_SCREEN2)

	exit_game_button = ui_Button(SURFACE_MAIN, 
					"Quit to desktop.", 
					(600, 75),
					(button_x, button_y + (button_offset * 2)),
					font = constants.FONT_TITLE_SCREEN2)

	while menu_running:
		list_of_events = pygame.event.get()
		mouse_position = pygame.mouse.get_pos()

		game_input = (list_of_events, mouse_position)

		#handle menu events
		for event in list_of_events:
			if event.type == pygame.QUIT:
				game_quit_sequence()

		#button updates
		if new_game_button.update(game_input):
			game_new()
			game_main_loop()
			game_initialize()

		if continue_game_button.update(game_input): #TODO: remove the 'game new' and disable the button if there's no savefile
			try:
				game_load()
			except:
				game_new()
			game_main_loop()
			game_initialize()

		if exit_game_button.update(game_input):
			game_quit_sequence()

		#draw menu

		if settings.DRAW_MENU_BACKGROUND and settings.MAIN_MENU_BG_IMAGE: 
			SURFACE_MAIN.blit(settings.MAIN_MENU_BG_IMAGE, (0,0))
		else:SURFACE_MAIN.fill(constants.COLOR_BLACK)   

		#clear
		draw_text(SURFACE_MAIN, title_text, constants.FONT_TITLE_SCREEN1,
					(title_x, title_y), constants.COLOR_WHITE, #constants.COLOR_BLACK, 
					center = True)

		new_game_button.draw()
		continue_game_button.draw()
		exit_game_button.draw()

		#update surfaces
		pygame.display.update()

def attempt_to_open_door(event_in, start_x = 0, start_y = 0):

	adjusted_coords = struc_Direction()
	to_open_coords = struc_Direction()

	adjusted_coords.x, adjusted_coords.y = game_direction_prompt(event_in, not_in_menu = False)

	print(str(adjusted_coords.x) + ", " + str(adjusted_coords.y))

	to_open_coords.x = start_x + adjusted_coords.x
	to_open_coords.y = start_y + adjusted_coords.y
	#print(str(to_open_coords.x) + ", " + str(to_open_coords.y))

	list_of_objects = map_objects_at_coords(to_open_coords.x, to_open_coords.y)
	for obj in list_of_objects:
		if obj.doorcom:
			obj.doorcom.interact()
			
			print("obj.door.interact() called")
		else:
			game_message("There is nothing to open there.")
			print("obj.door.interact() not called")

#def player_attempts_lock(event_in):

#really messy, clean up later
def menu_inventory():
	menu_close = False
	#clean up using tuples

	window_width = constants.CAM_WIDTH
	window_height = constants.CAM_HEIGHT

	#include different parameters later for teh lulz
	menu_width = 900
	menu_height = 700
	menu_x = (window_width / 2) - (menu_width / 2)
	menu_y = (window_height / 2) - (menu_height / 2)

	menu_text_font = constants.FONT_MESSAGE_TEXT
	menu_text_height = helper_text_height(menu_text_font)

	local_inventory_surface = pygame.Surface((menu_width, menu_height))
	
	while not menu_close:
		#clear the menu by wiping it black
		local_inventory_surface.fill(constants.COLOR_BLACK)

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

		if settings.DEBUG_MOUSE_IN_INVENTORY:
			if mouse_in_window == True:
				print(mouse_line_selection)

		if settings.DEBUG_MOUSE_DELTA == True:
			if delta_x > 0 and delta_y > 0:
				print(delta_x, delta_y)

					#create buttons for the right side of the menu
		

		for event in events_list:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_i:
					menu_close = True
					COLOR_GRAY = (100, 100, 100)

			if event.type == pygame.MOUSEBUTTONDOWN:
				if (event.button == 1):
					if (mouse_in_window and 
						mouse_line_selection <= len(print_list) - 1):
						PLAYER.container.inventory[mouse_line_selection].item.use()

			if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
				if len(PLAYER.container.inventory) > 0:
					#check if item is equipment, and, if so, unequip it
					try:
						PLAYER.container.inventory[mouse_line_selection].equipment.unequip()
					except:
						print("Meh.")

					#drop selected item
					PLAYER.container.inventory[mouse_line_selection].item.drop(PLAYER.x, PLAYER.y)
					if settings.CLOSE_AFTER_DROP:
						return "no-action"
					#if settings.Mod2 == False:
					#	return "no-action"
					#else:
					#	return "player-moved"
					
		#draw every line in the list
		for line, (name) in enumerate(print_list):
			if line == mouse_line_selection and mouse_in_window == True:
				draw_text(local_inventory_surface,
					name,
					menu_text_font,
					(0, 0 + (line * menu_text_height)), constants.COLOR_WHITE, constants.COLOR_GRAY)
			else:
				draw_text(local_inventory_surface,
					name, menu_text_font,
					(0, 0 + (line * menu_text_height)), constants.COLOR_WHITE)

		button_height = 80
		button_width = 100
		equipment_button = ui_Button(local_inventory_surface, 
								"Equipment", 
								(1000, 1000),
								(100, 100)
								)

		#render game 
		draw_game()
		SURFACE_MAIN.blit(local_inventory_surface, (int(menu_x), int(menu_y)))
			
		CLOCK.tick(constants.GAME_FPS)
		pygame.display.update()

def menu_tile_select(coords_origin = None, max_range = None, 
	radius = None, penetrate_walls = True, pierce_creature = True):
	#this 'menu' lets the player select a tile, for spells, etc.
	menu_close = False

	while not menu_close:
		mouse_x, mouse_y = pygame.mouse.get_pos() 				#get mouse postion
		events_list = pygame.event.get()						#get button clicks

		#mouse map selection
		mapx_pixel, mapy_pixel = CAMERA.win_to_map((mouse_x, mouse_y))
		map_coord_x = int(mapx_pixel / constants.CELL_WIDTH)
		map_coord_y = int(mapy_pixel / constants.CELL_HEIGHT)

		valid_tiles = []

		if coords_origin:
			full_list_of_tiles = map_find_line(coords_origin, (map_coord_x, map_coord_y))

			for i, (x, y) in enumerate(full_list_of_tiles):
				valid_tiles.append((x, y))
				
				if max_range and i == max_range:				#stop at max range
					break
				if not penetrate_walls and GAME.current_map[x][y].block_path: 	#stop at wall
					break
				if not pierce_creature and map_check_for_creatures(x, y):		#stop at creature
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

			#update drawing the game map
			SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
			SURFACE_MAP.fill(constants.COLOR_BLACK)
			CAMERA.update()
			draw_map(GAME.current_map)
			for obj in GAME.current_objects:
				obj.draw()

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

			#these numbers are the starting offset, for left/top padding
			SURFACE_MAIN.blit(SURFACE_MAP, (0, 0), CAMERA.rectangle)				

			if settings.ENABLE_DEBUG == True:
				draw_debug()

			draw_messages()
			#update display
			pygame.display.flip()
			CLOCK.tick(constants.GAME_FPS)

##########################################################################################################
#procedural generators

#note - possibly include 'special function' in items?
#to allow additional behaviors in items such as with pickaxes

#items
#use better solution later


def gen_scroll_lightning(coords):
	x, y = coords
	damage = helper_dice(5, 6)
	m_range = 8
	item_com = com_Item(use_function = cast_lightning, value = (damage, m_range), name = "Scroll of Lightning")#not going to worry about weight or volume yet

	return_object = obj_Actor(x, y, "Scroll of Lightning", item = item_com, 
							icon = settings.scroll_icon, icon_color = constants.COLOR_WHITE)

	return return_object

def gen_scroll_fireball(coords):
	x, y = coords
	damage = helper_dice(7, 7)
	local_radius = 2
	max_r = 9
	item_com = com_Item(use_function = cast_fireball, value = (damage, local_radius, max_r), name = "Scroll of Fireball")#not going to worry about weight or volume yet

	return_object =obj_Actor(x, y, "Scroll of Fireball", item = item_com, 
							icon = settings.scroll_icon, icon_color = constants.COLOR_ORANGE)

	return return_object

def gen_scroll_confusion(coords):
	x, y = coords
	effect_duration = helper_dice(3, 3)
	item_com = com_Item(use_function = cast_confusion, value = (effect_duration), name = "Scroll of Confusion")#not going to worry about weight or volume yet
	return_object =obj_Actor(x, y, "Scroll of Confusion", item = item_com, 
							icon = settings.scroll_icon, icon_color = constants.COLOR_GRAY)

	return return_object

#under construction
def distribute_item(coords):
	x, y = coords

#
def gen_item(coords, duration = 0):
	x, y = coords

	effect_duration = helper_dice(3, 3)
	item_com = com_Item(use_function = cast_confusion, value = (effect_duration), name = "Scroll of Confusion")#not going to worry about weight or volume yet
	return_object =obj_Actor(x, y, "Scroll of Confusion", item = item_com, 
							icon = settings.scroll_icon, icon_color = constants.COLOR_GRAY)


#generates a generic item
def gen_equip_item(coords, phys_outgoing = 0, equip_slot = "", item_name = "", item_icon = "", item_icon_color = constants.COLOR_WHITE):
	x, y = coords

	equipment_com = com_Equipment(damage_phys_bonus = phys_outgoing, equip_slot = slot, name = item_name) 

	return_object = obj_Actor(x, y, item_name,
					icon = item_icon, icon_color = item_icon_color,
					equipment = equipment_com)
	return return_object

	item = GAME.current_objects.append(tree)


def gen_weapon_sword(coords):
	x, y = coords
	equipment_com = com_Equipment(damage_phys_bonus = 18, slot = "Main Hand", name = "Longsword") #, name = "a plain longsword")

	return_object = obj_Actor(x, y, "Longsword",
					icon = settings.weapon_icon, icon_color = constants.COLOR_L_BLUE,
					equipment = equipment_com)
	return return_object

def gen_armor_leather(coords):
	x, y = coords
	equipment_com = com_Equipment(resist_phys_bonus = 6, resist_fire_bonus = 2,slot = "Armor", name = "a suit of leather armor")

	return_object = obj_Actor(x, y, "Leather Armor",
					icon = settings.armor_icon, icon_color = constants.COLOR_L_BLUE,
					 equipment = equipment_com) #, name_object = "TURRRRTTTLLLESSSSSS!!!!")
	return return_object

def gen_armor_helmet(coords):
	x, y = coords
	equipment_com = com_Equipment(resist_phys_bonus = 3, resist_fire_bonus = 1, slot = "Helmet", name = "an ancient Temryavite helmet") 

	item_com = com_Item(value = 3, use_function = cast_heal, name = "an ancient Temryavite helmet") 

	return_object = obj_Actor(x, y, "Temryavite Helm",
					icon = settings.armor_icon, icon_color = constants.COLOR_L_BLUE,
					 equipment = equipment_com, item = item_com)
	return return_object

def gen_armor_cloak(coords):
	x, y = coords
	equipment_com = com_Equipment(resist_phys_bonus = 1, resist_fire_bonus = - 1,slot = "Cloak", name = "a filthy barbarian cloak") 

	item_com = com_Item(value = 3, use_function = cast_heal, name = "a filthy barbarian cloak") 

	return_object = obj_Actor(x, y, "Southern Horde Parka",
					icon = settings.armor_icon, icon_color = constants.COLOR_L_BLUE,
					 equipment = equipment_com, item = item_com)
	return return_object

def gen_armor_shirt(coords):
	x, y = coords
	equipment_com = com_Equipment(resist_phys_bonus = 0, slot = "Shirt", name = "a bleached Guiding Star tunic.") 

	item_com = com_Item(value = 3, use_function = cast_heal, name = "a bleached Guiding Star tunic.")

	return_object = obj_Actor(x, y, "Guiding Star tunic",
					icon = settings.armor_icon, icon_color = constants.COLOR_GRAY,
					 equipment = equipment_com)
	return return_object

def gen_armor_boots(coords):
	x, y = coords
	equipment_com = com_Equipment(resist_phys_bonus = 1, slot = "Boots", name = "a pair of muddy combat boots.") 

	return_object = obj_Actor(x, y, "Combat Boots",
					icon = settings.armor_icon, icon_color = constants.COLOR_L_BROWN,
					 equipment = equipment_com)
	return return_object

def gen_armor_chainmail(coords):
	x, y = coords
	equipment_com = com_Equipment(resist_phys_bonus = 3, resist_fire_bonus = 2, slot = "Chainmail", name = "Ars Enchantica Chainmail") 

	return_object = obj_Actor(x, y, "Ars Enchantica Chainmail",
					icon = settings.armor_icon, icon_color = constants.COLOR_L_GRAY,
					 equipment = equipment_com)
	return return_object

def gen_armor_gloves(coords):
	x, y = coords

	equipment_com = com_Equipment(resist_phys_bonus = 1, resist_fire_bonus = 1, slot = "Gloves", name = "a weathered pair of standard-issue, legionaire glvoes.") 

	return_object = obj_Actor(x, y, "Pax Magisteria gloves",
					icon = settings.armor_icon, icon_color = constants.COLOR_GRAY,
					 equipment = equipment_com)
	return return_object

	#non-item actors

def gen_tree(coords, fruit = "None"):
	x, y = coords

	#item_com = com_Item(value = 3, use_function = cast_heal, name = "an Apple") 

	 
	ai_com = ai_Static()


	#name of item when picked up
	tree = obj_Actor(x, y, "an oak tree",
		ai = ai_com, #item = item_com,
		icon = settings.tree_icon, icon_color = constants.COLOR_GREEN)

	GAME.current_objects.append(tree)

#player
def gen_player(coords):
	global PLAYER, PLAYER_NAME
	x, y = coords
	#create the player
	container_com = com_Container()
	creature_com = com_Creature(PLAYER_NAME,
								damage_phys_base = 8, resist_phys_base = 3, hp = 100, #player's creature component name
								death_function = death_player
								)
	allegiance_com = com_Allegiance(category = "player", 
					hostile_list = {"eldritch", "wild", "draconic"},
					docile = False
					)

	PLAYER = obj_Actor(x, y, "Player",  
						creature = creature_com,
						container = container_com,
						icon = " @ ", icon_color = constants.COLOR_WHITE,
						allegiance_com = allegiance_com
						)
	PLAYER_SPAWNED = True

	GAME.current_objects.append(PLAYER)
	
def gen_town_folk(coords):
	x, y = coords

	container_com = com_Container()
	
	creature_com = com_Creature(name_instance = "Townfolk",
								damage_phys_base = 8, resist_phys_base = 3, hp = 10, #player's creature component name
								death_function = death_monster
								)

	ai_com = ai_Townfolk_Wander()
	
	allegiance_com = com_Allegiance(category = "townfolk")

	npc = obj_Actor(x, y, "Some random person.",  
						creature = creature_com,
						container = container_com,
						icon = " @ ", icon_color = constants.COLOR_L_GRAY,
						ai = ai_com,
						allegiance_com = allegiance_com
						
						)
	print("Townsfolk spawned")


	GAME.current_objects.append(npc)

#def gen_town_guard

#enemies
def gen_creature(coords):
	global GAME

	random_num = helper_dice(100, 0)
	if random_num  <= 30 : 					new_enemy = gen_nightcrawler_greater(coords)
	elif random_num <= 80 :					new_enemy = gen_nightcrawler_lesser(coords)
	elif random_num >= 90 :					new_enemy = gen_dragon(coords)
	else:									new_enemy = gen_rabbit(coords)
	
	GAME.current_objects.insert(0, new_enemy)

def gen_nightcrawler_lesser(coords):
	x, y = coords

	item_com = com_Item(value = 3, use_function = cast_heal, name = "the carcass of a Lesser Nightcrawler") 
	creature_com = com_Creature("Lesser Nightcrawler", death_function = death_monster,
								hp = 12,
								damage_phys_base = (helper_dice(3, 5)),
								resist_phys_base = (helper_dice(3, 3)),
								xp_on_death = 5
	) 
	ai_com = ai_Chase()
	allegiance_com = com_Allegiance(category = "eldritch",
								hostile_list = {"player", "townfolk" },
								docile = False)

							#name of item when picked up
	ENEMY = obj_Actor(x, y, "Lesser Nightcrawler",
		creature = creature_com, ai = ai_com, item = item_com,
		icon = settings.eldritch_icon, icon_color = constants.COLOR_GRAY,
		allegiance_com = allegiance_com)

	return ENEMY

def gen_nightcrawler_greater(coords):
	x, y = coords
	item_com = com_Item(value = 5, use_function = cast_heal, name = "the carcass of a Greater Nightcrawler")								#name of enemy when alive
	creature_com = com_Creature("Greater Nightcrawler", death_function = death_monster,
								hp = 15,
								damage_phys_base = (helper_dice(4, 9)),
								resist_phys_base = (helper_dice(4, 4)),
								xp_on_death = 12
	) 
	
	ai_com = ai_Chase()

	allegiance_com = com_Allegiance(category = "eldritch",
								hostile_list = {"player", "townfolk", "wild" },
								docile = False)

	#name of item when picked up
	ENEMY = obj_Actor(x, y, "Greater Nightcrawler", 
		creature = creature_com, ai = ai_com, item = item_com, icon = settings.eldritch_icon, 
		icon_color = constants.COLOR_GRAY,
		allegiance_com = allegiance_com)

	return ENEMY

def gen_dragon(coords):
	x, y = coords
	item_com = com_Item(value = 70, use_function = cast_heal, name = "the carcass of a Golden Dragon")								#name of enemy when alive
	creature_com = com_Creature("Golden Dragon", death_function = death_monster,
								hp = 35,
								damage_phys_base = (helper_dice(9, 12)),
								resist_phys_base = (helper_dice(4, 7)),
								xp_on_death = 75
	) 
	
	allegiance_com = com_Allegiance(category = "draconic",
								hostile_list = {"player", "townfolk", "eldritch", "wild" },
								docile = False)

	ai_com =	ai_Dragon()
	#name of item when picked up
	ENEMY = obj_Actor(x, y, "Golden Dragon", 
		creature = creature_com, ai = ai_com, item = item_com, icon = settings.draconic_icon, 
		icon_color = constants.COLOR_YINZER,
		allegiance_com = allegiance_com)

	return ENEMY

def gen_rabbit(coords):
	x, y = coords
	item_com = com_Item(value = 4, use_function = cast_heal, name = "the carcass of a Rabbit")								#name of enemy when alive
	creature_com = com_Creature("Rabbit", death_function = death_monster,
								hp = 3,
								damage_phys_base = 1,
								resist_phys_base = 1)

	allegiance_com = com_Allegiance(category = "wild",
								hostile_list = {"player", "townfolk", "eldritch", "draconic" },
								docile = False)

	ai_com = ai_Flee()
					
	ENEMY = obj_Actor(x, y, "Rabbit", 
		creature = creature_com, ai = ai_com, item = item_com, icon = settings.game_animal_icon, 
		icon_color = constants.COLOR_L_BROWN,
		allegiance_com = allegiance_com)

	return ENEMY

#special
def gen_stairs(coords, downwards):
	x, y = coords
	
	if downwards:
		stairs_com = com_Stairs()
		stairs = obj_Actor(x, y, "A staircase leading down.", stairs = stairs_com, 
			icon = settings.stairs_up_icon)
	else:
		stairs_com = com_Stairs(downwards)
		stairs = obj_Actor(x, y, "A staircase leading up.", stairs = stairs_com, icon = settings.stairs_down_icon)

	GAME.current_objects.append(stairs)

def gen_exit_point_stairs(coords, downwards, target_type = None):
	x, y = coords
	
	#randomly choose a type out of a dungeon or a cave
	if target_type == None:
		i = helper_dice(10)
		if i <= 7: map_type = "cave"
		elif i <= 10: map_type = "dungeon"
	else:
		map_type = target_type
	
	exit_point_com = com_Exit_Point(require_input = True, target_map_type = map_type)


	if downwards:
		ep_stairs = obj_Actor(x, y, "A staircase leading down.", exit_point = exit_point_com, icon = settings.stairs_up_icon, 
			static = True, discovered = False)
	else:
		ep_stairs = obj_Actor(x, y, "A staircase leading up.", exit_point = exit_point_com, icon = settings.stairs_up_icon, 
			static = True,  discovered = False)

	GAME.current_objects.append(ep_stairs)

def gen_exit_point_door(coords, 
	locked_by_default = False, closed_by_default = True, is_closed = True, is_locked = False, material = "wooden", 
	target_type = None,
	target_key = "",
	additional_message = "You are curious as to what may lie behind."):
	x, y = coords

	#randomly choose a type out of a dungeon or a cave
	if target_type == None:
		i = helper_dice(10)
		if i <= 4: map_type = "cave"
		elif i <= 10: map_type = "dungeon"
	else:
		map_type = target_type

	exit_point_com = com_Exit_Point(require_input = True, target_map_type = map_type, next_map_key = target_key)
	door_com = com_Door(is_destructable = True, is_locked = locked_by_default, is_closed = closed_by_default)
	
	if closed_by_default:
		ep_door = obj_Actor(x, y, ("A closed " + material + " door. ", additional_message), 
							exit_point = exit_point_com, doorcom = door_com, icon = settings.door_closed_icon,
							static = True,  discovered = False)
	
	else:
		ep_door = obj_Actor(x, y, ("An open " + material +" door. " + additional_message),
							exit_point = exit_point_com, door = door_com, icon = settings.door_open_icon,
							static = True,  discovered = False)

	GAME.current_objects.append(ep_door)

def gen_barrier_door(coords, default_locked, default_closed):
	print("Temporary placeholder.")

def gen_building_door(new_map, new_building):
	side = helper_dice(4, 0)
	if side == 1: #top?
		door_x_pos = round((new_building.x1 + new_building.x2) / 2)
		door_y_pos = new_building.y1

	if side == 2: #bottom
		door_x_pos = round((new_building.x1 + new_building.x2) / 2)
		door_y_pos = new_building.y2 - 1

	if side == 3: #left
		door_y_pos = round((new_building.y1 + new_building.y2) / 2)
		door_x_pos = new_building.x1  


	if side == 4: #right
		door_y_pos = round((new_building.y1 + new_building.y2) / 2)
		door_x_pos = new_building.x2 - 1 

	new_map[door_x_pos][door_y_pos].block_path = False
	gen_exit_point_door((door_x_pos, door_y_pos), target_type = "house")

################################################################################################################

#Main game loop, on tick
def game_main_loop():
	global PLAYER
	game_quit = False
	player_action = "no-action"

	while not game_quit:
		#player input
		player_action = game_handle_keys()

		map_calculate_fov()

		if player_action == "QUIT":
			game_quit_sequence()
		
		for obj in GAME.current_objects:
			if obj.ai: 
				if player_action != "no-action":
					obj.ai.take_turn()

			if obj.exitportal:
				obj.exitportal.update()

		if settings.DEBUG_PRINT_TURNS == True and player_action != "no-action":
			GAME.turns_elapsed += 1
			print(str(GAME.turns_elapsed) + " turns have elapsed so far")

		if (PLAYER.state == "STATUS_DEAD" or PLAYER.state == "STATUS_WIN"):	#either ending condition
			game_quit = True

	
		draw_game()
	
		pygame.display.flip()   #update the display

		CLOCK.tick(constants.GAME_FPS)   #tick the clock

#########################################################################################################

def game_handle_keys():
	global FOV_CALCULATE

	keys_list = pygame.key.get_pressed()
	events_list = pygame.event.get()
	
	#check for mod key (shift)
	MOD_KEY = (keys_list[pygame.K_RSHIFT] or keys_list[pygame.K_LSHIFT])
	
	for event in events_list:
		if event.type == pygame.QUIT:
			return "QUIT"	

		if event.type == pygame.KEYDOWN:
			move_coords = struc_Direction()
			move_coords.x, move_coords.y = game_direction_prompt(event_in = event)
			if (move_coords.x,  move_coords.y) != (0, 0):
				PLAYER.creature.move(move_coords.x, move_coords.y)

				#non-movement, non turn-changing ?
			if event.key == pygame.K_COMMA:
				objects_at_player = map_objects_at_coords(PLAYER.x, PLAYER.y)
				for obj in objects_at_player:
					if obj.item:
						obj.item.pick_up(PLAYER)
						if settings.Mod2 == False:
							return "no-action"
							
			if event.key == pygame.K_p:
				print("Test key triggered.")
				return "no-action"

			#open inventory or something idk tho
			if event.key == pygame.K_i:
				menu_inventory()
				if settings.Mod2 == False:
					return "no-action"
						
				#temporarily changed to quit the game

			#figure out what stuff is or something
			if event.key == pygame.K_q:
				#query_coords = map_tile_query()
				if settings.Mod2 == False:
					return "no-action"
					

			#fire projectiles and stuff
			if event.key == pygame.K_f:
				print("Hi")

			#open doors and stuff
			if event.key == pygame.K_o:
				#prompt player to select a new direction
				open_door_prompt(in_event = event)
				print("Open door function - receiving input.")

			FOV_CALCULATE = True
	
			#key L, turn on tile selection. change later as needed
			if MOD_KEY and event.key == pygame.K_PERIOD:
				print("Stair/portal key pressed")
				#reuse this kind of thing later 		
				list_of_objects = map_objects_at_coords(PLAYER.x, PLAYER.y)
				for obj in list_of_objects:
					if obj.stairs:
						obj.stairs.use()

						print("Using stairs.")
					if obj.exitportal:
						print("Using portal. I think.")
						obj.exitportal.use()
						return "player-moved"
					if obj.exit_point:
						obj.exit_point.use()
						return "player-moved"

			return "player-moved"
	return "no-action"

def game_direction_prompt(event_in, not_in_menu = True):
	#return a direction picked from using the numpad, used for moving, firing projectiles, or interacting with doors
	target_coords = struc_Direction(x = 0, y = 0)

	while not_in_menu:

		if event_in.key == pygame.K_KP1:
			target_coords = (-1, 1)
			#print("KP1")
			
		elif event_in.key == pygame.K_KP2:# or pygame.K_DOWN:
			target_coords = (0, 1)
			#print("KP2/KD")
			
		elif event_in.key == pygame.K_KP3:
			target_coords = (1, 1)
			#print("KP3")
			
		elif event_in.key == pygame.K_KP4: # or pygame.K_LEFT:
			target_coords = (-1, 0)
			#print("KP4/KL")
			
		elif event_in.key == pygame.K_KP5: #this one does literally nothing, just kinda chillin' here till I feel like using it
			target_coords = (0, 0)
			#print("KP5")
			
		elif event_in.key == pygame.K_KP6: # or pygame.K_RIGHT:
			target_coords = (1, 0)
			#print("KP6/KR")
			
		elif event_in.key == pygame.K_KP7:
			target_coords = (-1, -1)
			#print("KP7")

		elif event_in.key == pygame.K_KP8: # or pygame.K_UP:
			target_coords = (0, -1)
			#print("KP8/KU")
			
		elif event_in.key == pygame.K_KP9:
			target_coords = (1, -1)
			#print("KP9")
		else:
			target_coords = (0, 0)
			#print("No directional input.")

		not_in_menu = False
		return target_coords

def game_message(game_msg, msg_color = constants.COLOR_WHITE):
	GAME.message_history.append((game_msg, msg_color))

def game_new():
	global GAME, PLAYER_NAME
	#start a new game and map, and player with nonsense coords to be placed elsewhere
	PLAYER_NAME = helper_text_prompt(True)	#prompt the player for a name
	gen_player((0,0))
	
	PLAYER.creature.name = PLAYER_NAME
	print ("Player.creature.name is = " + PLAYER.creature.name)

	#setup the map the player spawns in
	GAME.current_map, GAME.current_buildings = map_create_town()
	map_place_objects_town(GAME.current_buildings)

	#PLAYER.x, PLAYER.y = (2, 3)

def game_quit_sequence():
	game_save()
	pygame.quit()
	pygame.font.quit()
	exit()

def game_save():		#add stuff for distributed builds that checks/adds a savegame folder
	if PLAYER:  #if the player is created (and not still in menu), save
		#filename = 'savedata/' + (PLAYER.creature.name_instance) + '.'+ 'savegame'
		if settings.SAVE_COMPRESSION:
			with gzip.open('savedata\savegame', 'wb') as file:
				pickle.dump([GAME, PLAYER], file)
		else:
			with open('savedata\savegame', 'wb') as file:  
				pickle.dump([GAME, PLAYER], file)

def game_load():
	global GAME, PLAYER
	#'savedata\savegame'
	if settings.SAVE_COMPRESSION == True:
		with gzip.open('savedata\savegame', 'rb') as file:
			GAME, PLAYER = pickle.load(file)
	else:
		with open('savedata\savegame', 'rb') as file:
			GAME, PLAYER = pickle.load(file)

	map_make_fov(GAME.current_map)

#'''initializing the main window and pygame'''
def game_initialize():
	global SURFACE_MAIN, SURFACE_MAP, FOV_CALCULATE, GAME
	global CAMERA, PLAYER, ENEMY, PLAYER_NAME
	global DUNGEON_DEPTH, SURFACE_WINDOW, SURFACE_BOTTOM_PANEL
	global CLOCK

	pygame.init()

	PLAYER_NAME = "Bob the Guy"

	if constants.PermitKeyHolding == True:
		pygame.key.set_repeat(constants.KeyDownDelay, constants.KeyRepeatDelay)

	#create the rendered window
	SURFACE_WINDOW = pygame.display.set_mode((int(constants.CAM_WIDTH * 1), int(constants.CAM_HEIGHT * 1)))


	SURFACE_MAIN = pygame.display.set_mode((constants.CAM_WIDTH, constants.CAM_HEIGHT))
	SURFACE_MAP = pygame.Surface((constants.MAP_WIDTH * constants.CELL_WIDTH,
									constants.MAP_HEIGHT * constants.CELL_HEIGHT))	

	SURFACE_BOTTOM_PANEL = pygame.display.set_mode((int(constants.CAM_WIDTH * 1), int(constants.CAM_HEIGHT * 1)))

	CAMERA = obj_Camera()

	#create GAME object to store game state
	GAME = obj_Game()
	CLOCK = pygame.time.Clock()

	FOV_CALCULATE = True

if __name__ == '__main__':
	menu_main()
	