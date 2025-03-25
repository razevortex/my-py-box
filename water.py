import pygame
import random
import math


# Configuration
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
CONTAINER_RECT = pygame.Rect(100, 100, 600, 400)
PARTICLE_RADIUS = 6
PARTICLE_BODY_RADIUS = 4
PARTICLE_COUNT = 150
MOUSE_RADIUS = 80
GRAVITY_FORCE = 4
COHESION_FORCE = .2
COLLISION_FORCE = 5
MOUSE_FORCE = 20.0
DENSITY_CHECK_RADIUS = 30

COLORS = [
	pygame.Color("blue"),
	pygame.Color("red")
	]

class Particle:
	def __init__(self):
		self.x = random.uniform(CONTAINER_RECT.left + PARTICLE_RADIUS,
		                        CONTAINER_RECT.right - PARTICLE_RADIUS
		                        )
		self.y = random.uniform(CONTAINER_RECT.top + PARTICLE_RADIUS,
		                        CONTAINER_RECT.bottom - PARTICLE_RADIUS
		                        )
		self.vx = 0
		self.vy = 0
		self.temperature = 0  # Will be used for color gradient
	
	def apply_force(self, fx, fy):
		self.vx += fx
		self.vy += fy
	
	def update(self):
		# Apply friction and movement
		self.vx *= 0.25
		self.vy *= 0.25
		self.x += self.vx
		self.y += self.vy
		
		# Constrain to container
		self.x = max(CONTAINER_RECT.left + PARTICLE_RADIUS * 1.5,
		             min(self.x, CONTAINER_RECT.right - PARTICLE_RADIUS * 1.5)
		             )
		self.y = max(CONTAINER_RECT.top + PARTICLE_RADIUS * 1.5,
		             min(self.y, CONTAINER_RECT.bottom - PARTICLE_RADIUS * 1.5)
		             )
	
	def draw(self, screen):
		density_color = COLORS[0].lerp(COLORS[1], self.temperature)
		pygame.draw.circle(screen, density_color,
		                   (int(self.x), int(self.y)), PARTICLE_BODY_RADIUS
		                   )

def main():
	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	particles = [Particle() for _ in range(PARTICLE_COUNT)]
	clock = pygame.time.Clock()
	
	running = True
	while running:
		screen.fill((30, 30, 30))
		
		# Handle input
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
		
		mouse_pos = pygame.mouse.get_pos()
		
		# Calculate particle interactions
		for particle in particles:
			# Gravity
			particle.apply_force(0, GRAVITY_FORCE)
			
			# Cohesion (surface tension)
			nearby = [p for p in particles
			          if math.hypot(p.x - particle.x, p.y - particle.y) < DENSITY_CHECK_RADIUS]
			if nearby:
				avg_x = sum(p.x for p in nearby) / len(nearby)
				avg_y = sum(p.y for p in nearby) / len(nearby)
				particle.apply_force((avg_x - particle.x) * COHESION_FORCE,
				                     (avg_y - particle.y) * COHESION_FORCE
				                     )
			
			# Collision avoidance
			for other in particles:
				if particle == other:
					continue
				dx = other.x - particle.x
				dy = other.y - particle.y
				distance = math.hypot(dx, dy)
				distance = distance if distance != 0 else 1
				min_distance = PARTICLE_RADIUS * 3
				if distance < min_distance:
					force = (min_distance - distance) * COLLISION_FORCE
					particle.apply_force(-dx / distance * force, -dy / distance * force)
			
			# Mouse interaction
			mx, my = mouse_pos
			distance_to_mouse = math.hypot(mx - particle.x, my - particle.y)
			if distance_to_mouse < MOUSE_RADIUS:
				angle = math.atan2(particle.y - my, particle.x - mx)
				force = MOUSE_FORCE * (1 - distance_to_mouse / MOUSE_RADIUS)
				particle.apply_force(math.cos(angle) * force, math.sin(angle) * force)
			
			# Update density for coloring
			neighbors = [p for p in particles
			             if math.hypot(p.x - particle.x, p.y - particle.y) < DENSITY_CHECK_RADIUS]
			particle.temperature = min(1, len(neighbors) / 15)
			
			particle.update()
			particle.draw(screen)
			[item.update() for item in particles]
			[item.draw(screen) for item in particles]
		pygame.draw.rect(screen, (200, 200, 200), CONTAINER_RECT, 2)
		pygame.display.flip()
		# Draw container

if __name__ == '__main__':
	main()