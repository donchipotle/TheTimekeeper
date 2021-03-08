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
	def __init__(self, block_path): #add more variables like blocking projectiles, blocking sight, DoT, etc.
		self.block_path = block_path
		self.explored = False
		#for things like cages, fences, other permeable barriers
		self.transparent = False
		self.is_diggable = True