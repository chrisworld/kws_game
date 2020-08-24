"""
input handler class
"""

import pygame


class InputHandler():
	"""
	Input Handler class
	"""

	def __init__(self, obj, handler_type='key_stroke_dir', grid_move=False):

		# handler type
		self.handler_type = handler_type;
		
		# object to be handled
		self.obj = obj

		# grid handling
		self.grid_move = grid_move


	def key_stroke_direction(self, event):
		"""
		input handling for object
		must have implemented direction_change
		"""

		# in direction
		if event.type == pygame.KEYDOWN:

			if event.key == pygame.K_LEFT:
				self.obj.direction_change([-1, 0])
			elif event.key == pygame.K_RIGHT:
				self.obj.direction_change([1, 0])
			if event.key == pygame.K_UP:
				self.obj.direction_change([0, -1])
			elif event.key == pygame.K_DOWN:
				self.obj.direction_change([0, 1])

		# counter direction
		elif event.type == pygame.KEYUP and not self.grid_move:

			if event.key == pygame.K_LEFT:
				self.obj.direction_change([1, 0])
			elif event.key == pygame.K_RIGHT:
				self.obj.direction_change([-1, 0])
			if event.key == pygame.K_UP:
				self.obj.direction_change([0, 1])
			elif event.key == pygame.K_DOWN:
				self.obj.direction_change([0, -1])


	def set_active(self, event):
		"""
		set object active on space
		"""

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				# toggle activeness
				self.obj.is_active = not self.obj.is_active


	def handle(self, event):
		"""
		update object
		"""

		# key stroke down handling
		if self.handler_type == 'key_stroke_dir':

			# direction
			self.key_stroke_direction(event)

		try:
			self.set_active(event)
		except:
			print("could not set object active")