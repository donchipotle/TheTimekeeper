import constants


class Damage:
	def __init__(self, fire = 0, electricity = 0, poison = 0, frost = 0, magic = 0,
				ballistic = 0, piercing = 0, bludgeoning = 0, slashing = 0, eldritch = 0):
		self.fire = fire
		self.electricity = electricity
		self.poison = poison
		self.frost = frost
		self.magic = magic

		self.ballistic = ballistic
		self.piercing = piercing
		self.bludgeoning = bludgeoning
		self.slashing = slashing
		self.eldritch = eldritch

class Resistance:
	def __init__(self, fire_resist = 0, electricity_resist = 0, poison_resist = 0, frost_resist = 0, magic_resist = 0,
				ballistic_resist = 0, piercing_resist = 0, bludgeoning_resist = 0, slashing_resist = 0, eldritch_resist = 0):
		self.fire_resist = fire_resist
		self.electricity_resist = electricity_resist
		self.poison_resist = poison_resist
		self.frost_resist = frost_resist
		self.magic_resist = magic_resist

		self.ballistic_resist = ballistic_resist
		self.piercing_resist = piercing_resist
		self.bludgeoning_resist = bludgeoning_resist
		self.slashing_resist = slashing_resist
		self.eldritch_resist = eldritch_resist

		#structures
class Tile:
	def __init__(self, block_path, tile_icon = ".", is_diggable = True, transparent = False, explored = False,
		visible_tile_color = constants.COLOR_WHITE,
		explored_tile_color = constants.COLOR_GRAY): 

		self.block_path = block_path
		self.explored = explored
		self.transparent = transparent
		self.is_diggable = is_diggable
		self.tile_icon = tile_icon
		self.visible_tile_color = visible_tile_color
		self.explored_tile_color = explored_tile_color

class Map:
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

class Direction:
	def __init__(self, x = 0, y = 0):
		self.x = x,
		self.y = y

class Target:
	def __init__(self, actor = None, distance = 0, threat_level = 0):
		self.actor = actor,
		self.distance = distance,
		self.threat_level = threat_level

class ScreenStatus:
	def __init__(self, inventory_open = False, message_log_open = False,):
		self.inventory_open = inventory_open,
		self.message_log_open = message_log_open
