from DynamicObjects.Plane import *
from SlotObjects.ValueMapping import ValueRange as vrange

		
	
class HorizontalSlider:
	def __init__(self, pos, size, value:dict):
		self.plane = Plane(pos, size, Pixel4(0, 0, 0, 0))
		self.plane.add_child(Vertex(.5, .5), Vertex(.95, .2), Pixel4(128, 164, 128, 255))
		self.plane.add_child(Vertex(-1, 0), Vertex(.05, 1), Pixel4(65, 255, 64, 255))
		self.value_range = vrange(**value)
	
	def draw(self, surface):
		if self.plane.hover:
			self.lane.draw(surface)
	
	def value_update(self, delta=0):
		self.value_range.value += delta
		if self.slider.hold:
			self.value_range.rel_pos = Mouse.position.x / self.posrange.x
		self.plane.childs[1]._center = Vertex(self.value_range.rel_pos, 0)
	
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
