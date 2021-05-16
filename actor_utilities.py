def reset_stats(actor_in):
	actor_in.creature.net_resistances = {}
	actor_in.creature.net_damages = {}

	for restype, resvalue in (actor_in.creature.base_resistances.items()):
		actor_in.creature.net_resistances[restype] = actor_in.creature.base_resistances[restype]
	for damtype, damvalue in (actor_in.creature.base_damages.items()):
		actor_in.creature.net_damages[damtype] = actor_in.creature.base_damages[damtype]

def update_stats(actor_to_update):
	reset_stats(actor_in = actor_to_update)

	#iterate through all equipped items in the actor's inventory
	for gear in actor_to_update.container.equipped_items:
		#check for nonzero bonuses/penalties incurred by item
		for damage_type, dam_value in gear.equipment.dam_bonus.items():
			if dam_value != 0:
				print(str(damage_type) + "," + str(dam_value))
				actor_to_update.creature.net_damages[damage_type] += gear.equipment.dam_bonus[damage_type]

		for resist_type, res_value in gear.equipment.res_bonus.items():
			if res_value != 0:
				actor_to_update.creature.net_resistances[resist_type] += gear.equipment.res_bonus[resist_type]

def damage_target(attacker, damage_in, target):
	final_damage = 0
	#check what damage types are being used and check them against the target's resistances. subtract and return total
	if damage_in and target.creature.net_resistances:
		for damage_type, dam_value in damage_in.items():
			if not (dam_value == 0):
				for res_type, res_value in target.creature.net_resistances.items():
					if damage_type == res_type:
					#	print("damage type " + str(damage_type) + ", " + str(dam_value) + " vs " + str(res_value) )
						damage = dam_value - res_value
						if (damage > 0):
							final_damage += damage

	return final_damage


def ai_designate_targets(actor = None, game_instance = None):

	map_make_local_fov(game_instance.current_map, actor_in = (actor), 
				fov_x = game_instance.current_map_x - 1, fov_y = game_instance.current_map_y - 1)
	
	libtcod.map_compute_fov(actor.creature.local_fov, actor.x, actor.y, 
								actor.creature.local_line_of_sight, 
								constants.FOV_LIGHT_WALLS, constants.FOV_AI_ALGO)

	for obj in game_instance.current_objects:
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