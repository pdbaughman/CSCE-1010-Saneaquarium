import pygame
import random
import math
import sys

# Constants for the game
WIDTH = 800
HEIGHT = 600
FPS = 60

TANK_FLOOR_Y = HEIGHT - 50

FONT_SIZE = 24
STARTING_MONEY = 200
FOOD_COST = 5
FISH_COST = 50


class Fish:
    pass
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


def main():
    # Initialize all imported pygame modules
    pygame.init()
    # Create the main window for the game with size 800x600 pixels
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    # Set the window title to "Fish Tank"
    pygame.display.set_caption("Fish Tank")
    # Create a clock object to help control the game's frame rate
    clock = pygame.time.Clock()
    # Load a default font of size 24 for rendering text
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
                    fishes.append(
                        Fish(
                            random.randint(80, WIDTH - 80),
                            random.randint(100, TANK_FLOOR_Y - 80),
                        )
                    )
                    money -= FISH_COST

        # update game state
        for fish in fishes:
            fish.update(dt, foods, coins)
            
        for food in foods:
            food.update(dt)
            
        for coin in coins:
            coin.update(dt)
            
        # drawing tank
        screen.fill((0, 0, 0))
        
        # tank floor
        pygame.draw.rect(screen, (0, 0, 0), (0, TANK_FLOOR_Y, WIDTH, HEIGHT - TANK_FLOOR_Y))
        
        #draw enties
        for food in foods:
            food.draw(screen)
            
        for coin in coins:
            coin.draw(screen)
            
        for fish in fishes:
            fish.draw(screen)
            
        # draw UI
        ui_text = f"Money: ${money} | Left-click: drop food (${FOOD_COST}) | Right-click: collect coins | F: buy fish (${FISH_COST})"
        text_surface = font.render(ui_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        pygame.display.flip()
        
    pygame.quit()
    sys.exit()
    
if __name__ == "__main__":
    main()