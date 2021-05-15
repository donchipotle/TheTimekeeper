import actor_utilities

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