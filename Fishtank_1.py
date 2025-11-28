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
    def __init__(self, sprite, Scale):
        self.sprite = pygame.image.load(sprite)
        self.position = (0,0)
        W, H = Scale
        self.sprite = pygame.transform.scale(self.sprite,(W*2,H))
        self.spriteM = pygame.Surface((W,H))
        self.spriteM.fill((0,0,255))
        self.spriteM.set_colorkey((0,0,255))
        self.spriteM.blit(self.sprite,(0,0))
        self.spriteRect = self.spriteM.get_rect(center = self.position)
    def update(self,dt, foods, coins):
        self.spriteRect.center = self.position
    def draw(self,screen):
        screen.blit(self.spriteM,self.spriteRect)
    
# Class Variables:
# x, y                 // Current position
# speed                // Horizontal movement speed
# direction            // -1 for left, +1 for right
# vertical_offset      // For sinusoidal bobbing motion
# vertical_speed       // Rate the fish “bobs” vertically

# size                 // Fish size for drawing + collision
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
        dt = clock.tick(FPS) / 1000.0
        
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
                    for coin in coins[:]:
                        dx = x - coin.x
                        dy = y - coin.y
                        if dx * dx + dy * dy <= coin.radius ** 2:
                            money += coin.value
                            coins.remove(coin)
                            break
            
            elif event.type == pygame.KEYDOWN:
                # Press F to buy a new fish
                if event.key == pygame.K_f and money >= FISH_COST:
                    basicfish = Fish('fish/basicfish.png',(292,128))
                    basicfish.position = (
                            random.uniform(80, WIDTH - 80),
                            random.uniform(100, TANK_FLOOR_Y - 80)
                    )
                    fishes.append(basicfish)
                    money -= FISH_COST

        # update game state
        for fish in fishes:
            fish.update(dt, foods, coins)
            
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
        
    pygame.quit()
    sys.exit()
    
if __name__ == "__main__":
    main()
