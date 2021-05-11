

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

class Container:
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


class Item:
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
			if self.owner.equipment: item_name = self.owner.equipment.name
			elif self.name: item_name = self.owner.item.name
			elif self.name_object: item_name = self.name_object
			#game_message(actor.creature.name + " picked up " + item_name + ".")

			actor.container.inventory.append(self.owner)
			game_instance.current_objects.remove(self.owner)
			self.current_container = actor.container
		
	def drop(self, new_x, new_y, game_instance = None):
		GAME.current_objects.append(self.owner)
		self.current_container.inventory.remove(self.owner)
		#place object at the coords at which it was dropped
		self.owner.x = new_x
		self.owner.y = new_y

		if self.owner.equipment: item_name = self.owner.equipment.name
		elif self.name: item_name = self.owner.item.name
		elif self.name_object: item_name = self.name_object
		game_instance.game_message(self.current_container.owner.creature.name + " drops " + item_name + ".")

	def use(self, actor_in, game_instance = None):
		if self.owner.equipment:
			self.owner.equipment.toggle_equip(actor_in)
			return
		else: 
			print("This item cannot be equipped.")
		
		if self.use_function:
			result = self.use_function(self.current_container.owner, self.value)
		
			if result is not None:
				print("use_function failed")
			else:
				self.current_container.inventory.remove(self.owner)