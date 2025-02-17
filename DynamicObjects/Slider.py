from DynamicObjects.Plane import *


		
	
class HorizontalSlider:
	def __init__(self, pos, size, sliders, value):
		self.plane = Plane(pos, size, Pixel4(0, 0, 0, 0))
		self.plane.add_child(Vertex(.5, .5), Vertex(.95, .2), Pixel4(128, 164, 128, 255))
		self.plane.add_child(Vertex(-1, 0), Vertex(.05, 1), Pixel4(65, 255, 64, 255))
		self.value_range = (0, value)
		self._value = 0
	
	def draw(self, surface):
		if self.plane.hover:
			self.lane.draw(surface)
	@property
	def value(self):
		self.slider._center

	@property
	def lane(self):
		return self.plane.childs[0]
	
	@property
	def slider(self):
		return self.plane.childs[1]
	
	@property
	def start(self):
		return self.lane.center - self.half_size
	
	@property
	def end(self):
		return self.lane.center + self.half_size
	
	@property
	def posrange(self):
		return self.end - self.start



if __name__ == '__main__':
	pass
