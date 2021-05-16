#3rd party modules
import pygame
import tcod as libtcod
import math
#import cpickle as pickle
import pickle
import gzip
import datetime
import os.path

import random
import string
import json

#necessary game files
import constants
import settings
import helpers
import objects
import structures
import components
import map_utilities
import actor_utilities
import misc_utils


class obj_Actor:
	def __init__(self, x, y, 
		name_object,
		creature = None, 
		ai = None, 
		ai_active = False,

		container = None, 
		item = None, 
		description = "No description for this actor.", 
		state = None,

		num_turns = 0, icon = "x", icon_color = constants.COLOR_WHITE,
		equipment = None,
		interact_function = None,
		stairs = None,
		static = False,		
		discovered = False,
		exit_point = False,
		doorcom = None,
		allegiance_com = None,
		shopkeep_com = None,
		trap_com = None
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
			self.item = components.ItemComponent()
			self.item.owner = self

		self.ai_active = ai_active

		self.stairs = stairs
		if self.stairs:
			self.stairs.owner = self

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

		self.shopkeep_com = shopkeep_com
		if self.shopkeep_com:
			self.shopkeep_com.owner = self

		self.trap_com = trap_com
		if self.trap_com:
			self.trap_com.owner = self

	@property
	def display_name(self):
		if self.creature:
			return(self.creature.name_instance + " the " + self.name_object)

		if self.item:
			if self.equipment and self.equipment.equipped:
				return (self.name_object + "(" + self.equipment.slot + ")") 
			else:
				return self.name_object

	def draw(self, map_surface = None, local_fov = None):
		is_visible = libtcod.map_is_in_fov(FOV_MAP, self.x, self.y)


		if self.static and self.discovered:
			draw_text(SURFACE_MAP, text_to_display = self.icon, font = constants.FONT_RENDER_TEXT, 
				coords = ((self.x * constants.CELL_WIDTH) + 16 , (self.y * constants.CELL_HEIGHT) + 16), 
				text_color = self.icon_color, 
				center = True)

		if is_visible:
			if self.static: 
				self.discovered = True
			if self.ai_active == False:
				self.ai_active = True

			draw_text(SURFACE_MAP, text_to_display = self.icon, font = constants.FONT_RENDER_TEXT, 
				coords = ((self.x * constants.CELL_WIDTH) + 16 , (self.y * constants.CELL_HEIGHT) + 16), 
				text_color = self.icon_color, 
				center = True)
			

	def distance_to(self, other):
		delta_x = other.x - self.x
		delta_y = other.y - self.y
		return math.sqrt(delta_x ** 2 + delta_y ** 2)

	def move_towards(self, other, game_instance = None):
		
		delta_x = other.x - self.x
		delta_y = other.y - self.y
		distance = math.sqrt(delta_x ** 2 + delta_y ** 2)
		if distance == 0:
			distance = 1

		#delta_x = int((delta_x / distance))
		#delta_y = int((delta_y/distance))
		delta_x = int(round(delta_x / distance))
		delta_y = int(round(delta_y / distance))

		self.creature.move(delta_x, delta_y, game_instance)

	def move_away(self, other, game_instance = None):
		
		delta_x = self.x - other.x 
		delta_y = self.y - other.y 
		distance = math.sqrt(delta_x ** 2 + delta_y ** 2)

		if distance == 0: distance = 1 
		delta_x = int(round(delta_x / distance))
		delta_y = int(round(delta_y / distance))

		self.creature.move(delta_x, delta_y, game_instance)

#massive structure that stores game state data 		
class obj_Game:
	def __init__(self):
		self.turns_elapsed = 0
		self.message_history = []
		self.first_map = True
		self.current_objects = []
		self.current_map, self.current_rooms, self.next_map_x, self.next_map_y = map_create()

		self.existing_maps =  {}      #dictionary used for new map loading system, replace with tree later
		self.this_map_key = ""
		self.new_key = ""
		self.next_map_type = "dungeon"
		self.current_map_x = constants.MAP_WIDTH
		self.current_map_y = constants.MAP_HEIGHT
		
	def transition(self):
		global FOV_CALCULATE

 		#get exit point the player is standing on
		list_of_objects = components.map_objects_at_coords(PLAYER.x, PLAYER.y, gameinstance = GAME)	
		for obj in list_of_objects:
			if obj.exit_point:
			#if the exit point leads to another map, load the map
				if obj.exit_point.next_map_key != "": 
					print("This exit point's key is " + obj.exit_point.next_map_key)

					(PLAYER.x, PLAYER.y, self.current_map, self.current_rooms, self.current_objects) = self.existing_maps[obj.exit_point.next_map_key]
					#get the dimensions of the next map (recursive list) and feed it to the FOV
					self.next_map_x, self.next_map_y = misc_utils.get_map_dimensions(self.current_map)
				
					map_make_fov(self.current_map, self.next_map_x, self.next_map_y) #, self.current_map.x_dimension, self.current_map.y_dimension)



				else:						#if the exit point has no key, create a new map and key, then load it
					##################################################################################################
					#create new key for the map to unload and new map
					GAME.current_key = helper_gen_random_key(settings.MAP_KEY_LENGTH)		
					GAME.new_key = helper_gen_random_key(settings.MAP_KEY_LENGTH)

					list_of_objects = components.map_objects_at_coords(PLAYER.x, PLAYER.y, gameinstance = GAME)
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
						#PLAYER.x, PLAYER.y = map_place_door_on_walls(door_x_pos, door_y_pos)
						

					if self.next_map_type == "cave":
						self.current_map, self.next_map_x, self.next_map_y = map_random_walk()

						map_tryplace_player(map_x_in = self.next_map_x, map_y_in = self.next_map_y)
						gen_exit_point_stairs((PLAYER.x, PLAYER.y), downwards = False)

					if self.next_map_type == "overworld":
						self.current_map = map_create_overworld()
						gen_exit_point_stairs((PLAYER.x, PLAYER.y), downwards = False)
						
					self.next_map_x, self.next_map_y = misc_utils.get_map_dimensions(self.current_map)
					
					#set the first exit point in the new map (where the player is located) to point back to the old one
					list_of_objects = components.map_objects_at_coords(PLAYER.x, PLAYER.y, gameinstance = GAME)
					for obj in list_of_objects:	
						if obj.exit_point: 
							obj.exit_point.next_map_key = GAME.current_key
							print("Exit point set to previous map.")
					
					map_to_save = (PLAYER.x, PLAYER.y, self.current_map, self.current_rooms, self.current_objects)
			
					self.existing_maps[GAME.new_key] = map_to_save
				
		map_make_fov(self.current_map, fov_x = self.next_map_x, fov_y = self.next_map_y)

		FOV_CALCULATE = True

	def game_message(self, game_msg, msg_color = constants.COLOR_WHITE):
		self.message_history.append((game_msg, msg_color))



###############################################################################################################################
#components






######################################################################################################################
#AI scripts
	#execute once per turn

def ai_designate_targets(actor = None):
	global GAME
	map_make_local_fov(GAME.current_map, actor_in = (actor), fov_x = GAME.current_map_x - 1, fov_y = GAME.current_map_y - 1)
	libtcod.map_compute_fov(actor.creature.local_fov, actor.x, actor.y, 
								actor.creature.local_line_of_sight, 
								constants.FOV_LIGHT_WALLS, constants.FOV_AI_ALGO)

	for obj in GAME.current_objects:
		if obj.creature:
			if libtcod.map_is_in_fov(actor.creature.local_fov, obj.x, obj.y) and obj != actor:
				actor.creature.proximate_actors.append(obj)

	if (len(actor.creature.proximate_actors)) == 0: return "no actors"

	for obj in actor.creature.proximate_actors:
		if obj.allegiance_com and actor.allegiance_com:

			# I literally have no idea why everything in this game is a list of lists, but hallelujah, it works now
			for category in actor.allegiance_com.hostile_list[0]:
				if category in obj.allegiance_com.category[0]:			# ditto
					distance_to_target = actor.distance_to(obj)
					target = structures.Target(actor = obj, distance = (distance_to_target), threat_level = 0)
					actor.creature.proximate_hostiles.append(target)
								
	if (len(actor.creature.proximate_hostiles)) == 0: return "no actors"
	actor.creature.proximate_hostiles = sorted(actor.creature.proximate_hostiles, key=lambda target: target.distance)
	target = (actor.creature.proximate_hostiles)[0]

	#reset everything
	actor.creature.local_fov = None
	actor.creature.proximate_hostiles = []
	actor.creature.proximate_actors = []

	return target	




class ai_Confuse:
	def __init__(self, old_ai, num_turns = 5):
		self.old_ai = old_ai
		#number of turns remaining until AI script ends

		self.num_turns = num_turns

	def take_turn(self):
		if self.num_turns > 0:
			self.owner.creature.move(libtcod.random_get_int(0,-1, 1), libtcod.random_get_int(0, -1, 1), game_instance = GAME)
			self.num_turns -= 1
		else:
			self.owner.ai = self.old_ai
			GAME.game_message(self.owner.display_name + " pauses and turns back to face you.")

class ai_Chase:
	#a basic ai script which chases and tries to harm the player
	#add target selection and prioritizaiton later
	def take_turn(self):
		global GAME, FOV_MAP
		monster = self.owner

		target_actor = (ai_designate_targets(actor = monster))
		if target_actor == "no actors":
			self.owner.creature.move(libtcod.random_get_int(0,-1, 1), libtcod.random_get_int(0, -1, 1), game_instance = GAME)
			return

		else:
			#if (target.distance)[0] >= 2.0:		#no idea why this is a tuple lol
			if monster.distance_to(target_actor.actor[0]) >= 2.0:
				monster.move_towards(target_actor.actor[0], game_instance = GAME)

			elif target_actor.actor[0].creature.current_hp > 0:
				monster.creature.attack(target_actor.actor[0], GAME)

		monster.creature.local_fov = None
		monster.creature.proximate_hostiles = []
		monster.creature.proximate_actors = []

class ai_Flee:
	def take_turn(self):
		monster = self.owner
		target_actor = (ai_designate_targets(actor = monster))

		if target_actor == "no actors":
			monster.creature.move(libtcod.random_get_int(0,-1, 1), libtcod.random_get_int(0, -1, 1), game_instance = GAME)
			return

		else:		#no idea why this is a tuple lol
			monster.move_away(target_actor.actor[0], game_instance = GAME)

class ai_Townfolk_Wander:
	def take_turn(self):
		#print("Townfolk taking turn")
		self.owner.creature.move(libtcod.random_get_int(0,-1, 1), libtcod.random_get_int(0, -1, 1), game_instance = GAME)

class ai_Town_Guardsman_Patrol:
	def take_turn(self):
		monster = self.owner
		target_actor = (ai_designate_targets(actor = monster))
		#targ
		if target_actor == "no actors":
			self.owner.creature.move(libtcod.random_get_int(0,-1, 1), libtcod.random_get_int(0, -1, 1), game_instance = GAME)
			return

		else:		#no idea why this is a tuple lol
			if monster.distance_to(target_actor.actor[0]) >= 2.0:
				monster.move_towards(target_actor.actor[0])

			elif target_actor.actor[0].creature.current_hp > 0:
				monster.creature.attack(target_actor.actor[0])


class com_AI:
	def take_turn(self):
		self.owner.creature.move(libtcod.random_get_int(0,-1, 1), libtcod.random_get_int(0, -1, 1), game_instance = GAME)

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

class ai_Static:
	def take_turn(self):
		return

class ai_Player:
	def take_turn(self):
		return

#engage with fireballs at range then attack
class ai_Dragon:
	def take_turn(self):
		monster = self.owner

		target_actor = ai_designate_targets(actor = monster) #, actor_fov = 10)
		if target_actor == "no actors":
			return

		else:
			target_coords = target_actor.actor[0].x, target_actor.actor[0].y
			#move towards the player if far away (out of spell reach)		
			# move towards the player if far away 

			if monster.distance_to(target_actor.actor[0]) >= 8:
				self.owner.move_towards(target_actor.actor[0], game_instance = GAME)
			#if target is alive, attack
			elif (target_actor.actor[0].creature.current_hp) and (target_actor.actor[0].creature.current_hp > 0):
				#cast fireball
				if monster.distance_to(target_actor.actor[0]) > 3:
					#replace this function with the more flexible aoe_damage function
					#cast_fireball(caster = self.owner, T_damage_radius_range = (13, 3, 8))
					aoe_damage(caster = self.owner, damage_type = "fire", damage_to_deal = 13, target_range = 8, to_hit_radius = 2, 
						penetrate_walls = False, msg = "The dragon's fireball scorches everything it touches.")

				else: # if within blast radius, engage in melee
					if monster.distance_to(target_actor.actor[0]) < 2:
						monster.creature.attack(target_actor.actor[0], game_instance = GAME)

					if monster.distance_to(target_actor.actor[0]) < 3:
						self.owner.move_towards(target_actor.actor[0], game_instance = GAME)	


def death_monster(monster):
	if monster.is_invulnerable != True:
		#on death, monster stops moving
		GAME.game_message(monster.creature.name_instance + " is dead!", constants.COLOR_GRAY)
		if (monster.creature.noncorporeal == False): 
			monster.icon = settings.consumable_icon

		monster.creature = None
		monster.ai = None
		monster.static = True
		
		#determine what to leave behind
	else:
		GAME.game_message("Nice try. " + monster.creature.name_instance + " is invulnerable.", constants.COLOR_GRAY)

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
def map_random_walk(dungeon_x = constants.MAP_WIDTH, dungeon_y = constants.MAP_HEIGHT, walk_nodes = 8, steps_per_node = 800):
	#initialize empty map, flooded with unwalkable tiles
	new_map = [[structures.Tile(block_path = True, tile_icon = "#", transparent = True, 
				visible_tile_color = constants.COLOR_L_BROWN, explored_tile_color = constants.COLOR_BROWN) 
								for y in range(0, dungeon_x)]  
									for x in range (0, dungeon_y)]

	x_l_bound = int(dungeon_x * .35)
	x_u_bound = int(dungeon_x * .55)
	y_l_bound = int(dungeon_y * .45)
	y_u_bound = int(dungeon_y * .55)

	map_utilities.make_borders_undiggable(map_in = new_map, map_x = dungeon_x -1, map_y = dungeon_y -1)
	first_node = True

	#random walk that propagates out from assigned nodes
	for n in range(walk_nodes):
		point_x = random.randint(x_l_bound, x_u_bound)
		point_y = random.randint(y_l_bound, y_u_bound)

		for i in range(steps_per_node):
			r = helper_dice(4, -1)

			if r == 0: point_x += 1
			if r == 1: point_x -= 1
			if r == 2: point_y += 1
			if r == 3: point_y -= 1

			if point_x > 2 and point_x < (dungeon_x -2):
				if point_y > 2 and point_y < (dungeon_y - 2):
					new_map[point_x][point_y].block_path = False
					new_map[point_x][point_y].is_diggable = True
					new_map[point_x][point_y].transparent = True
					new_map[point_x][point_y].visible_tile_color = constants.COLOR_WHITE
					new_map[point_x][point_y].explored_tile_color = constants.COLOR_L_GRAY
					new_map[point_x][point_y].tile_icon = "."

	map_tryplace_stairs(map_in = new_map, map_x_in = dungeon_x -1, map_y_in = dungeon_y -1)
	map_place_objects_dungeon(map_in = new_map, map_x =  dungeon_x -1, map_y =  dungeon_y -1)
	distribute_equipment(num_attempts = 4, map_in = new_map, map_x = dungeon_x -1, map_y = dungeon_y -1)

	map_utilities.make_borders_undiggable(map_in = new_map, map_x = dungeon_x - 1, map_y = dungeon_y - 1)
	map_make_fov(new_map, fov_x = dungeon_x -1, fov_y = dungeon_y -1)

	return (new_map, dungeon_x, dungeon_y)

def map_create(dungeon_x = constants.MAP_WIDTH, dungeon_y = constants.MAP_HEIGHT, total_rooms = constants.MAP_MAX_NUM_ROOMS):
	#initialize empty map, flooded with unwalkable tiles
	new_map = [[structures.Tile(block_path = True, tile_icon = "#", transparent = True, 
				visible_tile_color = constants.COLOR_L_BROWN, explored_tile_color = constants.COLOR_BROWN) 
								for y in range(0, dungeon_x)]  
									for x in range (0, dungeon_y)]

	map_utilities.make_borders_undiggable(map_in = new_map, map_x = dungeon_x - 1, map_y = dungeon_y - 1)								
						
	# generate new room
	list_of_rooms = []
	num = 0
	for num in range(total_rooms):
		w = libtcod.random_get_int(0, constants.ROOM_MIN_WIDTH,  constants.ROOM_MAX_WIDTH)

		h = libtcod.random_get_int(0,constants.ROOM_MIN_HEIGHT, constants.ROOM_MAX_HEIGHT)

		x = libtcod.random_get_int(0, 2, dungeon_x - w - 2)
		y = libtcod.random_get_int(0, 2, dungeon_y - h - 2)

		#create room
		new_room = objects.Room((x, y), (w, h))
		failed = False

		#check for interference (overlapping with any others)
		for other_room in list_of_rooms:
			if other_room.intersect(new_room):
				failed = True
				break

		if not failed:
			#place room
			map_utilities.create_room(new_map, new_room)
			current_center = new_room.center
			center_x, center_y = new_room.center

			#put player in the first room
			if len(list_of_rooms) != 0:
				previous_center = list_of_rooms[-1].center
				map_utilities.create_tunnels(current_center, previous_center, new_map)

			list_of_rooms.append(new_room)	

	#create FOV map		
	map_make_fov(new_map)
	print("map creation finished")
	return (new_map, list_of_rooms, dungeon_x, dungeon_y)

def create_building(new_map, new_building, has_door = True):
	for x in range(new_building.x1, new_building.x2):
		for y in range(new_building.y1, new_building.y2):
			new_map[x][y].block_path = True
			new_map[x][y].transparent = False
			new_map[x][y].visible_tile_color = constants.COLOR_L_BROWN
			new_map[x][y].explored_tile_color = constants.COLOR_BROWN
			new_map[x][y].tile_icon = "#"

	if has_door:
		place_building_door(new_map, new_building)

def map_create_overworld():
	#initialize empty map, flooded with empty tiles
	new_map = [[structures.Tile(block_path = False, tile_icon = "~", transparent = True,
							visible_tile_color = constants.COLOR_BLUE, explored_tile_color = constants.COLOR_BLUE)
							 for y in range(0, constants.OVERWORLD_HEIGHT)]  
									for x in range (0, constants.OVERWORLD_WIDTH)]

	noise_scale = 0.1 
	bias = 130

	#generate land vs perlin noise

	for y in range(0, constants.OVERWORLD_HEIGHT):
		for x in range (0, constants.OVERWORLD_WIDTH):

			b_noise = random.randint(0, round((255 * noise_scale) + bias, 0) )

			new_map[x][y].tile_icon = "#"
			new_map[x][y].visible_tile_color = (0, 0, b_noise )
			new_map[x][y].explored_tile_color = (0, 0, b_noise )


def map_create_town():	#initialize empty map, flooded with empty tiles
	new_map = [[structures.Tile(block_path = False, tile_icon = ".", transparent = True, 
				visible_tile_color = constants.COLOR_WHITE, explored_tile_color = constants.COLOR_L_GRAY) 
									for y in range(0, constants.MAP_HEIGHT)]  
										for x in range (0, constants.MAP_WIDTH)]

	#create borders of town
	map_utilities.make_borders_undiggable(map_in = new_map, map_x = constants.MAP_WIDTH, map_y = constants.MAP_HEIGHT)
	
	# generate new buildings
	list_of_buildings = []
	num = 0
	#create random buildings
	for num in range(constants.MAP_MAX_NUM_ROOMS):
		w = libtcod.random_get_int(0, constants.KAZANY_BUILDING_MIN_WIDTH,  
										constants.KAZANY_BUILDING_MAX_WIDTH)
		h = libtcod.random_get_int(0,constants.KAZANY_BUILDING_MIN_HEIGHT, 
										constants.KAZANY_BUILDING_MAX_HEIGHT)

		x = libtcod.random_get_int(0, 8, constants.MAP_WIDTH - w - 8)

		y = libtcod.random_get_int(0, 8, constants.MAP_HEIGHT - h - 8)

		#create room
		new_building = objects.Building((x, y), (w, h))

		failed = False

		#check for interference (overlapping with any others)
		for other_building in list_of_buildings:
			if other_building.intersect(new_building):
				failed = True
				break

		if not failed:
			#place room
			create_building(new_map, new_building)
			current_center = new_building.center
			center_x, center_y = new_building.center

			if len(list_of_buildings) != 0:
				previous_center = list_of_buildings[-1].center

			list_of_buildings.append(new_building)

	distribute_equipment(num_attempts = 20, map_in = new_map)
	gen_trap((2,2))

	map_make_fov(new_map)
	return (new_map, list_of_buildings)



def map_create_house_interior(house_x = constants.HOUSE_INTERIOR_MIN_WIDTH, house_y = constants.HOUSE_INTERIOR_MIN_HEIGHT):
	#initialize empty map, flooded with empty tiles

	new_map = [[structures.Tile(False) for y in range(0, house_y)]  
									for x in range (0, house_x)]

	map_utilities.make_borders_undiggable(map_in = new_map, map_x = house_x, map_y = house_y)	

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
	#	print("Attempt #" + str(i) + " to to place player at " + str(x) + "," + str(y))

		if GAME.current_map[x][y].block_path == False:
			PLAYER.x, PLAYER.y = x, y
			 		
			break	

def map_tryplace_guard(map_x_in = constants.MAP_WIDTH, map_y_in = constants.MAP_HEIGHT):
	for i in range(1, 2000):
		
		x = random.randint(1, map_x_in - 2)
		y = random.randint(1, map_y_in - 2)

		if GAME.current_map[x][y].block_path == False:
			gen_town_guard((x, y))
			 	
			break
		break	

def map_tryplace_stairs(map_in, map_x_in = constants.MAP_WIDTH, map_y_in = constants.MAP_HEIGHT, in_key = None): 
	for i in range (0, 1000):
		x = random.randint(1, map_x_in - 2)
		y = random.randint(1, map_y_in - 2)
		#check if there is already an exit point at the given location
		#map_objects_at_coords
		if map_in[x][y].block_path == False: 
			gen_exit_point_stairs((x, y), downwards = True)
			break

def map_tryplace_shopkeeper(map_x_in = constants.MAP_WIDTH, map_y_in = constants.MAP_HEIGHT):
	for i in range(1, 2000):
		x = random.randint(1, map_x_in - 2)
		y = random.randint(1, map_y_in - 2)


def map_tryplace_monster(map_x_in = constants.MAP_WIDTH, map_y_in = constants.MAP_HEIGHT):
	for i in range(1, 2000):
		x = random.randint(1, map_x_in - 2)
		y = random.randint(1, map_y_in - 2)
		if GAME.current_map[x][y].block_path == False:
			gen_creature((x, y))
		break


def map_place_objects(room_list, is_first_map = None):
	for room in room_list:
		first_room = (room ==  room_list[0])
		second_room = (room ==  room_list[1])
		last_room = (room == room_list[-1])

		#put the player in the first room
		if first_room: 
			PLAYER.x, PLAYER.y = room.center
			gen_exit_point_stairs(room.center, downwards = False)	#create stairs back up to last map
	
		if last_room:
			gen_exit_point_stairs(room.center, downwards = True)
			
		#generated items and enemies
		x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1) 
		y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)
		
		
		x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1) 
		y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1) 

		gen_creature((x,y))
		distribute_equipment(num_attempts = 5, map_in = GAME.current_map)
		distribute_scrolls(num_attempts = 5, map_in = GAME.current_map)

def map_place_objects_town(building_list, is_first_map = False):
	PLAYER.x, PLAYER.y = (3, 3)

	map_tryplace_player()
			
	gen_exit_point_door((5, 4), target_type = "overworld")
	gen_exit_point_door((8, 10))
	#map_create_overworld()


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

def map_place_objects_dungeon(map_in = None, map_x = constants.MAP_WIDTH, map_y = constants.MAP_HEIGHT):
	#map_tryplace_stairs()
	print("Placeholder to place stuff in the dungeon.")
	successful_mob_spawns = 0

	for i in range (0, 30):
		x = libtcod.random_get_int(0, 1, map_x -1)
		y = libtcod.random_get_int(0, 1, map_y - 1)
		if map_in[x][y].block_path == False:
			gen_creature((x, y))
			successful_mob_spawns += 1

		print(str(successful_mob_spawns) + " hostile mobs spawned ")
	
			
	
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

	map_utilities.clear_tile(map_in, door_x_pos, door_y_pos)

	gen_exit_point_door(coords = (door_x_pos, door_y_pos), target_key = GAME.current_key)

	PLAYER.x = door_x_pos
	PLAYER.y = door_y_pos
	

def map_make_fov(incoming_map, fov_x = constants.MAP_WIDTH, fov_y = constants.MAP_HEIGHT):
	global FOV_MAP
	FOV_MAP = libtcod.map.Map(fov_x, fov_y)

	for y in range(int(fov_y)):
		for x in range(int(fov_x)):
			libtcod.map_set_properties(FOV_MAP, x, y, 
				not incoming_map[int(x)][int(y)].block_path, not incoming_map[int(x)][int(y)].block_path)

def map_make_local_fov(incoming_map, actor_in = None, fov_x = constants.MAP_WIDTH - 1, fov_y = constants.MAP_HEIGHT - 1):
	global GAME
	actor_in.creature.local_fov = libtcod.map.Map(fov_x, fov_y)

	for y in range(int(fov_y)):
		for x in range(int(fov_x)):
			libtcod.map_set_properties(actor_in.creature.local_fov, x, y, 
				not incoming_map[int(x)][int(y)].block_path, not incoming_map[int(x)][int(y)].block_path)

def map_calculate_fov():
	global FOV_CALCULATE, PLAYER
	if FOV_CALCULATE:
		FOV_CALCULATE = False
		libtcod.map_compute_fov(FOV_MAP, PLAYER.x, PLAYER.y, 
								constants.TORCH_RADIUS, constants.FOV_LIGHT_WALLS, constants.FOV_ALGO)




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


#drawing functions
def draw_game():
	global GAME
	global SURFACE_MAIN, PLAYER, SURFACE_WINDOW, SURFACE_BOTTOM_PANEL

	#clear the display surface
	SURFACE_WINDOW.fill(constants.COLOR_D_GRAY)
	SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
	SURFACE_MAP.fill(constants.COLOR_BLACK)
	SURFACE_BOTTOM_PANEL.fill(constants.COLOR_BLACK)

	CAMERA.update(follow_actor = PLAYER)
	#draw the map
	draw_map(GAME.current_map)

	#draw all objects in the game
	for obj in GAME.current_objects: obj.draw(map_surface = SURFACE_MAIN)

	SURFACE_MAIN.blit(SURFACE_MAP, (0, 0), CAMERA.rectangle)
					
	if settings.ENABLE_DEBUG == True: draw_debug()

	draw_messages()
	draw_stat_panel()

def draw_text(display_surface, text_to_display, font, coords, text_color, back_color = None, center = False):
    # get both the surface and rectangle of the desired message
    text_surf, text_rect = helper_text_objects(text_to_display, font, text_color, back_color)
    
    if not center: text_rect.topleft = coords

    else: text_rect.center = coords

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

	if SCREEN_STATUS.inventory_open:
		start_y = (int((constants.CAM_HEIGHT + 20) * .85))

		stats = ("Health = " + str(PLAYER.creature.current_hp) + "/" + str(PLAYER.creature.max_hp) + 
			#	", Damage / hit = " + str(PLAYER.creature.damage) +
			#	", vs Physical = " + str(PLAYER.creature.resist_physical) +
			#	", vs Fire = " + str(PLAYER.creature.resist_fire) + 
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





	SURFACE_MAIN.blit(projectile_surface, (ballistic_x * constants.CELL_WIDTH * 1 , ballistic_y * constants.CELL_HEIGHT * 1))
	#SURFACE_MAIN.blit(projectile_surface, (ballistic_x, ballistic_y))


	#	new_x = x * constants.CELL_WIDTH - 16
	#	new_y = y * constants.CELL_HEIGHT  -16


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
	x, y = misc_utils.get_map_dimensions(GAME.current_map)
	
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
				if map_to_draw[x][y].block_path == True: #draw wall
					draw_text(
						SURFACE_MAP, text_to_display = (map_to_draw[x][y].tile_icon), font = constants.FONT_RENDER_TEXT, 
						coords = (((x * constants.CELL_WIDTH) + 16), ((y * constants.CELL_HEIGHT)+ 16)), 
						text_color = map_to_draw[x][y].visible_tile_color, back_color = constants.COLOR_BLACK,
						center = True)
				else:
					#draw visible floor tiles
						draw_text(
						SURFACE_MAP, text_to_display = map_to_draw[x][y].tile_icon, font = constants.FONT_RENDER_TEXT, 
						coords = (((x * constants.CELL_WIDTH) + 16), ((y * constants.CELL_HEIGHT)+ 16)), 
						text_color = map_to_draw[x][y].visible_tile_color, back_color = constants.COLOR_BLACK,
						center = True)	

			#tiles that have already been rendered but are no longer visible
			else:
				#draw explored but not visible wall tiles
				if map_to_draw[x][y].explored:
					if map_to_draw[x][y].block_path == True:
						#draw wall
						draw_text(
							SURFACE_MAP, text_to_display = map_to_draw[x][y].tile_icon, font = constants.FONT_RENDER_TEXT, 
							coords = (((x * constants.CELL_WIDTH) + 16), ((y * constants.CELL_HEIGHT) + 16)), 
							text_color = map_to_draw[x][y].explored_tile_color, back_color = constants.COLOR_BLACK,
							center = True)
					else:
						#draw explored floor but not visible wall tiles
						draw_text(
							SURFACE_MAP, text_to_display = map_to_draw[x][y].tile_icon, font = constants.FONT_RENDER_TEXT, 
							coords = (((x * constants.CELL_WIDTH) + 16), ((y * constants.CELL_HEIGHT) + 16)), 
							text_color = map_to_draw[x][y].explored_tile_color, back_color = constants.COLOR_BLACK,
							center = True)

###############################################################################################################
#magic

def cast_heal(caster, value):
	if caster.creature.current_hp == caster.creature.max_hp:
		GAME.game_message(caster.creature.name_instance + " is already at full health.")
		return "cancelled"

	else:
		GAME.game_message(caster.creature.name_instance + " healed for " + str(value) + " health.")
		caster.creature.heal(value)

		if caster.creature.current_hp >= caster.creature.max_hp:
			GAME.game_message(caster.creature.name_instance + " is now at full health.")
		
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
				draw_projectile((x * constants.CELL_HEIGHT), (y * constants.CELL_WIDTH), constants.COLOR_L_BLUE)
			target = map_check_for_creatures(x, y)
			if target: # and i != 0:
				GAME.game_message(caster.creature.name_instance + " casts Alenko-Kharyalov Effect.")
				#check if spell uselessly hits wall
				target.creature.take_damage(damage, attacker = caster)

				GAME.game_message("You smell ozone.")

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
		GAME.game_message(caster.creature.name_instance + " casts Conflagration.")#" casts Alenko-Kharyalov Conflagration.")
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

				if damage > 0:
					creature_to_damage.creature.take_damage(damage, attacker = caster)
				else:
					if creature_to_damage.creature.name:
						GAME.game_message(creature_to_damage.creature.name + " is unfazed.")

				if creature_to_damage is not PLAYER:
					creature_hit = True

		if creature_hit:
			GAME.game_message("You smell the repugnant stench of burning flesh.", constants.COLOR_RED)

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
			GAME.game_message(target.creature.name_instance + " stumbles around in circles.", constants.COLOR_GREEN)

# i.e. fireball
def aoe_damage(caster, damage_type = "fire", damage_to_deal = 10, target_range = 15, to_hit_radius = 3, penetrate_walls = False, msg = "The spell hits the target."):
	#definitions, change later

	caster_location = (caster.x, caster.y)
	#TODO get target tile
	if caster == PLAYER:
		point_selected = menu_tile_select(coords_origin = caster_location, max_range = target_range,
			 penetrate_walls = False, 
			 pierce_creature = False, 
			 radius = to_hit_radius)
	else:
		point_selected = PLAYER.x, PLAYER.y

	if point_selected:
		GAME.game_message(caster.creature.name_instance + " casts Conflagration.")
		#get sequence of tiles
		tiles_to_damage = map_find_radius(point_selected, to_hit_radius)
		creature_hit = False

		#damage all creatures in tiles
		for (x, y) in tiles_to_damage:
			#add visual feedback to fireball, maybe even adding a trail to its destination later
			#draw_explosion(local_radius, PLAYER.x, PLAYER.y, constants.COLOR_ORANGE)

			creature_to_damage = components.map_check_for_creatures(x, y, game_instance = GAME)
			if creature_to_damage: 
				#allow flexibility for damage types later
				#damage_to_deal -= creature_to_damage.creature.resist_fire
				#damage_to_deal -= creature_to_damage.creature.net_resistances[damage_type]
				damage_to_deal -= creature_to_damage.creature.net_resistances["fire"]

				if damage_to_deal > 0:
					creature_to_damage.creature.take_damage(damage_to_deal, attacker = caster)
				else:
					if creature_to_damage.creature.name_instance:
						GAME.game_message(creature_to_damage.creature.name_instance + " is unfazed.")

				if creature_to_damage is not PLAYER:
					creature_hit = True

		if creature_hit:
			GAME.game_message(msg, constants.COLOR_RED)

#i.e. lightning
def beam_damage(caster, damage_type = "fire", damage_to_deal = 10, target_range = 15, penetrate_walls = False, msg = "The spell hits the target."):


	player_location = (PLAYER.x, PLAYER.y)

	# prompt player for a tile
	point_selected = menu_tile_select(coords_origin = player_location, 
		max_range = target_range, penetrate_walls = False)

	if point_selected:
	# convert that tile into a list of coordinates, A -> B
		list_of_tiles = map_find_line(player_location, point_selected)

		#cycle through list and damage everything found
		for i, (x, y) in enumerate(list_of_tiles):
			if settings.RENDER_BALLISTICS:

				print ("Rendering tile at " + str(x) + ", " + str(y))
				draw_projectile((x), (y), constants.COLOR_L_BLUE)
				print("I like turtles")
			target = map_check_for_creatures(x, y)
			print ("Target at " + str(x) + ", " + str(y))
			if target: # and i != 0:
				GAME.game_message(caster.creature.name_instance + " casts Alenko-Kharyalov Effect.")
				#check if spell uselessly hits wall
				target.creature.take_damage(damage_to_deal, attacker = caster)

				GAME.game_message(msg, constants.COLOR_RED)


#def singular_effect():
#	caster, damage_type = "fire", damage_to_deal = 10, target_range = 15, penetrate_walls = False, msg = "The spell hits the target."):


#def area_affect():

def fire_projectile(source, ranged_weapon, target, ammo_count):
	if (ammo_count > 0 and target and ranged_weapon):
		print("Ranged attack placeholder..")

################################################################################
#UI stuff
class ui_Button:
	def __init__(self, surface, button_text, size, center_coords, font = constants.FONT_MESSAGE_TEXT,
					color_box_hovered = constants.COLOR_GRAY, color_box_default = constants.COLOR_L_GRAY,
					color_text_hovered = constants.COLOR_BLACK, color_text_default = constants.COLOR_BLACK):

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
			if mouse_clicked: return True
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

###############################################################################################################
#helper functions

def helper_text_objects(incoming_text, incoming_font, incoming_color, incoming_bg):
    # if there is a background color, render with that.
    if incoming_bg:
        Text_surface = incoming_font.render(incoming_text, False, incoming_color, incoming_bg)

    else:  # otherwise, render without a background.
        Text_surface = incoming_font.render(incoming_text, False, incoming_color)

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

#gets the dimensions of an array, particularly maps


def ynq_prompt(): #prompt the player to select Yes, No or Quit
	print("Placeholder.")
###############################################################################################################
#menus

def open_door_prompt(in_event):

	global SURFACE_MAIN, PLAYER
	prompt_close = False

	#hold down O and press a numpad direction, or release O to cancel
	while not prompt_close:
		#get keypresses and stuff
		draw_text(SURFACE_MAIN, 
			"Open door in which direction?", 
			constants.FONT_MESSAGE_TEXT, (100, 100), constants.COLOR_WHITE, back_color = constants.COLOR_BLACK, 
			center = False)

		for event in pygame.event.get():
			if event.type == pygame.QUIT: pygame.quit()

			if event.type == pygame.KEYDOWN:	
				if event.key in constants.NUMPAD_KEYS:
					print("SHOULD have called the attempt open function")
					adjusted = game_direction_prompt(event_in = in_event)
					#adjusted = attempt_to_open_door(event_in = in_event)
					print(str(adjusted))
					if adjusted != (0,0):
						to_open_x = PLAYER.x + adjusted.x
						to_open_y = PLAYER.y + adjusted.y
					prompt_close = True


			if event.type == pygame.KEYUP:
				if event.key == pygame.K_o:
			
					prompt_close = True
					GAME.game_message("You decide not to open anything.")
				


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

		else: SURFACE_MAIN.fill(constants.COLOR_BLACK)   

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
	adjusted_coords = structures.Direction()
	to_open_coords = structrues.Direction()

	adjusted_coords.x, adjusted_coords.y = game_direction_prompt(event_in, not_in_menu = False)
	#print(str(adjusted_coords.x) + ", " + str(adjusted_coords.y))

	to_open_coords.x = start_x + adjusted_coords.x
	to_open_coords.y = start_y + adjusted_coords.y

	list_of_objects = map_objects_at_coords(to_open_coords.x, to_open_coords.y)
	for obj in list_of_objects:
		if obj.doorcom:
			obj.doorcom.interact()
			print("obj.door.interact() called")
		else:
			GAME.game_message("There is nothing to open there.")
			print("obj.door.interact() not called")



def draw_paragraph(surface, text, color, rect, font, aa=False, bkg=None, indent = True):
    rect = pygame.Rect(rect)
    y = rect.top
    lineSpacing = -2

    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1

        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break

        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # if we've wrapped the text, then adjust the wrap to the last word      
        if i < len(text): 
            i = text.rfind(" ", 0, i) + 1

        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        surface.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing

        # remove the text we just blitted
        text = text[i:]
        #print(str(i))

    return text


#really messy, clean up later
def menu_inventory(owning_actor = None):
	menu_close = False
	window_width = constants.CAM_WIDTH
	window_height = constants.CAM_HEIGHT
	side_panel_width = 800
	side_panel_height = 850
	menu_width = 600
	menu_height = 850

	menu_x = (window_width * 1/ 2) - (side_panel_width )
	menu_y = (window_height * 1.02 / 2.3) - (menu_height / 2)

	#panel for stats and description
	panel_x = (window_width * 1.6/ 2) - (menu_width / 2)
	panel_y = (window_height * 1.02 / 2.3) - (side_panel_height / 2)

	menu_text_font = constants.FONT_MESSAGE_TEXT
	menu_text_height = helper_text_height(menu_text_font)

	local_inventory_surface = pygame.Surface((menu_width, menu_height))
	side_panel_surface = pygame.Surface((side_panel_width, side_panel_height))
	
	while not menu_close:
		#clear the menu by wiping it black
		local_inventory_surface.fill((20, 20, 20, 120))
		side_panel_surface.fill(constants.COLOR_D_GRAY)

		print_list = [obj.display_name for obj in PLAYER.container.inventory]
		events_list = pygame.event.get()

		mouse_x, mouse_y = pygame.mouse.get_pos()
		delta_x = mouse_x - menu_x
		delta_y = mouse_y - menu_y

		mouse_in_window = (delta_x > 0 and delta_y > 0 and delta_x < menu_width and delta_y < menu_height)

		#replace conversation -> int function later
		mouse_line_selection = int(delta_y / menu_text_height)

		for event in events_list:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_i:
					menu_close = True

		show_description = False			

		#draw every line in the list
		for line, (name) in enumerate(print_list):
			if line == mouse_line_selection and mouse_in_window == True:
				draw_text(local_inventory_surface,
					name,
					menu_text_font,
					(settings.MENU_X_OFFSET, settings.MENU_Y_OFFSET + (line * menu_text_height)), constants.COLOR_WHITE, constants.COLOR_GRAY)
				show_description = True

			else:
				draw_text(local_inventory_surface,
					name, menu_text_font,
					(settings.MENU_X_OFFSET, settings.MENU_Y_OFFSET + (line * menu_text_height)), constants.COLOR_WHITE)

			if show_description:
				i = 0
				description_text = str(PLAYER.container.inventory[mouse_line_selection].item.description)
				#reset panel
				side_panel_surface.fill(constants.COLOR_D_GRAY)
				#for paragraph in description_text:
				misc_utils.draw_wrapped_text(side_panel_surface, text = ("     " + str(description_text)), 
							color = constants.COLOR_WHITE, rect = ((10,  10), (600, 1000)), 
							font = constants.FONT_MESSAGE_TEXT, aa= False, bkg=None)
				#	i += 0

				#new method to print w/ paragraphs


		for event in events_list:
			if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
				if len(PLAYER.container.inventory) > 0:
					#check if item is equipment, and, if so, unequip it
					try:
						PLAYER.container.inventory[mouse_line_selection].equipment.unequip()
			
					except:
						print("Meh.")

					#drop selected item
					PLAYER.container.inventory[mouse_line_selection].item.drop(PLAYER.x, PLAYER.y, game_instance = GAME)
					if settings.CLOSE_AFTER_DROP:
						return "no-action"

			if event.type == pygame.MOUSEBUTTONDOWN:
				if (event.button == 1):
					if (mouse_in_window and 
						mouse_line_selection <= len(print_list) - 1):
						PLAYER.container.inventory[mouse_line_selection].item.use(PLAYER, game_instance = GAME)
						actor_utilities.update_stats(actor_to_update = PLAYER)

		#render game 
		draw_game()
		SURFACE_MAIN.blit(side_panel_surface, (int(panel_x), int(panel_y)))
		SURFACE_MAIN.blit(local_inventory_surface, (int(menu_x), int(menu_y)))

				#draw buttons	
		button_height = 80
		button_width = 100
		equipment_button = ui_Button(local_inventory_surface, "Equipment", (1, 10),(100, 100))
			
		CLOCK.tick(constants.GAME_FPS)
		pygame.display.update()

def menu_tile_select(coords_origin = None, max_range = None, radius = None, penetrate_walls = True, pierce_creature = True):
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
				if not pierce_creature and components.map_check_for_creatures(x, y, gameinstance = GAME):		#stop at creature
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
			CAMERA.update(follow_actor = PLAYER)
			draw_map(GAME.current_map)
			for obj in GAME.current_objects:
				#potentially replace this global later?
				obj.draw(map_surface = SURFACE_MAIN)

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
					draw_tile_rect(coords = (tile_x, tile_y), tile_color = constants.COLOR_ORANGE, tile_alpha = 150)

			#these numbers are the starting offset, for left/top padding
			SURFACE_MAIN.blit(SURFACE_MAP, (0, 0), CAMERA.rectangle)				

			if settings.ENABLE_DEBUG == True:
				draw_debug()

			draw_messages()
			#update display
			pygame.display.flip()
			CLOCK.tick(constants.GAME_FPS)

##########################################################################################################
#generators

def distribute_equipment(num_attempts = 10, map_in = None, map_x = constants.MAP_WIDTH, map_y = constants.MAP_HEIGHT):
	global GAME_EQUIPMENT_POOL

	for i in range (num_attempts):
		x = libtcod.random_get_int(0, 1, map_x - 1)
		y = libtcod.random_get_int(0, 1, map_y - 1)
		if map_in[x][y].block_path == False:
			gen_equipment((x, y))

def distribute_scrolls(num_attempts = 100, map_in = None, map_x = constants.MAP_WIDTH, map_y = constants.MAP_HEIGHT):
	global GAME_SCROLL_POOL

	for i in range (num_attempts):
		x = libtcod.random_get_int(0, 1, map_x - 1)
		y = libtcod.random_get_int(0, 1, map_y - 1)
		if map_in[x][y].block_path == False:
			gen_scroll((x, y))

def gen_equipment(coords):
	print("Placing equipment")
	global GAME_EQUIPMENT_POOL, GAME
	selected_equipment = random.choice(GAME_EQUIPMENT_POOL)

	dam_list = 	selected_equipment['bonus_damages']
	res_list = 	selected_equipment ['bonus_resistances']

	x, y = coords
	equipment_com = components.EquipmentComponent(slot = selected_equipment['slot'], name = selected_equipment['pickup_name'],
					dam_bonus = dam_list, res_bonus = res_list)

	return_object = obj_Actor(x, y, selected_equipment['name'],
					icon = selected_equipment['icon'], 
					icon_color = (selected_equipment['icon_r'],selected_equipment['icon_g'], selected_equipment['icon_b']),
					equipment = equipment_com, static = selected_equipment['static'])
	
	GAME.current_objects.append(return_object)

def gen_creature_by_id(coords, id = ""):
	print("Placeholder")

def gen_creature(coords):
	global GAME_CREATURE_POOL, GAME
	selected_creature = random.choice(GAME_CREATURE_POOL)
	x, y = coords

	ai_com = (assign_ai_script(creature_in = selected_creature))

	if (selected_creature['noncorporeal'] == False):
		item_description = []
		item_com = components.ItemComponent(value = selected_creature['carcass_heal_amount'], use_function = cast_heal, 
			description = selected_creature['description'],

			name = selected_creature['carcass_name'])	
	else: item_com = None

	dam_list = 	selected_creature['base_damages']
	res_list = 	selected_creature['base_resistances']

	creature_com = components.Creature_Component(selected_creature['creature_name'], death_function = death_monster,
								hp = selected_creature['base_hp'],
								xp_on_death = selected_creature['xp_on_death'],

								base_dodge = selected_creature['base_dodge'], 
								base_accuracy = selected_creature['base_accuracy'],
								base_crit_chance = selected_creature['base_crit_chance'],
								base_crit_mult = selected_creature['base_crit_mult'],

								base_damages = dam_list, base_resistances = res_list,
								net_damages = dam_list, net_resistances = res_list
									
	) 
	#print(str(selected_creature['base_resistances']))

	allegiance_com = components.AllegianceComponent(category = str(selected_creature['allegiance_category']),
								hostile_list = ['wild', 'player', 'townfolk', 'guardsman'],
								docile = selected_creature['docile'])

	#name of item when picked up
	return_object = obj_Actor(x, y, selected_creature['creature_name'], 
		creature = creature_com, ai = ai_com, item = item_com, icon = selected_creature['actor_icon'], 
		icon_color = (selected_creature['icon_r'], selected_creature['icon_g'], selected_creature['icon_b']),
		allegiance_com = allegiance_com)

	GAME.current_objects.append(return_object)

def gen_town_guard(coords):
	x, y = coords

	dam_list = 	[{"fire":4,"electricity":0,"poison":0,"frost":9,"magic":0,
				"ballistic":0, "piercing":0, "bludgeoning":5, "slashing":0, "eldritch":0}]

	res_list = 	[{"fire":3,"electricity":3,"poison":3,"frost":3,"magic":3,
				"ballistic":3, "piercing":3, "bludgeoning":3, "slashing":3, "eldritch":3}]

	creature_com = components.Creature_Component(name_instance = "Town Guard",
								hp = 37, #player's creature component name
								death_function = death_monster,
								noncorporeal = False,
								base_damages = dam_list, base_resistances = res_list,
								net_damages = dam_list, net_resistances = res_list)

	ai_com = ai_Town_Guardsman_Patrol()
	allegiance_com = components.AllegianceComponent(category = "guardsman", hostile_list = ['wild', 'eldritch', 'draconic'])
	

	#assign (assume lol) gender and create a name accordingly
	creature_com.gender = helper_dice(upper_bound = 2, bias = -1)
	creature_com.name_instance = ("guardsman " + assign_random_name(gender_in = creature_com.gender))

	npc = obj_Actor(x, y, "Some random person.",  
						creature = creature_com,
						ai = ai_com,
						icon = " @ ", icon_color = constants.COLOR_GRAY,
						allegiance_com = allegiance_com,
						)

	GAME.current_objects.append(npc)


def gen_shopkeeper():
	global GAME
	ai_com = ai_Townfolk_Wander()

	creature_com = components.Creature_Component("shopkeeper")
	print("Hi")



def gen_scroll(coords):
	global GAME, GAME_SCROLL_POOL
	x, y = coords
	selected_scroll = random.choice(GAME_SCROLL_POOL)

	damage = helper_dice(5, 6)
	m_range = 8

	if selected_scroll['attack_type'] == "aoe":
		item_com = components.ItemComponent(use_function = aoe_damage,
						value = (damage, m_range),
			 			name = selected_scroll['scroll_name'])

	elif selected_scroll['attack_type'] == "beam":
		item_com = components.ItemComponent(use_function = beam_damage,
						value = (damage, m_range),
						name = selected_scroll['scroll_name'])


	return_object = obj_Actor(x, y, selected_scroll['scroll_name'], item = item_com, 
							icon = selected_scroll['icon'], icon_color = (selected_scroll['icon_r'], selected_scroll['icon_g'], selected_scroll['icon_b']))

	GAME.current_objects.append(return_object)


def assign_ai_script(creature_in = None):
	if str(creature_in['ai_script_type'])== "dragon_fireball":
		return ai_Dragon()

	elif str(creature_in['ai_script_type']) == "flee":
		return ai_Flee()
	else: 
		return ai_Chase()

def gen_tree(coords, fruit = "None"):
	x, y = coords
 
	ai_com = ai_Static()

	#name of item when picked up
	tree = obj_Actor(x, y, "an oak tree",
		ai = ai_com, #item = item_com,
		icon = settings.tree_icon, icon_color = constants.COLOR_GREEN, static = True)

	GAME.current_objects.append(tree)

#player
def gen_player(coords):
	global PLAYER, PLAYER_NAME
	x, y = coords

	dam_list = {"fire":0,"electricity":0,"poison":0,"frost":0,"magic":0,
				"ballistic":0, "piercing":0, "bludgeoning":5, "slashing":0, "eldritch":0}

	res_list = {"fire":3,"electricity":3,"poison":3,"frost":3,"magic":3,
				"ballistic":3, "piercing":3, "bludgeoning":3, "slashing":3, "eldritch":3}


	container_com = components.ContainerComponent()
	creature_com = components.Creature_Component(PLAYER_NAME,
								hp = 100, #player's creature component name
								death_function = death_player,
								noncorporeal = False,
								base_accuracy = 90, base_dodge = 30,
								base_crit_chance = 5, base_crit_mult = 1.5,
								base_damages = dam_list, base_resistances = res_list,
								net_damages = dam_list, net_resistances = res_list
								
								)

	allegiance_com = components.AllegianceComponent(category = "player", 
					hostile_list = ["eldritch", "wild", "draconic", "townfolk"],
					docile = False
					)
	

	PLAYER = obj_Actor(x, y, "Player",  
						creature = creature_com,
						container = container_com,
						icon = " @ ", icon_color = constants.COLOR_WHITE,
						allegiance_com = allegiance_com
						)

	GAME.current_objects.append(PLAYER)
	
def gen_town_folk(coords):
	x, y = coords

	base_dam_list = {'fire':0,'electricity':0,'poison':0,'frost':0,'magic':0,
				'ballistic':0, 'piercing':0, 'bludgeoning':5, 'slashing':0, 'eldritch':0}

	base_res_list = {'fire':3,'electricity':3,'poison':3,'frost':3,'magic':3,
				'ballistic':3, 'piercing':3, 'bludgeoning':3, 'slashing':3, 'eldritch':3}

	dam_list = base_dam_list
	res_list = base_res_list

	container_com = components.ContainerComponent()
	creature_com = components.Creature_Component(name_instance = "Townfolk",
								hp = 10, #player's creature component name
								death_function = death_monster,
								noncorporeal = False,
								base_damages = dam_list, base_resistances = res_list,
								net_damages = dam_list, net_resistances = res_list)

	ai_com = ai_Townfolk_Wander()
	allegiance_com = components.AllegianceComponent(category = "townfolk")

	#assign (assume lol) gender and create a name accordingly
	creature_com.gender = helper_dice(upper_bound = 2, bias = -1)
	creature_com.name_instance = assign_random_name(gender_in = creature_com.gender)

	npc = obj_Actor(x, y, "Some random person.",  
						creature = creature_com,
						container = container_com,
						icon = " @ ", icon_color = constants.COLOR_L_GRAY,
						ai = ai_com,
						allegiance_com = allegiance_com,
						)

	GAME.current_objects.append(npc)

#M:0, F:1, N:0
def assign_random_name(gender_in = 0):
	global GAME_SURNAME_POOL, GAME_MALNAME_POOL, GAME_FEMNAME_POOL
	print(str(gender_in))
	if gender_in == 0:
		firstname = random.choice(GAME_MALNAME_POOL)['firstname']
	#if gender_in == 1:
	else:
		firstname = random.choice(GAME_FEMNAME_POOL)['firstname']

	lastname = (random.choice(GAME_SURNAME_POOL))['surname']
	return(str(firstname) + " " + str(lastname))



def gen_exit_point_stairs(coords, downwards, target_type = None):
	x, y = coords
	
	#randomly choose a type out of a dungeon or a cave
	if target_type == None:
		i = helper_dice(10)
		if i <= 7: map_type = "cave"
		elif i <= 10: map_type = "dungeon"
	else:
		map_type = target_type
	
	exit_point_com = components.Exit_Point_Component(require_input = True, target_map_type = map_type)


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

	exit_point_com = components.Exit_Point_Component(require_input = True, target_map_type = map_type, next_map_key = target_key)
	door_com = components.Door_Component(is_destructable = True, is_locked = locked_by_default, is_closed = closed_by_default)
	
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

def place_building_door(new_map, new_building):
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
	new_map[door_x_pos][door_y_pos].is_diggable = False
	new_map[door_x_pos][door_y_pos].transparent = True
	new_map[door_x_pos][door_y_pos].visible_tile_color = constants.COLOR_WHITE
	new_map[door_x_pos][door_y_pos].explored_tile_color = constants.COLOR_L_GRAY
	new_map[door_x_pos][door_y_pos].tile_icon = "."

	gen_exit_point_door((door_x_pos, door_y_pos), target_type = "house")

#basic trap which damages whatever steps on it
def gen_trap(coords):
	x, y = coords
	#create the player

	trapcom = components.Trap_Component(trap_effect = "fire_trap", is_active = True, is_visible = True, disarm_difficulty = 1)

	trap = obj_Actor(x, y, "Fire trap",  
						trap_com = trapcom,
						icon = " + ", icon_color = constants.COLOR_WHITE
						)
	

	GAME.current_objects.append(trap)


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
		
		if player_action != "no-action":
			for obj in GAME.current_objects:
				if obj.ai:
					if obj.ai_active: 
						obj.ai.take_turn()

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
		if event.type == pygame.QUIT: return "QUIT"	

		if event.type == pygame.KEYDOWN:
			move_coords = structures.Direction()
			move_coords.x, move_coords.y = game_direction_prompt(event_in = event)
			if (move_coords.x,  move_coords.y) != (0, 0):
				PLAYER.creature.move(move_coords.x, move_coords.y, game_instance = GAME)

			#pop up menu if there are multiple objects at the tile?
			if event.key == pygame.K_COMMA:
				objects_at_player = components.map_objects_at_coords(PLAYER.x, PLAYER.y, gameinstance = GAME)
				for obj in objects_at_player:
					if obj.item:
						obj.item.pick_up(PLAYER, game_instance = GAME)
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
					#is this second return even necessary? idk anymore
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

			if event.key == pygame.K_q:
				x, y = menu_tile_select(coords_origin = None, max_range = None, 
					radius = None, penetrate_walls = True, pierce_creature = True)

				components.map_tile_query(x, y, accept_nothing = True, distant_query = True, game_instance = GAME)

	
			#key L, turn on tile selection. change later as needed
			if MOD_KEY and event.key == pygame.K_PERIOD:
				print("Stair/portal key pressed")
				#reuse this kind of thing later 		
				list_of_objects = components.map_objects_at_coords(PLAYER.x, PLAYER.y, gameinstance = GAME)
				for obj in list_of_objects:
					if obj.exit_point:
						obj.exit_point.use(game_instance = GAME)
						return "player-moved"
			return "player-moved"
	return "no-action"

def game_direction_prompt(event_in, not_in_menu = True):
	#return a direction picked from using the numpad, used for moving, firing projectiles, or interacting with doors
	target_coords = structures.Direction(x = 0, y = 0)
	target_coords = (0, 0)

	while not_in_menu:
		if event_in.key == pygame.K_KP1:
			target_coords = (-1, 1)
			print("KP1")
			
		elif event_in.key == pygame.K_KP2:# or pygame.K_DOWN:
			target_coords = (0, 1)
			print("KP2/KD")
			
		elif event_in.key == pygame.K_KP3:
			target_coords = (1, 1)
			print("KP3")
			
		elif event_in.key == pygame.K_KP4: # or pygame.K_LEFT:
			target_coords = (-1, 0)
			print("KP4/KL")
			
		elif event_in.key == pygame.K_KP5: #this one does literally nothing, just kinda chillin' here till I feel like using it
			target_coords = (0, 0)
			print("KP5")
			
		elif event_in.key == pygame.K_KP6: # or pygame.K_RIGHT:
			target_coords = (1, 0)
			print("KP6/KR")
			
		elif event_in.key == pygame.K_KP7:
			target_coords = (-1, -1)
			print("KP7")

		elif event_in.key == pygame.K_KP8: # or pygame.K_UP:
			target_coords = (0, -1)
			print("KP8/KU")
			
		elif event_in.key == pygame.K_KP9:
			target_coords = (1, -1)
			print("KP9")
		not_in_menu = False
		return target_coords




def game_new():
	global GAME, PLAYER_NAME
	#start a new game and map, and player with nonsense coords to be placed elsewhere
	PLAYER_NAME = helper_text_prompt(True)	#prompt the player for a name

	#gen_player((0,0))
	
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
			#game_json_loader()

	map_make_fov(GAME.current_map)

def game_json_loader():
	with open('equipment.json') as equip: equipment_archive = json.load(equip)
	with open('actors.json') as actor: actor_archive = json.load(actor)
	with open('scrolls.json') as scroll: scroll_archive = json.load(scroll)
	with open('surnames.json') as surname: surname_archive = json.load(surname)
	with open('male_names.json') as malname: malname_archive = json.load(malname)
	with open('female_names.json') as femname: femname_archive = json.load(femname)

	global GAME_EQUIPMENT_POOL, GAME_CREATURE_POOL, GAME_SCROLL_POOL, GAME_SURNAME_POOL, GAME_MALNAME_POOL, GAME_FEMNAME_POOL
	GAME_EQUIPMENT_POOL = []
	GAME_CREATURE_POOL = []
	GAME_SCROLL_POOL = []
	GAME_SURNAME_POOL = []
	GAME_MALNAME_POOL = []
	GAME_FEMNAME_POOL = []

	for item in equipment_archive['equipmentlist']:GAME_EQUIPMENT_POOL.append(item)
	for actor in actor_archive['actorlist']:GAME_CREATURE_POOL.append(actor)
	for scroll in scroll_archive['scrollslist']:GAME_SCROLL_POOL.append(scroll)
	for surname in surname_archive['surnameslist']:GAME_SURNAME_POOL.append(surname)
	for malname in malname_archive['malenameslist']:GAME_MALNAME_POOL.append(malname)
	for femname in femname_archive['femalenameslist']:GAME_FEMNAME_POOL.append(femname)


#'''initializing the main window and pygame'''
def game_initialize():
	global SURFACE_MAIN, SURFACE_MAP, FOV_CALCULATE, GAME
	global CAMERA, PLAYER, PLAYER_NAME, SCREEN_STATUS, CLOCK
	global DUNGEON_DEPTH, SURFACE_WINDOW, SURFACE_BOTTOM_PANEL


	pygame.init()
	PLAYER_NAME = "Bob the Guy"


	#init_flags = ((int(constants.CAM_WIDTH * 1), int(constants.CAM_HEIGHT * 1)) #| pygame.OPENGL | pygame.FULLSCREEN)



	print("Pygame 2.whatever actually working lol.")

	SCREEN_STATUS = structures.ScreenStatus()

	if constants.PermitKeyHolding == True:
		pygame.key.set_repeat(constants.KeyDownDelay, constants.KeyRepeatDelay)

	#create the rendered window
	SURFACE_WINDOW = pygame.display.set_mode((int(constants.CAM_WIDTH * 1), int(constants.CAM_HEIGHT * 1)))

	SURFACE_MAIN = pygame.display.set_mode(((constants.CAM_WIDTH, constants.CAM_HEIGHT)))

	SURFACE_MAP = pygame.Surface((constants.MAP_WIDTH * constants.CELL_WIDTH,
									constants.MAP_HEIGHT * constants.CELL_HEIGHT))	


	SURFACE_BOTTOM_PANEL = pygame.display.set_mode((int(constants.CAM_WIDTH * 1), int(constants.CAM_HEIGHT * 1)))


	#create GAME object to store game state
	GAME = obj_Game()

	gen_player((0,0))
	CAMERA = objects.Camera(follow_actor = PLAYER)

	
	game_json_loader()

	CLOCK = pygame.time.Clock()
	FOV_CALCULATE = True



if __name__ == '__main__':
	menu_main()
	