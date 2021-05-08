import tcod as libtcod
import constants
import random


def create_room(new_map, new_room):
	for x in range(new_room.x1, new_room.x2):
		for y in range(new_room.y1, new_room.y2):
			clear_tile(map_in = new_map, tileX = x, tileY = y)

def clear_tile(map_in, tileX, tileY):
		map_in[tileX][tileY].block_path = False
		map_in[tileX][tileY].is_diggable = False
		map_in[tileX][tileY].transparent = True
		map_in[tileX][tileY].visible_tile_color = constants.COLOR_WHITE
		map_in[tileX][tileY].explored_tile_color = constants.COLOR_L_GRAY
		map_in[tileX][tileY].tile_icon = "."

def create_tunnels(coords1, coords2, new_map):
	coin_flip = (libtcod.random_get_int(0, 0, 1) == 1)

	x1, y1 = coords1
	x2, y2 = coords2

	if coin_flip:
		for x in range(int(min(int(x1), int(x2))), int(max(int(x1), int(x2)) + 1)):
			clear_tile(map_in = new_map, tileX = int(x), tileY = int(y1))

		for y in range(min(y1, y2), max(y1, y2) + 1):
			clear_tile(map_in = new_map, tileX = int(x2), tileY = int(y))
	else:
		for y in range(min(int(y1), int(y2)), max(int(y1), int(y2)) +1):
			clear_tile(map_in = new_map, tileX = int(x1), tileY = int(y))

		for x in range(min(int(x1), int(x2)), max(x1, x2) +1):
			clear_tile(map_in = new_map, tileX = int(x), tileY = int(y2))

	if coin_flip:
		for x in range(min(int(x1), int(x2)), max(int(x1), int(x2)) +1):
			clear_tile(map_in = new_map, tileX = int(x), tileY = int(y1))

		for y in range(min(int(y1), int(y2)), max(int(y1), int(y2)) +1):
			clear_tile(map_in = new_map, tileX = int(x2), tileY = int(y))
	else: 
		for y in range(min(int(y1), int(y2)), max(int(y1), int(y2)) +1):
			clear_tile(map_in = new_map, tileX = int(x1), tileY = int(y1))

		for x in range(min(int(x1), int(x2)), max(int(x1), int(x2)) +1):
			clear_tile(map_in = new_map, tileX = int(x), tileY = int(y1))

def make_borders_undiggable(map_in, map_x, map_y):
	for i in range(0, map_x):
		map_in[i][0].block_path = True
		map_in[i][0].is_diggable = False
		map_in[i][0].transparent = False
		map_in[i][0].visible_tile_color = constants.COLOR_L_BROWN
		map_in[i][0].explored_tile_color = constants.COLOR_BROWN
		map_in[i][0].tile_icon = "#"

		map_in[i][map_y -1].block_path = True
		map_in[i][map_y -1].block_path = True
		map_in[i][map_y -1].is_diggable = False
		map_in[i][map_y -1].transparent = False
		map_in[i][map_y -1].visible_tile_color = constants.COLOR_L_BROWN
		map_in[i][map_y -1].explored_tile_color = constants.COLOR_BROWN
		map_in[i][map_y -1].tile_icon = "#"

	for i in range(0, map_y):
		map_in[0][i].block_path = True
		map_in[0][i].is_diggable = False
		map_in[0][i].transparent = False
		map_in[0][i].visible_tile_color = constants.COLOR_L_BROWN
		map_in[0][i].explored_tile_color = constants.COLOR_BROWN
		map_in[0][i].tile_icon = "#"

		map_in[map_x -1][i].block_path = True
		map_in[map_x -1][i].is_diggable = False
		map_in[map_x -1][i].transparent = False
		map_in[map_x -1][i].visible_tile_color = constants.COLOR_L_BROWN
		map_in[map_x -1][i].explored_tile_color = constants.COLOR_BROWN
		map_in[map_x -1][i].tile_icon = "#"

