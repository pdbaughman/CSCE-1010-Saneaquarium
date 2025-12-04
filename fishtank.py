import pygame
import random
import math
import sys

# Initialize pygame first
pygame.init()

# --- Initial base resolution ---
BASE_WIDTH = 1280
BASE_HEIGHT = 720
FPS = 60

STARTING_MONEY = 200
FOOD_COST = 5   #default is 5
FISH_COST = 50  #default is 50
FOOD_SPOIL_TIME = 30  # Food disappears after x seconds
COIN_SPOIL_TIME = 30  # Coins disappear after x seconds

# Fish base (unscaled) values
FISH_BASE_WIDTH = 146
FISH_BASE_HEIGHT = 64
FISH_BASE_VELOCITY_X = 100
FISH_BASE_VELOCITY_Y = 100

# Food base (unscaled) values
FOOD_BASE_WIDTH = 30
FOOD_BASE_HEIGHT = 30
FOOD_BASE_VELOCITY = 50

# Coin base (unscaled) values
COIN_BASE_WIDTH = 50
COIN_BASE_HEIGHT = 50
COIN_BASE_VELOCITY = 10

def get_scale_factors(current_size):
    # returns width_scale, height_scale
    return current_size[0] / BASE_WIDTH, current_size[1] / BASE_HEIGHT

# Function to get constants for screen resizing
def get_dynamic_constants(screen_size):
    width, height = screen_size
    TANK_FLOOR_Y = height - 50*(height/600)
    FONT_SIZE = int(27*(width/1280))
    # scaled assets sizes
    return width, height, TANK_FLOOR_Y, FONT_SIZE

# Fush class
# - Manages the fish entity's sprite, position, movement, and behavior.
# - Handles sprite scaling, animation, and direction flipping.
# - Tracks hunger state, food memory, and coin collection.
# - Implements fish movement logic based on target food/coin positions.
# - Manages sprite initialization, resizing, and updates.
# - Handles fish collision detection with food and coins.
# - Manages fish hunger state and coin production.
# - Manages fish sprite flipping and direction.
class Fish:
    def __init__(self, sprite, beforeHunger, maxHunger, MoneyMax, dt):
        self.sprite_fp = sprite # sprite file path
        self.beforeHunger = beforeHunger # time until fish is hungry
        self.maxHunger = maxHunger # time until fish is full
        self.Mmax = MoneyMax # time until fish can produce coins
        self.init(dt) # initialize fish

    def init(self, dt, screen_size=None):
        if screen_size is None:   # get current screen size
            screen_size = pygame.display.get_surface().get_size()
        # Load and rescale the sprite and set up necessary variables for drawing
        self.sprite = pygame.image.load(self.sprite_fp)   # load sprite image
        w_scale, h_scale = get_scale_factors(screen_size) # get scale factors
        W, H = int(FISH_BASE_WIDTH * w_scale), int(FISH_BASE_HEIGHT * h_scale)  # get scaled dimensions
        self.Rescaled = (W, H)  # store scaled dimensions
        # Make fish a bit wider for animation
        self.sprite = pygame.transform.scale(self.sprite, (W * 2, H)) # stretch sprite a bit
        self.velocityY = FISH_BASE_VELOCITY_Y * h_scale # set vertical velocity
        self.velocityX = FISH_BASE_VELOCITY_X * w_scale # set horizontal velocity
        self.spriteM = pygame.Surface((W,H)) # create surface for sprite
        self.spriteM.fill((0,0,255))
        self.spriteM.set_colorkey((0,0,255)) # set color key
        self.spriteM.blit(self.sprite,(0,0)) # blit sprite onto surface
        self.spriteRect = self.spriteM.get_rect(center=(0,0)) # get rect for sprite
        self.directionX = -1 # set initial direction to left
        self.directionY = 1 # set initial direction to up
        self.sprite_flipped = False  # Track if sprite is facing right
        self.trajectory = (0,0) # set initial trajectory to center
        self.foodMemory = [] # set initial food memory to empty
        self.foodmane = [] # set initial food memory to empty
        self.Ct = dt # set initial coin timer
        self.htu = dt # set initial hunger timer
        self.FNP = False # float in peace (is fish dead)
        self.position = (0,0) # set initial position to center

    # update_on_resize function
    # - Scales the fish's sprite and position when the screen is resized, keeping visuals consistent.
    # - Adjusts sprite and trajectory target according to new screen size by scaling their coordinates.
    # - Saves the current direction and flipping state before reinitializing the sprite for new size.
    # - Calls the init() function to regenerate the sprite image and visual rect with new scaling.
    # - Clamps fish position and trajectory within the bounds of the resized tank, preventing out-of-bounds.
    # - Updates the current position, time, and trajectory vector after resizing.
    # - Restores direction and flipping state to preserve fish facing orientation after resizing.
    def update_on_resize(self, old_size, new_size):
        # Scale the ACTUAL visual position (spriteRect.center) proportionally
        old_w, old_h = old_size
        new_w, new_h = new_size
        current_x, current_y = self.spriteRect.center
        new_x = current_x * new_w / old_w
        new_y = current_y * new_h / old_h
        # Also scale trajectory target
        traj_x = self.trajectory[0] * new_w / old_w
        traj_y = self.trajectory[1] * new_h / old_h
        
        # Save the old state BEFORE init() resets it
        old_directionX = self.directionX
        old_directionY = self.directionY
        was_flipped = self.sprite_flipped
        
        # Redo image etc for new screen size
        self.init(self.Ct, screen_size=new_size)
        
        # Reset position into bounds
        width, height, TANK_FLOOR_Y, _ = get_dynamic_constants(new_size)
        W, H = self.Rescaled
        # Clamp the position to keep fish in bounds
        min_x = W // 2
        max_x = width - W // 2
        min_y = H // 2
        max_y = TANK_FLOOR_Y - H // 2
        new_x = max(min_x, min(new_x, max_x)) # clamp x position
        new_y = max(min_y, min(new_y, max_y)) # clamp y position
        traj_x = max(min_x, min(traj_x, max_x)) # clamp trajectory x
        traj_y = max(min_y, min(traj_y, max_y)) # clamp trajectory y
        
        # Set current visual position
        self.spriteRect.center = (new_x, new_y)
        self.trajectory = (traj_x, traj_y)
        
        # Restart trajectory from current position to avoid jump
        self.position = (new_x, new_y)
        self.dt = pygame.time.get_ticks() / 1000.0
        
        # Recalculate distance to target
        self.Dx = traj_x - new_x
        self.Dy = traj_y - new_y
        
        # Restore the old direction and flip state
        # init() resets sprite to unflipped (facing left)
        # If sprite was flipped before, flip it again to restore
        if was_flipped:
            self.spriteM = pygame.transform.flip(self.spriteM, 1, 0)
        self.sprite_flipped = was_flipped
        self.directionX = old_directionX
        self.directionY = old_directionY

    # The update() function manages the main real-time behavior of the fish entity in the game:
    # - It determines whether the fish is hungry, based on elapsed time and hunger threshold.
    # - If no food is present, it clears any memory of food targets.
    # - When hungry and food is available, it finds the closest food item using distance calculations.
    # - It ensures the fish targets food within valid screen/tank bounds (clamping coordinates).
    # - If a new food target is found, it initiates a new trajectory, otherwise it updates the target's position.
    # - If there is no trajectory (fish is at its current destination), the fish will prepare to select a new random target location.
    # The function handles the fish movement logic and reacts to environmental cues (food/coindrops, boundaries).
    
    # I changed the time since start approach to time since last frame approach
    # added bounds checking to prevent fish from leaving the screen
    # replaced the food intercept system with food chasing system
    # added distance based food target selection
    # checks for "unreachable" targets and resets trajectory to a new random location
    def update(self,dt, foods, coins, screen, floorrect, Coinclass):
        Newtrajectory = False
        current_hunger = dt - self.htu # get current hunger
        is_hungry = current_hunger >= self.beforeHunger / 2 # check if hungry
        
        if len(foods) == 0: # if no food, clear food memory
            self.foodMemory = [] # clear food memory
            self.foodmane = [] # clear food memory
        
        # Only chase food when hungry
        if is_hungry and len(foods) > 0: # if hungry and food, find closest food
            min_dist = float('inf') # set initial minimum distance to infinity
            best_food = None # set initial best food to None
            for f in foods: # loop through all food
                fx, fy = f.SpriteR.center
                dist = (fx-self.spriteRect.center[0])**2 + (fy-self.spriteRect.center[1])**2
                if dist < min_dist:
                    min_dist = dist
                    best_food = f
            
            if best_food:
                food_pos = best_food.SpriteR.center # get food position
                # Clamp food target to valid fish bounds so fish can actually reach it
                W, H = self.Rescaled # get scaled dimensions
                width, height = screen.get_size() # get screen size
                _, _, TANK_FLOOR_Y, _ = get_dynamic_constants(screen.get_size()) # get dynamic constants
                min_x = W // 2 # get minimum x
                max_x = width - W // 2 # get maximum x
                min_y = H // 2 # get minimum y
                max_y = floorrect.top - H // 2 # get maximum y
                clamped_food_pos = (max(min_x, min(food_pos[0], max_x)), max(min_y, min(food_pos[1], max_y))) # clamp food position
                
                # Check if we're starting to chase a NEW food (or first time chasing)
                is_new_target = (len(self.foodmane) == 0 or 
                                self.foodmane[0] not in foods or 
                                self.foodmane[0] != best_food)
                
                if is_new_target:
                    # New food target - start fresh trajectory
                    self.foodmane = [best_food]
                    self.trajectory = clamped_food_pos
                    Newtrajectory = True
                else:
                    # Same food, just update target position (don't reset timer)
                    self.trajectory = clamped_food_pos

        elif self.trajectory == self.position:
            width, height = screen.get_size()
            W, H = self.Rescaled
            _, _, TANK_FLOOR_Y, _ = get_dynamic_constants(screen.get_size())
            # Calculate bounds so the fish never leaves the screen
            min_x = W // 2
            max_x = width - W // 2
            min_y = H // 2
            max_y = floorrect.top - H // 2
            self.trajectory = (
                random.uniform(min_x, max_x),
                random.uniform(min_y, max_y)
            )
            Newtrajectory = True
        # Initialize last_dt if not set
        if not hasattr(self, 'last_dt'):
            self.last_dt = dt
            
        # Calculate frame delta time
        frame_dt = dt - self.last_dt
        self.last_dt = dt
        
        # Calculate the new center but keep it in bounds
        W, H = self.Rescaled
        width, height = screen.get_size()
        _, _, TANK_FLOOR_Y, _ = get_dynamic_constants(screen.get_size())
        min_x = W // 2
        max_x = width - W // 2
        min_y = H // 2
        max_y = floorrect.top - H // 2

        # Calculate direction from current position to target (recalculated each frame)
        current_pos = self.spriteRect.center
        target_x, target_y = self.trajectory
        dx = target_x - current_pos[0]
        dy = target_y - current_pos[1]
        dist_to_target = math.sqrt(dx**2 + dy**2)
        
        # Handle sprite flipping based on horizontal direction
        if dx != 0:
            want_facing_right = (dx > 0)
            if want_facing_right != self.sprite_flipped:
                self.spriteM = pygame.transform.flip(self.spriteM, 1, 0)
                self.sprite_flipped = want_facing_right
            self.directionX = 1 if dx > 0 else -1
        
        # Calculate movement for this frame
        speed = (self.velocityX + self.velocityY) / 2
        move_dist = speed * frame_dt
        
        # Check if we've reached or will pass the target this frame
        if dist_to_target <= move_dist or dist_to_target < 1:
            # Snap to target
            new_center_x = target_x
            new_center_y = target_y
            self.position = self.trajectory
        else:
            # Move toward target
            dir_x = dx / dist_to_target
            dir_y = dy / dist_to_target
            new_center_x = current_pos[0] + dir_x * move_dist
            new_center_y = current_pos[1] + dir_y * move_dist

        # Clamp fish so it can't go outside the game area (left/right/top/bottom)
        clamped_center_x = max(min_x, min(new_center_x, max_x))
        clamped_center_y = max(min_y, min(new_center_y, max_y))

        self.spriteRect.center = (clamped_center_x, clamped_center_y)

        if self.spriteRect.midbottom[1] > floorrect.top:
            self.spriteRect.midbottom = (self.spriteRect.midbottom[0],floorrect.top)

        # Check if fish is stuck at a boundary (target is outside valid bounds)
        # If we're clamped and the target is unreachable, reset to pick a new trajectory
        clamped_target_x = max(min_x, min(target_x, max_x))
        clamped_target_y = max(min_y, min(target_y, max_y))
        dist_to_clamped_target = math.sqrt((clamped_target_x - clamped_center_x)**2 + 
                                            (clamped_target_y - clamped_center_y)**2)
        if dist_to_clamped_target < 1:
            # We've reached as close as we can get to the target (it was outside bounds)
            self.position = self.spriteRect.center
            self.trajectory = self.spriteRect.center

        CCt = dt - self.Ct
        # Food collision detection
        current_hunger = dt - self.htu
        for i in range(len(foods)-1,-1,-1):
            # Fish can only eat when at half hunger or more
            if self.spriteRect.colliderect(foods[i].SpriteR) and current_hunger >= self.beforeHunger / 2:
                del foods[i]
                # Each food only fills hunger by half (not fully reset)
                self.htu = dt - (current_hunger / 2)
                # Reset the sprite to reflect fed state using re-scaled image
                self.spriteM = pygame.Surface(self.Rescaled)
                self.spriteM.fill((0,0,255))
                self.spriteM.set_colorkey((0,0,255))
                self.spriteM.blit(self.sprite,(0,0))
                if self.sprite_flipped:
                    self.spriteM = pygame.transform.flip(self.spriteM,1,0)
                # After eating, reset position and trajectory to resume wandering
                current_pos = self.spriteRect.center
                self.position = current_pos
                self.trajectory = current_pos
                break
        # hunger detection
        hdt = dt - self.htu
        if self.beforeHunger <= hdt:
            self.spriteM = pygame.Surface(self.Rescaled)
            self.spriteM.fill((0,0,255))
            self.spriteM.set_colorkey((0,0,255))
            self.spriteM.blit(self.sprite,(-self.Rescaled[0],0))
            if self.sprite_flipped:
                self.spriteM = pygame.transform.flip(self.spriteM,1,0)
        # coin production
        if  self.maxHunger <= hdt:
            self.FNP = True
        if self.Mmax <= CCt:
            self.Ct = dt
            coin = Coinclass(self.spriteRect.center, 10, 'money.png', dt)
            coins.append(coin)

    def draw(self,screen):
        screen.blit(self.spriteM,self.spriteRect)

# Food class
# - Manages the food entity's sprite, position, movement, and behavior.
# - Handles sprite scaling, animation, and direction flipping.
# - Tracks food expiration timer.
# - Manages food initialization, resizing, and updates.
# - Handles food collision detection with fish.
# - Manages food sprite flipping and direction.

class Food:
    def __init__(self, x, y, dt, Sprite):
        self.sprite_fp = Sprite
        self.created_at = dt  # Track when food was created for spoil timer
        self.init(x, y, dt)

    # seperate init function (that can be called without creating a new food object)
    def init(self, x, y, dt, screen_size=None):
        if screen_size is None: # get current screen size
            screen_size = pygame.display.get_surface().get_size()
        w_scale, h_scale = get_scale_factors(screen_size) # get scale factors
        SW = int(FOOD_BASE_WIDTH * w_scale) # get scaled dimensions
        SH = int(FOOD_BASE_HEIGHT * h_scale) # get scaled dimensions
        self.position = (x, y) # set initial position
        self.velocity = FOOD_BASE_VELOCITY * h_scale # set vertical velocity
        self.dt = dt # set initial food timer
        self.Sprite = pygame.image.load(self.sprite_fp) # load sprite image
        self.Sprite = pygame.transform.scale(self.Sprite,(SW,SH)) # scale sprite
        self.SpriteR = self.Sprite.get_rect(center = self.position) # get rect for sprite
        self.Size = (SW, SH) # store scaled dimensions

    def is_spoiled(self, dt):
        # Returns True if food has existed longer than FOOD_SPOIL_TIME
        return (dt - self.created_at) >= FOOD_SPOIL_TIME

    def update_on_resize(self, old_size, new_size):
        # Scale position proportionally to new screen size
        old_w, old_h = old_size
        new_w, new_h = new_size
        new_x = self.position[0] * new_w / old_w # scale x position
        new_y = self.position[1] * new_h / old_h # scale y position
        self.init(new_x, new_y, self.dt, new_size) # call init function to update food position

    def update(self,dt,floorrect):
        elapsed = dt - self.dt # get elapsed time since last frame
        self.SpriteR.center = (self.position[0],self.position[1]+self.velocity*elapsed) # update food position
        if self.SpriteR.midbottom[1] > floorrect.top:
            self.SpriteR.midbottom = (self.SpriteR.midbottom[0],floorrect.top) # keep food in bounds

    def draw(self,screen):
        screen.blit(self.Sprite,self.SpriteR) # draw food

# Coin class
# - Manages the coin entity's position, movement, and behavior.
# - Handles sprite scaling, animation, and direction flipping.
# - Tracks coin expiration timer.
# - Manages coin initialization, resizing, and updates.
# - Handles coin collision detection with fish.
# - Manages coin sprite flipping and direction.
class Coin:
    def __init__(self, p, value, Sprite, dt):
        self.sprite_fp = Sprite
        self.value = value
        self.created_at = dt  # Track when coin was created for spoil timer
        self.init(p, dt)

    # seperate init function (that can be called without creating a new coin object)
    def init(self, p, dt, screen_size=None):
        if screen_size is None:
            screen_size = pygame.display.get_surface().get_size()
        self.Position = list(p) # convert position to list
        w_scale, h_scale = get_scale_factors(screen_size) # get scale factors
        SW = int(COIN_BASE_WIDTH * w_scale)
        SH = int(COIN_BASE_HEIGHT * h_scale) # get scaled dimensions
        self.Size = (SW, SH) # store scaled dimensions
        self.velocity = COIN_BASE_VELOCITY * h_scale # set vertical velocity
        self.Sprite = pygame.image.load(self.sprite_fp) # load sprite image
        self.Sprite = pygame.transform.scale(self.Sprite, self.Size) # scale sprite
        self.Spriter = self.Sprite.get_rect(center=self.Position) # get rect for sprite
        self.dt = dt # set initial coin timer

    def update_on_resize(self, old_size, new_size):
        # Scale position proportionally to new screen size
        old_w, old_h = old_size
        new_w, new_h = new_size
        new_x = self.Position[0] * new_w / old_w # scale x position
        new_y = self.Position[1] * new_h / old_h # scale y position
        self.Position = [new_x, new_y]
        self.init(self.Position, self.dt, new_size) # call init function to update coin position

    def update(self, dt, floorrect): 
        y = self.velocity * (dt-self.dt) # update coin position
        self.Spriter.center = (self.Position[0],self.Position[1]+y)
        if self.Spriter.midbottom[1] > floorrect.top:
            self.Spriter.midbottom = (self.Spriter.midbottom[0],floorrect.top) # keep coin in bounds
    def draw(self, surface):
        surface.blit(self.Sprite, self.Spriter) # draw coin

    def is_spoiled(self, dt):
        # Returns True if coin has existed longer than COIN_SPOIL_TIME
        return (dt - self.created_at) >= COIN_SPOIL_TIME

def load_and_resize_background(screen_size):
    width, height, TANK_FLOOR_Y, _ = get_dynamic_constants(screen_size) # get dynamic constants
    bg = pygame.image.load('background.png') # load background image
    bg = pygame.transform.scale(bg, (width, int(TANK_FLOOR_Y))) # scale background image
    bgrect = bg.get_rect(topleft=(0,0)) # get rect for background
    return bg, bgrect

def get_floor_rect(screen_size):
    width, height, TANK_FLOOR_Y, _ = get_dynamic_constants(screen_size) # get dynamic constants
    return pygame.Rect(0, TANK_FLOOR_Y, width, height - TANK_FLOOR_Y) # get floor rect


# The main function serves as the main game loop and entry point for the Fish Tank game.
# Features:
# - Sets the window title and initializes a resizable display window.
# - Initializes dynamic game constants based on the current window size, such as tank dimensions and font size.
# - Loads and scales the background image appropriate to the tank size.
# - Determines the position and dimensions of the tank floor.
# - Sets up the font for rendering text in the game.
# - Initializes lists to keep track of all fish, food, and coins currently in the tank.
# - Sets the starting amount of in-game currency (money).
# - Enters a loop (`while running`) that persists until the player closes the window.
#     - On each loop iteration:
#         - Updates the current time (`dt`) for use in animations and timers.
#         - Processes Pygame events:
#             - Handles window close requests.
#             - Handles window resizing, updating all dynamic elements and their positions/scaling accordingly.
#             - Handles mouse clicks for collecting coins or dropping food depending on context and available funds.
#         - (Additional game logic, updating positions, drawing, spawning, etc. is handled elsewhere in the loop.)
# - Manages interaction between player actions (mouse), graphical updates, and the various objects in the game (fish, food, coins).

def main():
    pygame.display.set_caption("Fish Tank") # set window title
    screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE) # create main, resizable window
    clock = pygame.time.Clock() # create clock

    WIDTH, HEIGHT, TANK_FLOOR_Y, FONT_SIZE = get_dynamic_constants(screen.get_size()) # get dynamic constants
    background1, background1reck = load_and_resize_background(screen.get_size()) # load and resize background
    floorrect = get_floor_rect(screen.get_size()) # get floor rect
    font = pygame.font.Font(None, FONT_SIZE) # create font
    fishes = [] # initialize list to store fish
    foods = [] # initialize list to store food
    coins = [] # initialize list to store coins
    money = STARTING_MONEY # set starting money
    running = True # set running to True
    while running:
        dt =  pygame.time.get_ticks()/ 1000.0 # get time since start
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False # set running to False
            elif event.type == pygame.VIDEORESIZE:
                old_size = screen.get_size() # store old size
                new_size = event.size # get new size
                WIDTH, HEIGHT, TANK_FLOOR_Y, FONT_SIZE = get_dynamic_constants(new_size) # get dynamic constants
                screen = pygame.display.set_mode(new_size, pygame.RESIZABLE) # create new window
                background1, background1reck = load_and_resize_background(new_size) # load and resize background
                floorrect = get_floor_rect(new_size) # get floor rect
                font = pygame.font.Font(None, FONT_SIZE) # create font
                # update all fish, foods, coins for screen_size
                for fish in fishes:
                    fish.update_on_resize(old_size, new_size) # update fish
                for food in foods:
                    food.update_on_resize(old_size, new_size) # update food
                for coin in coins:
                    coin.update_on_resize(old_size, new_size) # update coin

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos # get mouse position
                if event.button == 1:  # left click: collect coin or drop food
                    # First check if clicking on a coin
                    coin_clicked = False
                    click = pygame.Rect(x, y, 1, 1)
                    for coin in coins:
                        if coin.Spriter.colliderect(click):
                            money += coin.value # add coin value to money
                            coins.remove(coin) # remove coin from list
                            coin_clicked = True
                            break
                    # If no coin was clicked, drop food
                    if not coin_clicked and money >= FOOD_COST:
                        ff = Food(x, y, dt, 'ff.png') # create new food
                        foods.append(ff) # add food to list
                        money -= FOOD_COST # subtract food cost from money

            elif event.type == pygame.KEYDOWN:
                # Press F to buy a new fish
                if event.key == pygame.K_f and money >= FISH_COST:
                    width, height, TANK_FLOOR_Y, _ = get_dynamic_constants(screen.get_size()) # get dynamic constants
                    basicfish = Fish(
                        'fish/basicfish.png',  # Sprite image file
                        60,                    # beforeHunger: seconds until hungry
                        90,                    # maxHunger: seconds until death if unfed
                        15,                    # MoneyMax: seconds between coin drops
                        dt                     # dt: current game time for timers
                    )
                    # Make sure the new fish is placed within bounds
                    W, H = basicfish.Rescaled # get scaled dimensions
                    min_x = W // 2 # get minimum x
                    max_x = width - W // 2 # get maximum x
                    min_y = H // 2 # get minimum y
                    max_y = TANK_FLOOR_Y - H // 2 # get maximum y
                    rand_x = random.uniform(min_x, max_x) # get random x
                    rand_y = random.uniform(min_y, max_y) # get random y
                    basicfish.position = (rand_x, rand_y) # set position
                    basicfish.spriteRect.center = basicfish.position # set sprite rect center
                    basicfish.trajectory = basicfish.position # set trajectory
                    fishes.append(basicfish) # add fish to list
                    money -= FISH_COST # subtract fish cost from money
        # update game state
        for food in foods:
            food.update(dt, floorrect) # update food
        # Remove spoiled food
        foods[:] = [food for food in foods if not food.is_spoiled(dt)] # remove spoiled food
        for coin in coins:
            coin.update(dt, floorrect) # update coin
        # Remove spoiled coins
        coins[:] = [coin for coin in coins if not coin.is_spoiled(dt)] # remove spoiled coins
        for fish in fishes:
            fish.update(dt, foods, coins, screen, floorrect, Coin)
            if fish.FNP:
                fishes.remove(fish) # remove fish from list

        # Drawing tank
        screen.blit(background1, background1reck) # draw background
        # tank floor
        pygame.draw.rect(screen, (0, 0, 0), floorrect)
        # Draw entities
        for food in foods:
            food.draw(screen) # draw food

        for fish in fishes:
            fish.draw(screen) # draw fish

        for coin in coins:
            coin.draw(screen) # draw coin
        # draw UI
        ui_text = f"Money: ${money} | Click: drop food (${FOOD_COST}) or collect coins | F: buy fish (${FISH_COST})"
        text_surface = font.render(ui_text, True, (255, 155, 0))
        screen.blit(text_surface, (10, 10)) # draw UI text

        pygame.display.flip() # update display
        clock.tick(FPS) # tick clock

    pygame.quit() # quit pygame
    sys.exit() # exit program

if __name__ == "__main__":
    main() # run main function
