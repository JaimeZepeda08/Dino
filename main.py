import pygame 
import neat 
import os 
import time 
import random

pygame.init()

WIDTH,HEIGHT = 1200,400
WINDOW = pygame.display.set_mode((WIDTH,HEIGHT))

GREY = (25,25,25)

DINO1_IMG = pygame.image.load(os.path.join("Assets","dino1.png"))
DINO2_IMG = pygame.image.load(os.path.join("Assets","dino2.png"))
DINO3_IMG = pygame.image.load(os.path.join("Assets","dino3.png"))
DINO4_IMG = pygame.image.load(os.path.join("Assets","dino4.png"))
DINO5_IMG = pygame.image.load(os.path.join("Assets","dino5.png"))
DINO_IMGS = [DINO1_IMG,DINO2_IMG,DINO3_IMG,DINO4_IMG,DINO5_IMG]

BIRD1_IMG = pygame.image.load(os.path.join("Assets","bird1.png"))
BIRD2_IMG = pygame.image.load(os.path.join("Assets","bird2.png"))
BIRD_IMGS = [BIRD1_IMG,BIRD2_IMG]

CACTUS_SMALL1_IMG = pygame.image.load(os.path.join("Assets","cactus_small1.png"))
CACTUS_SMALL2_IMG = pygame.image.load(os.path.join("Assets","cactus_small2.png"))
CACTUS_SMALL3_IMG = pygame.image.load(os.path.join("Assets","cactus_small3.png"))
CACTUS_SMALL_IMGS = [CACTUS_SMALL1_IMG,CACTUS_SMALL2_IMG,CACTUS_SMALL3_IMG]

CACTUS_LARGE1_IMG = pygame.image.load(os.path.join("Assets","cactus_large1.png"))
CACTUS_LARGE2_IMG = pygame.image.load(os.path.join("Assets","cactus_large2.png"))
CACTUS_LARGE3_IMG = pygame.image.load(os.path.join("Assets","cactus_large3.png"))
CACTUS_LARGE_IMGS = [CACTUS_LARGE1_IMG,CACTUS_LARGE2_IMG,CACTUS_LARGE3_IMG]

GROUND_IMG = pygame.image.load(os.path.join("Assets","ground.png"))

FONT_STATS = pygame.font.Font(os.path.join("Assets","PressStart2P-Regular.ttf"),20)

SPEED = 12 
MAX_SPEED = 20 
ACCELERATION = 1.0002

FPS = 60

class Dino:
	IMGS = DINO_IMGS
	ANIMATION_TIME = 8

	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.initial_height = self.y 
		self.velocity = 0
		self.elapsed_time = 0 
		self.can_jump = False
		self.is_jump_short = False
		self.is_jump_long = False
		self.is_duck = False
		self.img_counter = 0 
		self.curr_img = self.IMGS[1]

	def move(self):
		self.elapsed_time += 1
		d = (self.velocity * self.elapsed_time + 1.5 * self.elapsed_time ** 2) / 5 #projectile formula 
		if d >= 16: #terminal velocity 
			d = 16 
		self.y += d

		if self.y >= self.initial_height:
			self.y = self.initial_height
			self.is_jump_short = False
			self.is_jump_long = False
			self.can_jump = True 

	def jump_short(self):
		self.is_jump_short = True
		if self.can_jump == True: 
			self.velocity = -23
			self.elapsed_time = 0
		self.can_jump = False 

	def jump_long(self):
		self.is_jump_long = True
		if self.can_jump == True:
			self.velocity = -25
			self.elapsed_time = 0
		self.can_jump = False 

	def duck(self):
		self.is_duck = True

	def stand(self):
		 self.is_duck = False

	def draw(self,win):
		if not self.is_duck and not self.is_jump_short and not self.is_jump_long:
			self.img_counter += 1
			if self.img_counter < self.ANIMATION_TIME:
				self.curr_img = self.IMGS[1]
			elif self.img_counter < self.ANIMATION_TIME * 2:
				self.curr_img = self.IMGS[2]
			elif self.img_counter < self.ANIMATION_TIME * 2 + 1:
				self.curr_img = self.IMGS[1]
				self.img_counter = 0

		elif (self.is_jump_long or self.is_jump_short) and not self.is_duck:
			self.curr_img = self.IMGS[0]

		elif self.is_duck and not self.is_jump_long and not self.is_jump_short:
			self.img_counter += 1
			if self.img_counter < self.ANIMATION_TIME:
				self.curr_img = self.IMGS[3]
			elif self.img_counter < self.ANIMATION_TIME * 2:
				self.curr_img = self.IMGS[4]
			elif self.img_counter < self.ANIMATION_TIME * 2 + 1:
				self.curr_img = self.IMGS[3]
				self.img_counter = 0

		win.blit(self.curr_img,(self.x,self.y))

	def get_mask(self):
		return pygame.mask.from_surface(self.curr_img)

class Bird: 
	VELOCITY = SPEED
	ANIMATION_TIME = 10
	IMGS = BIRD_IMGS

	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.img_counter = 0
		self.curr_img = self.IMGS[0]

	def move(self):
		self.VELOCITY = SPEED
		self.x -= self.VELOCITY 

	def draw(self,win):
		self.img_counter += 1
		if self.img_counter < self.ANIMATION_TIME:
			self.curr_img = self.IMGS[0]
		elif self.img_counter < self.ANIMATION_TIME * 2:
			self.curr_img = self.IMGS[1]
		elif self.img_counter < self.ANIMATION_TIME * 2 + 1:
			self.curr_img = self.IMGS[0]
			self.img_counter = 0

		win.blit(self.curr_img,(self.x,self.y))

	def collide(self,dino):
		dino_mask = dino.get_mask()
		mask = pygame.mask.from_surface(self.curr_img)
		offset = (int(self.x - dino.x), int(self.y - round(dino.y)))
		point = dino_mask.overlap(mask,offset)

		if point:
			return True 
		else:
			return False 

class Cactus:
	VELOCITY = SPEED
	IMGS_SMALL = CACTUS_SMALL_IMGS 
	IMGS_LARGE = CACTUS_LARGE_IMGS 

	def __init__(self,x,size):
		self.x = x
		self.y = 0
		self.img = self.IMGS_LARGE[2]
		self.size = size 

	def move(self):
		self.VELOCITY = SPEED
		self.x -= self.VELOCITY

	def draw(self,win):
		if self.size == 1:
			self.img = self.IMGS_SMALL[0]
			self.y = 280
		elif self.size == 2:
			self.img = self.IMGS_SMALL[1]
			self.y = 280
		elif self.size == 3:
			self.img = self.IMGS_SMALL[2]
			self.y = 280
		elif self.size == 4:
			self.img = self.IMGS_LARGE[0]
			self.y = 250
		elif self.size == 5:
			self.img = self.IMGS_LARGE[1]
			self.y = 250
		elif self.size == 6:
			self.img = self.IMGS_LARGE[2]
			self.y = 250

		win.blit(self.img,(self.x,self.y))

	def collide(self,dino):
		dino_mask = dino.get_mask()
		mask = pygame.mask.from_surface(self.img)
		offset = (int(self.x - dino.x), int(self.y - round(dino.y)))
		point = dino_mask.overlap(mask,offset)

		if point:
			return True 
		else:
			return False 


class Ground:
	VELOCITY = SPEED
	WIDTH = GROUND_IMG.get_width()
	IMG = GROUND_IMG

	def __init__(self,y):
		self.y = y 
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self):
		self.VELOCITY = SPEED
		self.x1 -= self.VELOCITY
		self.x2 -= self.VELOCITY

		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH
		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self,win):
		win.blit(self.IMG,(self.x1,self.y))
		win.blit(self.IMG,(self.x2,self.y))

def draw_window(dino,obstacles,ground,score):
	WINDOW.fill(GREY)

	ground.draw(WINDOW)
	for obstacle in obstacles:
			obstacle.draw(WINDOW)
	dino.draw(WINDOW)
	text = FONT_STATS.render("Score: " + str(int(score)),1,(255,255,255))
	WINDOW.blit(text,(WIDTH - 10 - text.get_width(),10))

	pygame.display.update()

def main():
	global SPEED

	clock = pygame.time.Clock()
	run = True 

	dino = Dino(100,250)
	obstacles = [Cactus(1500,random.randint(1,6))]
	ground = Ground(240 + DINO1_IMG.get_height())

	score = 0

	while run:
		clock.tick(FPS)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False 
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN: #temporary
				if event.key == pygame.K_SPACE:
					dino.jump_long()
				if event.key == pygame.K_UP:
					dino.jump_short()
				if event.key == pygame.K_DOWN:
					dino.duck()
			else:
				dino.stand()

		dino.move()
		for obstacle in obstacles:
			obstacle.move()
			if obstacle.collide(dino):
				main()
			if obstacle.x < -150:
				obstacles.remove(obstacle)
		ground.move()

		if obstacles[len(obstacles) - 1].x <= random.randint(600,800):
			index = random.randint(1,6)
			if index == 1 or index == 2 or index == 3 or index == 4:
				obstacles.append(Cactus(1500,random.randint(1,6)))
			elif index == 5:
				obstacles.append(Bird(1500,250))
			elif index == 6:
				obstacles.append(Bird(1500,190))

		if SPEED < MAX_SPEED:
			SPEED *= ACCELERATION
		elif SPEED > MAX_SPEED:
			SPEED = MAX_SPEED

		score += 0.1

		draw_window(dino,obstacles,ground,score)

main()

