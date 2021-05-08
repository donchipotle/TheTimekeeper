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