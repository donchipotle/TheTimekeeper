import actor_utilities
import structures
import random
import constants

class AllegianceComponent:
	def __init__(self, category = "undefined", protect_list = "", hostile_list = [], docile = True):
		#list of targets whose attackers the npc will attack
		self.category = category,
		self.protect_list = protect_list,
		#list of categories which the npc will not
		self.hostile_list = hostile_list,
		#npc has not yet been provoked into attacking
		self.docile = docile

class ItemComponent:
	def __init__(self, weight = 0.0, volume = 0.0, name = "foo", category = "misc", 
		use_function = None, value = None, slot = None, 
		description = "There is no description for this item."):
		self.weight = weight
		self.volume = volume
		self.name = name
		self.value = value
		self.use_function = use_function
		self.description = description

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
		else: print("This item cannot be equipped.")
		
		if self.use_function:
			result = self.use_function(self.current_container.owner, self.value)
		
			if result is not None: print("use_function failed")
			else:
				self.current_container.inventory.remove(self.owner)

class ContainerComponent:
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


class ItemComponent:
	def __init__(self, weight = 0.0, volume = 0.0, name = "foo", category = "misc", 
		use_function = None, value = None, slot = None, 
		description = "There is no description for this item."):
		self.weight = weight
		self.volume = volume
		self.name = name
		self.value = value
		self.use_function = use_function
		self.description = description

		#pick up this item
	def pick_up(self, actor, game_instance = None):
		if actor.container:
			if self.owner.equipment: 
				item_name = self.owner.equipment.name

			elif self.name: 
				item_name = self.owner.item.name
			elif self.name_object: 

				item_name = self.name_object
			game_instance.game_message(actor.creature.name + " picked up " + item_name + ".")

			actor.container.inventory.append(self.owner)
			game_instance.current_objects.remove(self.owner)
			self.current_container = actor.container
		
	def drop(self, new_x, new_y, game_instance = None):
		game_instance.current_objects.append(self.owner)
		self.current_container.inventory.remove(self.owner)
		#place object at the coords at which it was dropped
		self.owner.x = new_x
		self.owner.y = new_y

		if self.owner.equipment: 
			item_name = self.owner.equipment.name

		elif self.name: 
			item_name = self.owner.item.name

		elif self.name_object: 
			item_name = self.name_object

		game_instance.game_message(self.current_container.owner.creature.name + " drops " + item_name + ".")

	def use(self, actor_in, game_instance = None):
		if self.owner.equipment:
			self.owner.equipment.toggle_equip(actor_in, game_state = game_instance)
			return
		else: 
			print("This item cannot be equipped.")
		
		if self.use_function:
			result = self.use_function(self.current_container.owner, self.value)
		
			if result is not None:
				print("use_function failed")
			else:
				self.current_container.inventory.remove(self.owner)


class EquipmentComponent:
	def __init__(self, slot = None, name = None,
		dam_bonus = {}, res_bonus = {},description = "There is no description for this item."):

		self.description = description
		self.dam_bonus = dam_bonus
		self.res_bonus = res_bonus
		self.name = name
		self.slot = slot
		self.equipped = False

	def toggle_equip(self, actor_in = None, game_state = None):
		if self.equipped:
			self.equipped = False
			actor_utilities.update_stats(actor_to_update = actor_in)

		else:
			self.equip(game_instance = game_state)

	def equip(self, game_instance = None):
		all_equipped_items = self.owner.item.current_container.equipped_items
		
		for item in all_equipped_items:
			if item.equipment.slot and (item.equipment.slot == self.slot):
				#ynaq prompt to replace?
				return
		self.equipped = True
		game_instance.game_message("Equipped in " + (str(self.slot)) + ".")

class Exit_Point_Component:
	def __init__(self, require_input, next_map_key = "", static = True, target_map_type = "dungeon"):
		self.require_input = require_input,
		self.next_map_key = next_map_key
		self.static = True
		self.target_map_type = target_map_type

	def use(self, game_instance = None):
		game_instance.transition()


		#physical door that can be opened or closed
class Door_Component:
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

	def interact(self, game_instance = None):
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
		game_instance.game_message(self.door_interaction_message)

	def lock_unlock(self, game_instance = None):
		#add a line or two to check if the door is closed first. you can't lock and open door
		if is_locked:
			is_locked = False
			door_interaction_message = "You unlock the door."
		else:
			is_locked = True
			door_interaction_message = "You lock the door."

		game_instance.game_message(door_interaction_message, msg_color = constants.COLOR_WHITE)

	print("Placeholder")


class Shopkeep_Component:
	def __init__(self, category = "general", funds = 100, stock = []):
		self.category = category,
		self.funds = funds,
		self.stock = stock

class Trap_Component:
	def __init__(self, trap_effect = None, is_active = True, is_visible = True, disarm_difficulty = 1):
		self.trap_effect = trap_effect,
		self.is_active = is_active,
		self.disarm_difficulty = disarm_difficulty
		self.is_visible = is_visible

		#(trap_effect = "fire_trap", is_active = True, is_visible = True, disarm_difficulty = 1)


	def affect_receiver(receiver = None):
		#self.trap_effect

		#default, damage the receiver
		if receiver.creature:
			receiver.creature.take_damage
		print("Placeholder")

class Creature_Component:
	def __init__(self, name_instance, hp = 10, 
		death_function = None, money = 0,

		category = "",

		base_dodge = 20,
		base_accuracy = 100,
		base_crit_chance = 5,
		base_crit_mult = 1.5,

		noncorporeal = False,
		local_line_of_sight = 7,
		proximate_actors = [],
		proximate_hostiles = [],
		target = structures.Target(),

		base_damages = {},
		base_resistances = {},
		net_resistances = 	{},	
		net_damages = 	{},	
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
		self.noncorporeal = noncorporeal

		#combat stats
		self.base_accuracy = base_accuracy
		self.base_dodge = base_dodge
		self.base_crit_chance = base_crit_chance
		self.base_crit_mult = base_crit_mult
		self.local_line_of_sight = local_line_of_sight
		self.proximate_actors = proximate_actors
		self.proximate_hostiles = proximate_hostiles
		self.base_damages = base_damages
		self.base_resistances = base_resistances
		self.net_resistances = base_resistances
		self.net_damages = base_damages

		#add new damage types and stuff later
	def take_damage(self, damage_received, attacker):
		self.current_hp -= damage_received

		#possibly change later to include the name of the attacker
		if self.current_hp <= 0:
			if self.death_function is not None:
				self.death_function(self.owner)
				
				attacker.creature.current_xp += self.xp_on_death


	def move(self, dx, dy, game_instance = None):
		new_x = self.owner.x
		new_y = self.owner.y
		next_x = self.owner.x + dx
		next_y = self.owner.y + dy

		#check if creature is trying to move off the map
		if next_x > 0 and next_x <= (game_instance.current_map_x - 1):
			if next_y > 0 and next_y < (game_instance.current_map_y - 1):
				tile_is_wall = (game_instance.current_map[next_x][next_y].block_path == True)
				target = map_check_for_creatures(next_x, next_y, self.owner, game_instance)

				#is there are target where the actor iss attempting to movie
				if target:

					#check if moving to a trap
					if target.trap_com:
						print("Target is a trap.")
						if not tile_is_wall:
							self.owner.x = next_x
							self.owner.y = next_y
							target.trap_com.affect_receiver(receiver = self)
							return

					#else, check if hostile
					if self.owner.allegiance_com and target.allegiance_com:
					#	if (self.owner == PLAYER): 
						print(self.owner.allegiance_com.category[0])
						if (self.owner.allegiance_com.category[0] == "player"):			#include Y/N/Q prompt later
							self.attack(target, game_instance)
							return

						#check if target's category is in the list of hostile categories, if so, attack
						for allegiance_type in self.owner.allegiance_com.hostile_list:
							if str(target.allegiance_com.category) == allegiance_type: 
								self.attack(target, game_instance)
						
					else:print("One or both actors does not have an allegiance component.")

				#move this code to a separate function
				if not tile_is_wall and target is None:
					#used for checking if the owner has moved from the last tile or not
					self.owner.last_x = self.owner.x
					self.owner.last_y = self.owner.y

					self.owner.x = next_x
					self.owner.y = next_y

					#if there are items at the player's tile, print them to the message log
					#collapse this into a function later?
					if (self.owner.allegiance_com.category[0] == "player"):
						map_tile_query(query_x = self.owner.x, query_y = self.owner.y, exclude_query_player = True, game_instance = game_instance)
							

	def attack(self, target, game_instance = None):
		chance_to_hit = self.base_accuracy - target.creature.base_dodge

		if random.randint(0,100) < chance_to_hit:
			#do the damage
			damage_dealt = actor_utilities.damage_target(self, damage_in = self.net_damages, target = target)

			hit_was_critical = False
			if random.randint(0,100) < self.base_crit_chance:
				damage_dealt = damage_dealt * self.base_crit_mult
				hit_was_critical = True

			if (damage_dealt <= 0): 
				game_instance.game_message(self.name_instance + " fails to do any damage " + target.creature.name_instance + " at all.")
			
			else:
				if hit_was_critical: game_instance.game_message((self.name_instance + " attacks " + target.creature.name_instance + " and does " + str(damage_dealt) + " damage in a critical hit."), constants.COLOR_WHITE)
				else: 
					game_instance.game_message((self.name_instance + " attacks " + target.creature.name_instance + " and does " + str(damage_dealt) + " damage."), constants.COLOR_WHITE)
					target.creature.take_damage(damage_dealt, attacker = self.owner)
		else: game_instance.game_message((self.name_instance + " fails to hit " + target.creature.name_instance + " and does no damage."), constants.COLOR_WHITE)
			

	def heal(self, value):
		self.current_hp += value
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
			if bonus: dodge += bonus

		return dodge

	@property
	def dodge(self):
		dodge = self.base_dodge_chance
		object_bonuses = []
		if self.owner.container:
			object_bonuses = [obj.equipment.dodge_bonus 
			for obj in self.owner.container.equipped_items]

		for bonus in object_bonuses: 
			if bonus: dodge += bonus

		return dodge


def map_check_for_creatures(x, y, exclude_object = None, game_instance = None):
	target = None
	if exclude_object:
		#check objectlist to find creature at that location that isn't excluded
		#include check to determine if hostile or not
		for object in game_instance.current_objects:
			if (object is not exclude_object and 										
				object.x == x and 
				object.y == y and 		
				object.creature):												
					target = object					
			if target:
				return target
	else:
		#check objectlist to find any creature at that location ???
		for object in game_instance.current_objects:
			if (
			#ability to attack thin air? 										
				object.x == x and 
				object.y == y and 		
				object.creature):												
					target = object				
			if target:
				return target	


def map_tile_query(query_x, query_y, exclude_query_player = False, accept_nothing = False, distant_query = False, game_instance = None):
	objects_at_player_tile = map_objects_at_coords(query_x, query_y, exclude_player = exclude_query_player, gameinstance = game_instance)
	query_result = "nothing."

	if (query_x > 0 and query_x < game_instance.current_map_x): 
		if (query_y > 0 and query_y < game_instance.current_map_y):
			tile_is_wall = (game_instance.current_map[query_x][query_y].block_path == True)
		
	else: return

	if tile_is_wall: query_result = " a wall. Very astute."

	if not tile_is_wall:
		if len(objects_at_player_tile) == 1:
			for obj in objects_at_player_tile:

				if obj.item: 
					query_result = obj.item.name

				if obj.equipment: 
					query_result = obj.equipment.name

				if obj.creature: 
					query_result = obj.creature.name_instance
			
		elif len(objects_at_player_tile) > 1: query_result = " multiple objects."
 
	if not distant_query:
		if not accept_nothing and query_result == "nothing.": return
		first_half = "You see at your feet "

	else : first_half = "You see "

	game_instance.game_message(str(first_half) + query_result)


def map_objects_at_coords(coords_x, coords_y, exclude_player = False, gameinstance = None):
	object_options = [obj for obj in gameinstance.current_objects 
	if obj.x == coords_x and obj.y == coords_y]

	if exclude_player:
		for obj in object_options:
			if (obj.allegiance_com) and (obj.allegiance_com.category[0] == "player"):
				object_options.remove(obj)

	return object_options
