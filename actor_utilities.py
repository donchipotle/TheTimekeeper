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
				#print(str(damage_type) + "," + str(dam_value))
				actor_to_update.creature.net_damages[damage_type] += gear.equipment.dam_bonus[damage_type]

		for resist_type, res_value in gear.equipment.res_bonus.items():
			if res_value != 0:
				actor_to_update.creature.net_resistances[resist_type] += gear.equipment.res_bonus[resist_type]