import pygame
import random
import math
import sys

# Initialize pygame first (required before loading images or creating display)
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

def get_dynamic_constants(screen_size):
    width, height = screen_size
    TANK_FLOOR_Y = height - 50*(height/600)
    FONT_SIZE = int(27*(width/1280))
    # scaled assets sizes
    return width, height, TANK_FLOOR_Y, FONT_SIZE

class Fish:
    def __init__(self, sprite, beforeHunger, maxHunger, MoneyMax, dt):
        self.sprite_fp = sprite
        self.beforeHunger = beforeHunger
        self.maxHunger = maxHunger
        self.Mmax = MoneyMax
        self.init(dt)

    def init(self, dt, screen_size=None):
        if screen_size is None:
            screen_size = pygame.display.get_surface().get_size()
        # Load and rescale the sprite and set up necessary variables for drawing
        self.sprite = pygame.image.load(self.sprite_fp)
        w_scale, h_scale = get_scale_factors(screen_size)
        W, H = int(FISH_BASE_WIDTH * w_scale), int(FISH_BASE_HEIGHT * h_scale)
        self.Rescaled = (W, H)
        # Make fish a bit wider for animation
        self.sprite = pygame.transform.scale(self.sprite, (W * 2, H))
        self.velocitY = FISH_BASE_VELOCITY_Y * h_scale
        self.velocitX = FISH_BASE_VELOCITY_X * w_scale
        self.spriteM = pygame.Surface((W,H))
        self.spriteM.fill((0,0,255))
        self.spriteM.set_colorkey((0,0,255))
        self.spriteM.blit(self.sprite,(0,0))
        self.spriteRect = self.spriteM.get_rect(center=(0,0))
        self.directionX = -1
        self.directionY = 1
        self.sprite_flipped = False  # Track if sprite is visually flipped (facing right)
        self.trajectory = (0,0)
        self.foodMemory = []
        self.foodmane = []
        self.Ct = dt
        self.htu = dt 
        self.FNP = False # float in peace
        self.position = (0,0)

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
        
        # Reset position appropriately into bounds
        width, height, TANK_FLOOR_Y, _ = get_dynamic_constants(new_size)
        W, H = self.Rescaled
        # Clamp the position so fish stays in bounds
        min_x = W // 2
        max_x = width - W // 2
        min_y = H // 2
        max_y = TANK_FLOOR_Y - H // 2
        new_x = max(min_x, min(new_x, max_x))
        new_y = max(min_y, min(new_y, max_y))
        traj_x = max(min_x, min(traj_x, max_x))
        traj_y = max(min_y, min(traj_y, max_y))
        
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

    def update(self,dt, foods, coins, screen, floorrect, Coinclass):
        Newtrajectory = False
        current_hunger = dt - self.htu
        is_hungry = current_hunger >= self.beforeHunger / 2
        
        if len(foods) == 0:
            self.foodMemory = []
            self.foodmane = []
        
        # Only chase food when hungry
        if is_hungry and len(foods) > 0:
            # Find the closest food
            min_dist = float('inf')
            best_food = None
            for f in foods:
                fx, fy = f.SpriteR.center
                dist = (fx-self.spriteRect.center[0])**2 + (fy-self.spriteRect.center[1])**2
                if dist < min_dist:
                    min_dist = dist
                    best_food = f
            
            if best_food:
                food_pos = best_food.SpriteR.center
                # Clamp food target to valid fish bounds so fish can actually reach it
                W, H = self.Rescaled
                width, height = screen.get_size()
                _, _, TANK_FLOOR_Y, _ = get_dynamic_constants(screen.get_size())
                min_x = W // 2
                max_x = width - W // 2
                min_y = H // 2
                max_y = floorrect.top - H // 2
                clamped_food_pos = (
                    max(min_x, min(food_pos[0], max_x)),
                    max(min_y, min(food_pos[1], max_y))
                )
                
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
        speed = (self.velocitX + self.velocitY) / 2
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
                # Reset the sprite to reflect 'fed' state using re-scaled image
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

class Food:
    def __init__(self, x, y, dt, Sprite):
        self.sprite_fp = Sprite
        self.created_at = dt  # Track when food was created for spoil timer
        self.init(x, y, dt)

    def init(self, x, y, dt, screen_size=None):
        if screen_size is None:
            screen_size = pygame.display.get_surface().get_size()
        w_scale, h_scale = get_scale_factors(screen_size)
        SW = int(FOOD_BASE_WIDTH * w_scale)
        SH = int(FOOD_BASE_HEIGHT * h_scale)
        self.position = (x, y)
        self.velocity = FOOD_BASE_VELOCITY * h_scale
        self.dt = dt
        self.Sprite = pygame.image.load(self.sprite_fp)
        self.Sprite = pygame.transform.scale(self.Sprite,(SW,SH))
        self.SpriteR = self.Sprite.get_rect(center = self.position)
        self.Size = (SW, SH)

    def is_spoiled(self, dt):
        """Returns True if food has existed longer than FOOD_SPOIL_TIME"""
        return (dt - self.created_at) >= FOOD_SPOIL_TIME

    def update_on_resize(self, old_size, new_size):
        # Scale position proportionally to new screen size
        old_w, old_h = old_size
        new_w, new_h = new_size
        new_x = self.position[0] * new_w / old_w
        new_y = self.position[1] * new_h / old_h
        self.init(new_x, new_y, self.dt, new_size)

    def update(self,dt,floorrect):
        elapsed = dt - self.dt
        self.SpriteR.center = (self.position[0],self.position[1]+self.velocity*elapsed)
        if self.SpriteR.midbottom[1] > floorrect.top:
            self.SpriteR.midbottom = (self.SpriteR.midbottom[0],floorrect.top)

    def draw(self,screen):
        screen.blit(self.Sprite,self.SpriteR)

class Coin:
    def __init__(self, p, value, Sprite, dt):
        self.sprite_fp = Sprite
        self.value = value
        self.created_at = dt  # Track when coin was created for spoil timer
        self.init(p, dt)

    def init(self, p, dt, screen_size=None):
        if screen_size is None:
            screen_size = pygame.display.get_surface().get_size()
        self.Position = list(p)
        w_scale, h_scale = get_scale_factors(screen_size)
        SW = int(COIN_BASE_WIDTH * w_scale)
        SH = int(COIN_BASE_HEIGHT * h_scale)
        self.Size = (SW, SH)
        self.velocity = COIN_BASE_VELOCITY * h_scale
        self.Sprite = pygame.image.load(self.sprite_fp)
        self.Sprite = pygame.transform.scale(self.Sprite, self.Size)
        self.Spriter = self.Sprite.get_rect(center=self.Position)
        self.dt = dt

    def update_on_resize(self, old_size, new_size):
        # Scale position proportionally to new screen size
        old_w, old_h = old_size
        new_w, new_h = new_size
        new_x = self.Position[0] * new_w / old_w
        new_y = self.Position[1] * new_h / old_h
        self.Position = [new_x, new_y]
        self.init(self.Position, self.dt, new_size)

    def update(self, dt, floorrect):
        y = self.velocity * (dt-self.dt)
        self.Spriter.center = (self.Position[0],self.Position[1]+y)
        if self.Spriter.midbottom[1] > floorrect.top:
            self.Spriter.midbottom = (self.Spriter.midbottom[0],floorrect.top)
    def draw(self, surface):
        surface.blit(self.Sprite, self.Spriter)

    def is_spoiled(self, dt):
        """Returns True if coin has existed longer than COIN_SPOIL_TIME"""
        return (dt - self.created_at) >= COIN_SPOIL_TIME

def load_and_resize_background(screen_size):
    width, height, TANK_FLOOR_Y, _ = get_dynamic_constants(screen_size)
    bg = pygame.image.load('background.png')
    bg = pygame.transform.scale(bg, (width, int(TANK_FLOOR_Y)))
    bgrect = bg.get_rect(topleft=(0,0))
    return bg, bgrect

def get_floor_rect(screen_size):
    width, height, TANK_FLOOR_Y, _ = get_dynamic_constants(screen_size)
    return pygame.Rect(0, TANK_FLOOR_Y, width, height - TANK_FLOOR_Y)

def main():
    # Set the window title to "Fish Tank"
    pygame.display.set_caption("Fish Tank")
    # Create the main, resizable window
    screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    # Initial dynamic values
    WIDTH, HEIGHT, TANK_FLOOR_Y, FONT_SIZE = get_dynamic_constants(screen.get_size())
    background1, background1reck = load_and_resize_background(screen.get_size())
    floorrect = get_floor_rect(screen.get_size())
    font = pygame.font.Font(None, FONT_SIZE)
    # Initialize lists to store fish, food, and coins
    fishes = []
    foods = []
    coins = []

    money = STARTING_MONEY

    running = True
    while running:
        dt =  pygame.time.get_ticks()/ 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                # Store old size before resizing
                old_size = screen.get_size()
                new_size = event.size
                # Automatic re-scale of all game assets
                WIDTH, HEIGHT, TANK_FLOOR_Y, FONT_SIZE = get_dynamic_constants(new_size)
                screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
                background1, background1reck = load_and_resize_background(new_size)
                floorrect = get_floor_rect(new_size)
                font = pygame.font.Font(None, FONT_SIZE)
                # update all fish, foods, coins for screen_size
                for fish in fishes:
                    fish.update_on_resize(old_size, new_size)
                for food in foods:
                    food.update_on_resize(old_size, new_size)
                for coin in coins:
                    coin.update_on_resize(old_size, new_size)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if event.button == 1:  # left click: collect coin or drop food
                    # First check if clicking on a coin
                    coin_clicked = False
                    click = pygame.Rect(x, y, 1, 1)
                    for coin in coins:
                        if coin.Spriter.colliderect(click):
                            money += coin.value
                            coins.remove(coin)
                            coin_clicked = True
                            break
                    # If no coin was clicked, drop food
                    if not coin_clicked and money >= FOOD_COST:
                        ff = Food(x, y, dt, 'ff.png')
                        foods.append(ff)
                        money -= FOOD_COST

            elif event.type == pygame.KEYDOWN:
                # Press F to buy a new fish
                if event.key == pygame.K_f and money >= FISH_COST:
                    width, height, TANK_FLOOR_Y, _ = get_dynamic_constants(screen.get_size())
                    basicfish = Fish(
                        'fish/basicfish.png',  # Sprite image file
                        60,                    # beforeHunger: seconds until hungry
                        90,                    # maxHunger: seconds until death if unfed
                        15,                    # MoneyMax: seconds between coin drops
                        dt                     # dt: current game time for timers
                    )
                    # Make sure the new fish is placed within bounds
                    W, H = basicfish.Rescaled
                    min_x = W // 2
                    max_x = width - W // 2
                    min_y = H // 2
                    max_y = TANK_FLOOR_Y - H // 2
                    rand_x = random.uniform(min_x, max_x)
                    rand_y = random.uniform(min_y, max_y)
                    basicfish.position = (rand_x, rand_y)
                    basicfish.spriteRect.center = basicfish.position
                    basicfish.trajectory = basicfish.position
                    fishes.append(basicfish)
                    money -= FISH_COST
        # update game state
        for food in foods:
            food.update(dt, floorrect)
        # Remove spoiled food
        foods[:] = [food for food in foods if not food.is_spoiled(dt)]
        for coin in coins:
            coin.update(dt, floorrect)
        # Remove spoiled coins
        coins[:] = [coin for coin in coins if not coin.is_spoiled(dt)]
        for fish in fishes:
            fish.update(dt, foods, coins, screen, floorrect, Coin)
            if fish.FNP:
                fishes.remove(fish)

        # Drawing tank
        screen.blit(background1, background1reck)
        # tank floor
        pygame.draw.rect(screen, (0, 0, 0), floorrect)
        # Draw entities
        for food in foods:
            food.draw(screen)

        for fish in fishes:
            fish.draw(screen)

        for coin in coins:
            coin.draw(screen)
        # draw UI
        ui_text = f"Money: ${money} | Click: drop food (${FOOD_COST}) or collect coins | F: buy fish (${FISH_COST})"
        text_surface = font.render(ui_text, True, (255, 155, 0))
        screen.blit(text_surface, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
