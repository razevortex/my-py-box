from DynamicObjects.AdaptingPlane import AdaptingPlane
from SlotObjects.Verticies import *
from SlotObjects.Fetcher import *

class RelativeTo:
	def __init__(self, parent=None):
		self.parent = parent if parent is None else FetcherObject(parent)
		if self.parent is not None:
			self.parent.keys = ['center', 'size', 'half_size', 'full_size']

	def abs_center(self, center):
		if self.parent is None:
			return AdaptingPlane.overlay.half_size + AdaptingPlane.overlay.half_size * center
		else:
			return self.parent.center + self.size * center
		
	def abs_size(self, size):
		if self.parent is None:
			return AdaptingPlane.overlay.fullsize * size
		else:
			return self.parent.full_size * size

if __name__ == '__main__':
	pass
