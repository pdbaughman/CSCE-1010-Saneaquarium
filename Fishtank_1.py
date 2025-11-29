import pygame
import random
import math
import sys

# Constants for the game
WIDTH = 800
HEIGHT = 600
FPS = 60

TANK_FLOOR_Y = HEIGHT - 50*(HEIGHT/600)

FONT_SIZE = int(27*(WIDTH/800))
STARTING_MONEY = 200
FOOD_COST = 5
FISH_COST = 50
# this represents the background of the aquarium
background1 = pygame.image.load('background.png')
# This is for resizing the background
background1 = pygame.transform.scale(background1,(WIDTH,TANK_FLOOR_Y))
# this represents the position of the aquarium
background1reck = background1.get_rect(topleft = (0,0))
# floor rectangle
floorrect = pygame.Rect(0, TANK_FLOOR_Y, WIDTH, HEIGHT - TANK_FLOOR_Y)
class Fish:
    def __init__(self, sprite,Scale,velocitX,velocitY,beforeHunger,maxHunger,dt):
        self.sprite = pygame.image.load(sprite)
        self.position = (0,0)
        self.Scale = Scale
        W, H = Scale
        self.sprite = pygame.transform.scale(self.sprite,(W*2,H))
        self.velocitY = velocitY
        self.velocitX = velocitX
        self.spriteM = pygame.Surface((W,H))
        self.spriteM.fill((0,0,255))
        self.spriteM.set_colorkey((0,0,255))
        self.spriteM.blit(self.sprite,(0,0))
        self.spriteRect = self.spriteM.get_rect(center = self.position)
        self.directionX = -1
        self.directionY = 1
        self.trajectory = (0,0)
        self.beforeHunger = beforeHunger
        self.maxHunger = maxHunger
        self.dtu = dt 
        self.FNP = False # float in peace
    def update(self,dt, foods, coins, screen,floorrect):
        hdt = dt - self.dtu
        if self.beforeHunger <= hdt:
            W, H = self.Scale
            self.spriteM = pygame.Surface((W,H))
            self.spriteM.fill((0,0,255))
            self.spriteM.set_colorkey((0,0,255))
            self.spriteM.blit(self.sprite,(-W,0))
            if self.directionX !=-1:
                self.spriteM = pygame.transform.flip(self.spriteM,1,0)
        if  self.maxHunger <= hdt:
            self.FNP = True
        if self.trajectory == self.position:
            self.dt = dt
            self.trajectory = (random.uniform(80, (screen.get_size())[0] - 80),random.uniform(100, floorrect.top - 80))
            X,Y = self.trajectory
            self.Dx = X-self.position[0]
            self.Dy = Y-self.position[1]
            if self.Dx!=0:
                directionX = int(self.Dx/abs(self.Dx))
            else:
                directionX = 0
            if self.directionX != directionX:
                self.spriteM = pygame.transform.flip(self.spriteM,1,0)
                self.directionX = directionX
            if self.Dy!=0:
                self.directionY = self.Dy/abs(self.Dy)
            else:
                self.directionY = 0
        ndt = dt - self.dt
        # I am having issues with the speed and The detection
        x = self.directionX*self.velocitX*ndt
        if (x>self.Dx and self.directionX>0)or(x<self.Dx and self.directionX<0):
            x = 0
            self.position[0] = self.trajectory[0]
        y = self.directionY*self.velocitY*ndt
        if (y>self.Dy and self.directionY>0)or(y<self.Dy and self.directionY<0):
            y = 0
            self.position[1] = self.trajectory[1]
        self.position = (self.position[0]+x,self.position[1]+y)
        self.spriteRect.center = self.position
        # For testing positions
        print(self.directionX,self.directionY)
        print(self.spriteRect.center)
        print(self.trajectory)

    def draw(self,screen):
        screen.blit(self.spriteM,self.spriteRect)
# hunger               // Time remaining until it becomes hungry
# max_hunger           // Max hunger value
# hungry               // Boolean flag: true if hunger ≤ 0

# coin_timer           // Time elapsed since last coin
# coin_interval        // Random interval required to spawn a new coin


# Class requirements:
# 1. fish moving horizontally and bouncing off the tank walls
# 2. Vertical sinusoidal bobbing motion
# 3. Hunger management
# 4. If hungry and food exists then move towards closest Food
# 5. If hungry, coins are created slower


# Class functions:
# move_towards(target_x, target_y) - moves the fish towards the target position
# draw() - draws the fish on the screen


class Food:
    pass
# Class Variables:
# x, y       // Current position
# radius     // Size
# speed      // Fall speed


# Class functions:
# init(self, x, y) - initializes the food
# update(self, dt) - updates the food
# draw(self, surface) - draws the food on the surface


class Coin:
    pass
# Class Variables:
# x, y             // Position
# radius           // Rendering size + collision detection for clicks
# value            // Money gained when collected
# fall_speed       // Speed until it hits the floor
# resting          // True once coin hits the floor and stops moving


# Class functions:
# init(self, x, y, value) - initializes the coin
# update(self, dt) - updates the coin
# draw(self, surface) - draws the coin on the surface

# Create the main window for the game with size 800x600 pixels


screen = pygame.display.set_mode((WIDTH, HEIGHT))
def main():
    # Initialize all imported pygame modules
    pygame.init()
    # Set the window title to "Fish Tank"
    pygame.display.set_caption("Fish Tank")
    # Create a clock object to help control the game's frame rate
    clock = pygame.time.Clock()
    # Load a default font of size 27 for rendering text
    font = pygame.font.Font(None, FONT_SIZE)
    
    # Initialize lists to store fish, food, and coins
    fishes = []
    foods = []
    coins = []
    
    money = STARTING_MONEY
    
    running = True
    while running:
        dt =  pygame.time.get_ticks()/ 1000.0
        
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if event.button == 1:  # left click: drop food
                    if money >= FOOD_COST:
                        foods.append(Food(x, y))
                        money -= FOOD_COST
                elif event.button == 3:  # right click: collect coins
                    for coin in coins:
                        dx = x - coin.x
                        dy = y - coin.y
                        if dx ** 2 + dy ** 2 <= coin.radius ** 2:
                            money += coin.value
                            coins.remove(coin)
                            break
            
            elif event.type == pygame.KEYDOWN:
                # Press F to buy a new fish
                if event.key == pygame.K_f and money >= FISH_COST:
                    basicfish = Fish('fish/basicfish.png',(292*WIDTH/800,128*HEIGHT/600),1*WIDTH/800,1*HEIGHT/600,60,90,dt)
                    basicfish.position = (
                            random.uniform(80, WIDTH - 80),
                            random.uniform(100, TANK_FLOOR_Y - 80)
                    )
                    basicfish.trajectory = basicfish.position
                    fishes.append(basicfish)
                    money -= FISH_COST
        # update game state
        for fish in fishes:
            fish.update(dt, foods, coins, screen,floorrect)
            
        for food in foods:
            food.update(dt)
            
        for coin in coins:
            coin.update(dt)
            
        # drawing tank
        screen.blit(background1,background1reck)
        
        # tank floor
        pygame.draw.rect(screen, (0, 0, 0), floorrect)
        
        #draw enties
        for food in foods:
            food.draw(screen)
            
        for coin in coins:
            coin.draw(screen)
            
        for fish in fishes:
            fish.draw(screen)   
        # draw UI
        ui_text = f"Money: ${money} | Left-click: drop food (${FOOD_COST}) | Right-click: collect coins | F: buy fish (${FISH_COST})"
        text_surface = font.render(ui_text, True, (255, 155, 0))
        screen.blit(text_surface, (10, 10))
        
        pygame.display.flip()
        print(fishes)
        
    pygame.quit()
    sys.exit()
    
if __name__ == "__main__":
    main()
