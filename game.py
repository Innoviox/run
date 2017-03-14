import pygame, sys, random

global unlocked, entities
entities = pygame.sprite.Group()
unlocked = []

WIN_WIDTH = 800
WIN_HEIGHT = 640
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

load = lambda image: pygame.image.load('resources/'+image) #quicker

solidTiles = {'P':True, ' ':False}
images = {
          'T': load('top.bmp'),
          'B': load('bottom.bmp'),
          'E': load('door-top.bmp'), 
          'F': load('door-bottom.bmp'), 
          'L': load('lock-red.bmp'), 
          'K': load('key-red.bmp'),
          'A': load('lava.bmp'),
          'S': load('spikes.bmp'),
         }

empty = [' ', '@']
deadly = ['A', 'S']
winners = ['E', 'F']
keys = {'K': 'L'}

screen = pygame.display.set_mode((800, 640), 0, 32)

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class Platform(Entity):
    def __init__(self, x, y, imag):
        Entity.__init__(self)
        self.image = imag
        self.rect = pygame.Rect(x, y, 32, 32)
        self.type = {v: k for k,v in images.items()}[imag]
        self.show = True
        
class Player(Entity):
    def __init__(self, x, y, level, speed):
        Entity.__init__(self)
        self.x = self.origX = x
        self.y = self.origY = y
        
        self.level = level

        self.max_speed = speed
        self.sx = 0
        self.sy = 0
        
        self.onGround = False
        
        self.rect = pygame.Rect(x, y, 32, 32)

        self.image = pygame.Surface((32, 32))
        self.image.convert()
        self.image.fill(pygame.Color("#AA00D0"))

        self.won = False
        self.type = "Player"
        self.show = True
    def run(self, up, left, right):
        #movement
        if up and self.onGround:
            self.sy = -11
        if left:
            self.sx = -8
        elif right:
            self.sx = 8
        else:
            self.sx = 0
        #gravity
        if not self.onGround:
            self.sy += 0.3

        self.rect.left += self.sx
        self.collide(self.sx, 0, self.level.platforms)

        self.rect.top += self.sy
        self.onGround = False
        self.collide(0, self.sy, self.level.platforms)

        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.left < 0:
            self.rect.left = 0
    def collide(self, sx, sy, platforms):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if p.type in deadly:
                    self.die()
                    
                elif p.type in winners:
                    self.won = True
                    
                elif p.type in keys:
                    unlock(keys[p.type])
                    unlock(p.type)
                    
                else:
                    if sx > 0:
                        self.rect.right = p.rect.left
                        
                    elif sx < 0:
                        self.rect.left = p.rect.right
                        
                    if sy > 0:
                        self.rect.bottom = p.rect.top
                        self.onGround = True
                        self.sy = 0
                        
                    elif sy < 0:
                        self.rect.top = p.rect.bottom
    def die(self):
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.sx = self.sy = 0
        
class Level():
    def __init__(self, tile_width, tile_height, level):
        self.height = len(level)
        self.width = len(level[0])
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.level = level
        
    def start(self):
        self.platforms = []
        for ri, row in enumerate(self.level):
            for ci, col in enumerate(row):
                if col not in empty:
                    self.platforms.append(Platform(ci*self.tile_height, ri*self.tile_width, images[col]))

    def find(self, square):
        for ri, row in enumerate(self.level):
            for ci, col in enumerate(row):
                if col == square:
                    yield ri, ci
        
class Camera():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.state = pygame.Rect(0, 0, width, height)
        
    def camera(self, target_rect):
        l, t, _, _ = target_rect
        _, _, w, h = self.state
        l, t, _, _ = -l+HALF_WIDTH, -t+HALF_HEIGHT, w, h

        l = min(0, l)                           # stop scrolling at the left edge
        l = max(-(self.state.width-WIN_WIDTH), l)   # stop scrolling at the right edge
        t = max(-(self.state.height-WIN_HEIGHT), t) # stop scrolling at the bottom
        t = min(0, t)                           # stop scrolling at the top
        return pygame.Rect(l, t, w, h)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera(target.rect)

def destroy(e):
    e.show = False
    e.rect.width=0
    e.rect.height=0
    
def unlock(_type, platforms=entities, rep=' '):
    for i in platforms:
        if i.type == _type:
            destroy(i)
def run(l):
    level = Level(32, 32, l)
    level.start()
    
    p1 = next(level.find('@'))

    player1 = Player(p1[0]*32, p1[1]*32, level, 5)
    
    bg = pygame.Surface((32,32))
    bg.convert()
    bg.fill(pygame.Color("#000000"))
    
    clock = pygame.time.Clock()
    
    global entities
    for p in level.platforms:
        entities.add(p)
    entities.add(player1)
        
    total_level_width  = len(level.level[0])*32
    total_level_height = len(level.level)*32
    camera = Camera(total_level_width, total_level_height)

    up = left = right = False
    while not player1.won:
        clock.tick(60)
        screen.fill((255, 255, 255))
        
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                   up = True
                if e.key == pygame.K_LEFT:
                    left = True
                if e.key == pygame.K_RIGHT:
                    right = True

            if e.type == pygame.KEYUP:
                if e.key == pygame.K_UP:
                    up = False
                if e.key == pygame.K_RIGHT:
                    right = False
                if e.key == pygame.K_LEFT:
                    left = False
                    
        # draw background
        for y in range(32):
            for x in range(32):
                screen.blit(bg, (x * 32, y * 32))
                
        player1.run(up, left, right)
        camera.update(player1)
        
        for e in entities:
            if e.show:
                screen.blit(e.image, camera.apply(e))
            
        pygame.display.update()
        
def main():
    pygame.init()
    l = [
       '@                            LLL           T',
       'T                            LEL           B',
       'B                       S    LFL           B',
       'B                    TTTTTTTTTTT           B',
       'B                                          B',
       'B                                          B',
       'B                                          B',
       'B    TTTTTTTT                              B',
       'B                                          B',
       'B                          TTTTTTT         B',
       'B                 TTTTTT                   B',
       'B                                          B',
       'B         TTTTTTT                          B',
       'B                                          B',
       'B                     TTTTTT               B',
       'B                                          B',
       'B   TTTTTTTTTTT                            B',
       'B                                          B',
       'B                 TTTTTTTTTTT              B',
       'B                                          B',
       'B                                          B',
       'B                                          B',
       'B                                       K  B',
       'BTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTAAATTTTB'
       ]
    run(l)
    print('You win!')
    raise SystemExit
main()
