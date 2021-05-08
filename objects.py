import constants
import pygame
import settings


class Room:
	def __init__(self, coords, size): #coords are upper left corner location 
		self.x1, self.y1 = coords
		self.w, self.h = size

		self.x2 = self.x1 + self.w
		self.y2 = self.y1 + self.h

	@property
	def center(self):
		center_x = int(((self.x1 + self.x2) // 2))
		center_y = int(((self.y1 + self.y2) // 2))

		return (center_x, center_y)

	def intersect(self, other):
		#return true if another obj intersects with this one
		objects_intersect = (self.x1 <= other.x2 and self.x2 >= other.x1 and
                             self.y1 <= other.y2 and self.y2 >= other.y1)

		return objects_intersect

#object that is spawned in towns
class Building:
	def __init__(self, coords, size): #coords are upper left corner location 
		self.x1, self.y1 = coords
		self.w, self.h = size

		self.x2 = self.x1 + self.w
		self.y2 = self.y1 + self.h

	def intersect(self, other):
		#return true if another obj intersects with this one
		objects_intersect = (self.x1 <= other.x2 and self.x2 >= other.x1 and
                             self.y1 <= other.y2 and self.y2 >= other.y1)

		return objects_intersect

	#the center of each building
	@property
	def center(self):
		center_x = ((self.x1 + self.x2) // 2)
		center_y = ((self.y1 + self.y2) // 2)

		return (center_x, center_y)



class Camera:
	def __init__(self, follow_actor):
		self.width = constants.CAM_WIDTH
		self.height = constants.CAM_HEIGHT
		self.x, self.y = (0,0)

	def update(self, follow_actor): #include some code to move along with the selection cursor
		target_x = follow_actor.x * constants.CELL_WIDTH + constants.CELL_HALF_WIDTH
		target_y = follow_actor.y * constants.CELL_HEIGHT + constants.CELL_HALF_HEIGHT
		distance_x, distance_y = self.map_dist((target_x, target_y))

		self.x += int(distance_x * settings.CAM_LERP_X)
		self.y += int(distance_y * settings.CAM_LERP_Y)

	@property
	def rectangle(self):
		pos_rect = pygame.Rect((0,0), (constants.CAM_WIDTH, constants.CAM_HEIGHT))
		pos_rect.center = (self.x, self.y)
		return pos_rect

	@property 
	def map_address(self):
		map_x = self.x / constants.CELL_WIDTH
		map_y = self.y / constants.CELL_HEIGHT
		return (map_x, map_y)

	def map_dist(self, coords):
		new_x, new_y = coords
		dist_x = new_x - self.x
		dist_y = new_y - self.y
		return(dist_x, dist_y)

	def cam_dist(self, coords):
		win_x, win_y = coords
		dist_x = win_x - (self.width / 2)
		dist_y = win_y - (self.height / 2)
		return (dist_x, dist_y)

	def win_to_map(self, coords):  #
		target_x, target_y = coords
		#convert window coords -> distance from camera
		cam_d_x, cam_d_y = self.cam_dist((target_x, target_y))
		#distance from cam -> map coord
		map_p_x = self.x + cam_d_x
		map_p_y = self.y + cam_d_y

		return((map_p_x, map_p_y))
