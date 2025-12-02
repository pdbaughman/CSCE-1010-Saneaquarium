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
    def __init__(self, sprite,Scale,velocitX,velocitY,beforeHunger,maxHunger,MoneyMax,moneymid,dt):
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
        self.foodMemory = []
        self.foodmane = -1
        self.Ct = dt
        self.Mmax = MoneyMax
        self.Mmid = moneymid
        self.htu = dt 
        self.FNP = False # float in peace
    def update(self,dt, foods, coins, screen,floorrect,Coinclass):
        Newtrajectory = False
        if len(foods) == 0:
            self.foodMemory = []
        print(foods,self.foodMemory)
        if self.foodMemory != foods:
            print(True)
            nFoods = foods[:]
            self.foodMemory = nFoods
            velocity = foods[0].velocity
            foodPm = (0,0)
            foodmane = 0
            for i in range(0,len(foods)):
                foodP = foods[i].SpriteR.center
                if i > 0:
                    fx,fy = foodPm
                    nfx,nfy = foodP
                    if ((fx-self.spriteRect.center[0])**2+(fy - self.spriteRect.center[1])**2)<((nfx-self.spriteRect.center[0])**2+(nfy - self.spriteRect.center[1])**2):
                        foodP = foodPm
                    else:
                        foodmane = i
                foodPm = foodP
            if self.foodmane != foodmane:
                self.foodmane = foodmane
                fx,fy = foodPm
                t = (fx-self.spriteRect.center[0])/self.velocitX
                Ydirect = fy+t*velocity
                self.trajectory = (fx,Ydirect)
                Newtrajectory = True
        elif self.trajectory == self.position:
            self.trajectory = (random.uniform(80, (screen.get_size())[0] - 80),random.uniform(100, floorrect.top - 80))
            Newtrajectory = True
        if Newtrajectory ==True:
            self.dt = dt
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
        x = self.directionX*self.velocitX*ndt
        if (x>=self.Dx and self.directionX>0)or(x<=self.Dx and self.directionX<0):
            x = 0
            self.position = (self.trajectory[0],self.position[1])
        y = self.directionY*self.velocitY*ndt
        if (y>=self.Dy and self.directionY>0)or(y<=self.Dy and self.directionY<0):
            y = 0
            self.position = (self.position[0],self.trajectory[1])
        self.spriteRect.center = (self.position[0]+x,self.position[1]+y)
        if self.spriteRect.midbottom[1] > floorrect.top:
            self.spriteRect.midbottom = (self.spriteRect.midbottom[0],floorrect.top)
        W, H = self.Scale
        CCt = dt - self.Ct
        # Food collision detection
        for i in range(0,len(foods)):
            if self.spriteRect.colliderect(foods[i].SpriteR):
                del foods[i]
                self.htu = dt
                self.spriteM = pygame.Surface((W,H))
                self.spriteM.fill((0,0,255))
                self.spriteM.set_colorkey((0,0,255))
                self.spriteM.blit(self.sprite,(0,0))
                if self.directionX !=-1:
                    self.spriteM = pygame.transform.flip(self.spriteM,1,0)
                break
        # hunger detection
        hdt = dt - self.htu
        if self.beforeHunger <= hdt:
            self.spriteM = pygame.Surface((W,H))
            self.spriteM.fill((0,0,255))
            self.spriteM.set_colorkey((0,0,255))
            self.spriteM.blit(self.sprite,(-W,0))
            if self.directionX !=-1:
                self.spriteM = pygame.transform.flip(self.spriteM,1,0)
        # coin production
        if  self.maxHunger <= hdt:
            self.FNP = True
        if self.Mmax <= CCt:
            self.Ct = dt
            Coin = Coinclass(self.spriteRect.center,10,10*screen.get_height()/600,(50*screen.get_width()/800,50*screen.get_height()/600),'money.png',dt)
            coins.append(Coin)

        # For testing positions
        print(self.directionX,self.directionY)
        print(self.spriteRect.center)
        print(self.trajectory)

    def draw(self,screen):
        screen.blit(self.spriteM,self.spriteRect)
# coin_timer           // Time elapsed since last coin
# coin_interval        // Random interval required to spawn a new coin


# Class requirements:
# 1. fish moving horizontally and bouncing off the tank walls
# 2. Vertical sinusoidal bobbing motion
# 3. Hunger management
# 4. If hungry and food exists then move towards closest Food
# 5. If hungry, coins are created slower

class Food:
    def __init__(self, x, y, v ,dt,Sprite,SW,SH):
        self.position = (x, y)
        self.velocity = v
        self.dt = dt
        self.Sprite = pygame.image.load(Sprite)
        self.Sprite = pygame.transform.scale(self.Sprite,(SW,SH))
        self.SpriteR = self.Sprite.get_rect(center = self.position)
    def update(self,dt,floorrect):
        dt -= self.dt
        self.SpriteR.center = (self.position[0],self.position[1]+self.velocity*dt)
        if self.SpriteR.midbottom[1] > floorrect.top:
            self.SpriteR.midbottom = (self.SpriteR.midbottom[0],floorrect.top)

    def draw(self,screen):
        screen.blit(self.Sprite,self.SpriteR)

# Class functions:
# init(self, x, y) - initializes the food
# update(self, dt) - updates the food
# draw(self, surface) - draws the food on the surface


class Coin:
    def __init__(self,p,value,velocity,Size,Sprite,dt):
        self.Position = p
        self.value = value
        self.velocity = velocity
        self.Size = Size
        self.Sprite = pygame.image.load(Sprite)
        self.Sprite = pygame.transform.scale(self.Sprite,Size)
        self.Spriter = self.Sprite.get_rect(center=self.Position)
        self.dt = dt
    def update(self, dt, floorrect):
        y = self.velocity * (dt-self.dt)
        self.Position[1]
        self.Spriter.center = (self.Position[0],self.Position[1]+y)
        if self.Spriter.midbottom[1] > floorrect.top:
            self.Spriter.midbottom = (self.Spriter.midbottom[0],floorrect.top)
    def draw(self, surface):
        surface.blit(self.Sprite, self.Spriter)

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
                        ff = Food(x, y,50*HEIGHT/600,dt,'ff.png',54*WIDTH/800,54*HEIGHT/600)
                        foods.append(ff)
                        money -= FOOD_COST
                elif event.button == 3:  # right click: collect coins
                    for coin in coins:
                        click = pygame.Rect(x, y,1,1)
                        if coin.Spriter.colliderect(click):
                            money += coin.value
                            coins.remove(coin)
                            break
            
            elif event.type == pygame.KEYDOWN:
                # Press F to buy a new fish
                if event.key == pygame.K_f and money >= FISH_COST:
                    basicfish = Fish('fish/basicfish.png',(292*WIDTH/800,128*HEIGHT/600),150*WIDTH/800,150*HEIGHT/600,60,90,15,2,dt)
                    basicfish.position = (
                            random.uniform(80, WIDTH - 80),
                            random.uniform(100, TANK_FLOOR_Y - 80)
                    )
                    basicfish.trajectory = basicfish.position
                    fishes.append(basicfish)
                    money -= FISH_COST
        # update game state
        for food in foods:
            food.update(dt,floorrect)
        for coin in coins:
            coin.update(dt,floorrect)
        for fish in fishes:
            fish.update(dt, foods, coins, screen,floorrect,Coin)
            if fish.FNP:
                fishes.remove(fish)
        # drawing tank
        screen.blit(background1,background1reck)
        
        # tank floor
        pygame.draw.rect(screen, (0, 0, 0), floorrect)
        
        #draw enties
        for food in foods:
            food.draw(screen)
            
        for fish in fishes:
            fish.draw(screen)
        
        for coin in coins:
            coin.draw(screen)
        # draw UI
        ui_text = f"Money: ${money} | Left-click: drop food (${FOOD_COST}) | Right-click: collect coins | F: buy fish (${FISH_COST})"
        text_surface = font.render(ui_text, True, (255, 155, 0))
        screen.blit(text_surface, (10, 10))
        
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()
    
if __name__ == "__main__":
    main()
