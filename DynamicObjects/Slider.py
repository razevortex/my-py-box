from DynamicObjects.Plane import *
from SlotObjects.ValueMapping import ValueRange as vrange

		
	
class HorizontalSlider:
	def __init__(self):
		self.plane = Plane(Vertex(.0, .9), Vertex(1, .2), Pixel4(0, 0, 0, 0))
		self.lane = Plane(Vertex(.0, .85), Vertex(1, .15), Pixel4(255, 0, 0, 255))
		self.slider = Plane(Vertex(-1, .85), Vertex(.05, .2), Pixel4(65, 255, 64, 255))
		#self.plane.add_child(Vertex(.5, .5), Vertex(1, 1), Pixel4(128, 164, 128, 255))
		#self.plane.add_child(Vertex(0, 0), Vertex(.05, 1), Pixel4(65, 255, 64, 255))
		self.value_range = vrange()
	
	def draw(self, surface):
		self.value_update()
		if self.plane.hover:
			pg.draw.rect(surface, self.lane.color.__tuple__(), pg.Rect(*self.lane.to_rect))
			pg.draw.rect(surface, self.slider.color.__tuple__(), pg.Rect(*self.slider.to_rect))
			#self.lane.draw(surface)
			self.slider.draw(surface)
			print(self.lane._center, self.lane._size, self.lane.to_rect)
			print(self.slider._center, self.slider._size, self.slider.to_rect)
			#self.lane.draw(surface)
			
	
	def value_update(self, delta=0):
		self.value_range.value += delta
		if self.slider.drag:
			self.value_range.rel_pos = self.posrange.x / 2 - (self.posrange.x - Mouse.position.x)
		try:t = self.posrange.x / self.value_range.rel_pos
		except:t = 0
		self.slider._center.x = 1 / self.value_range.rel_pos #self.posrange.x / 2
	
	
	@property
	def start(self):
		return self.lane._center - self.lane.half_size
	
	@property
	def end(self):
		return self.lane._center + self.lane.half_size
	
	@property
	def posrange(self):
		print('posrange: ', self.end - self.start)
		return self.end - self.start



if __name__ == '__main__':
	import time
	AdaptingPlane.setup_window('VLC media player', 'Playlist')
	area = HorizontalSlider()
	while True:
		time.sleep(.2)
		Mouse.update()
		AdaptingPlane._align()
		print(area)