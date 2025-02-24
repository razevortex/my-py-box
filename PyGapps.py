import pygame
from pygame.locals import *
import pygame.freetype as ttf
from SlotObjects.Verticies import *
from DynamicObjects.Slider import *
from DynamicObjects.Event import *
from DynamicObjects.MutaGen import *
from DynamicObjects.Switch import *
import win32api, win32com.client
import win32con
import win32gui

#test = MuCircleGen(Vertex(0, 0), Vertex(.1, 0), Pixel4(0, 0, 0, 64), 60)
#test.addEvent('hover', 60, radius=Vertex(.15, 0), color=Pixel4(127, 127, 127, 255))

test = SwitchMain(Vertex(0, 0), Vertex(.2, .1))
#test = Plane(Vertex(.0, .9), Vertex(.98, .1), (0, 0, 0, 0))
#test.add_child(Vertex(.5, 1.0), Vertex(.02, 1.0), (128, 62, 52))
#AdaptingPlane.setup_window('VLC media player', 'Playlist')
area = HorizontalSlider()
class PygameApp:
	def __init__(self, titles=('VLC media player', 'overlay')):
		pygame.init()
		self.title = titles
		AdaptingPlane.setup_window(*titles)
		self.areas = [ValueLine(), test]
		self.active_window = False
		self.main_window_rect = 0, 0, 0, 0
		self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
		self.background_color = (0, 0, 0, 255)
		pygame.display.set_caption(self.title[1])
		'''self.screen_width = self.screen.get_width()
		self.screen_height = self.screen.get_height()
		self.center = Vertex(self.screen_width//2, self.screen_height//2)
		self.size = Vertex(self.screen_width + self.screen_height) // 2
		self.frame = 0'''
		fuchsia = self.background_color[:3]
		hwnd = pygame.display.get_wm_info()["window"]
		win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
							   win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED
							   )
		# Set window transparency color
		win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
		self.running = True
	
	@property
	def current_main_rect(self):
		if self.main_window_rect != win32gui.GetWindowRect(win32gui.FindWindow(None, self.title[0])):
			self.main_window_rect = win32gui.GetWindowRect(win32gui.FindWindow(None, self.title[0]))
			return True
		return False
	
	def set_active_window(self):
		active_window = win32gui.GetForegroundWindow()
		active = win32gui.GetWindowText(active_window)
		if self.current_main_rect:
			overlay = win32gui.FindWindow(0, self.title[1])
			l, t, r, b = self.main_window_rect
			win32gui.MoveWindow(overlay, l, t, r - l, b - t, True)
			shell = win32com.client.Dispatch("WScript.Shell")
			shell.SendKeys('%')
			win32gui.SetForegroundWindow(handles(self.title[1]))
	
	def run(self, fps=60):
		"""Run the application loop until ESC is pressed"""
		self.running = True
		clock = pygame.time.Clock()
		
		while self.running:
			for event in pygame.event.get():
				if event.type == QUIT:
					self.running = False
				elif event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						self.running = False
			# self.set_active_window()
			Mouse.update()
			AdaptingPlane._align()
			self.screen.fill(self.background_color)
			for area in self.areas:
				area.draw(self.screen)
			# rect = pygame.Rect(area.to_rect)
			# pygame.draw.rect(self.screen, area._color, rect)
			
			# pygame.draw.polygon(self.screen, (128, 222, 53), [(0, 0), (100, 0), (100, 100), (0, 100)])
			
			pygame.display.flip()
			clock.tick(fps)
		
		pygame.quit()

def handles(title):
	def window_enum_handler(hwnd, resultList):
		if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != '':
			resultList.append((hwnd, win32gui.GetWindowText(hwnd)))
	
	def get_app_list(handles=[]):
		mlst = []
		win32gui.EnumWindows(window_enum_handler, handles)
		for handle in handles:
			mlst.append(handle)
		return mlst
	
	appwindows = get_app_list()
	for i in appwindows:
		if i[1] == title:
			return i[0]

# Execution Sandbox
if __name__ == '__main__':
	app = PygameApp()
	app.run()
