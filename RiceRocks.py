
# program template for Spaceship
try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
ANGLE_VEL = 0.07

# damping constant
DAMPING = 0.02
# acceleration constant
ACC = 0.25
# bullet's velocity constant
B = 8
# missile lifespan constatn
LIFESPAN = 40
# postive and negative
directions = [1, -1]
# time 
time = 0

# score_board
score = 0
lives = 3


class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, LIFESPAN)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# alternative upbeat soundtrack by composer and former IIPP student Emiel Stopler
# please do not redistribute without permission from Emiel at http://www.filmcomposer.nl
#soundtrack = simplegui.load_sound("https://storage.googleapis.com/codeskulptor-assets/ricerocks_theme.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

# return distance between p and q
def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

# return position after move
def pos_after_move(pos, vel):
    return [(pos[0] + vel[0]) % WIDTH, (pos[1] + vel[1]) % HEIGHT]

def new_rock():
    return Sprite([random.randrange(0, WIDTH), random.randrange(0, HEIGHT)], [random.random() * random.choice(directions), random.random() * random.choice(directions)], 
                        random.random() * random.choice(directions), (random.random() / 25) * random.choice(directions), asteroid_image, asteroid_info)

def new_missile():
    global game
    bullet_vel = [game.ship.vel[0] + game.ship.forward[0] * B, game.ship.vel[1] + game.ship.forward[1] * B]
    bullet_pos = [game.ship.pos[0] + game.ship.forward[0] * 40, game.ship.pos[1] + game.ship.forward[1] * 40]        
    return	Sprite(bullet_pos, bullet_vel, 0, 0, missile_image, missile_info, missile_sound)

def new_explosion(pos):    
    return Sprite(pos, [0, 0], 0, 0, explosion_image, explosion_info, explosion_sound)

# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
        # acceleration of ship
        self.acc = 0
        # forward vetor
        self.forward = angle_to_vector(self.angle)
        
    def draw(self,canvas):        
        # draw image of spaceship
        if self.thrust == False:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
            
        else:
            
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0], self.image_center[1]],
                                           self.image_size, self.pos, self.image_size, self.angle)
            
    def update(self):
        
        # if thrust is on
        if self.thrust == True:
            # update acceleration of ship
            self.acc = ACC
            
            # play thrust sound
            ship_thrust_sound.play()
        else:
            # update acceleration of ship
            self.acc = 0
            
            # pause thrust sound
            ship_thrust_sound.pause()
        
        # forward vector
        self.forward = angle_to_vector(self.angle)
        
        # update velocity
        self.vel[0] = (1 - DAMPING) * self.vel[0] + self.acc * self.forward[0]
        self.vel[1] = (1 - DAMPING) * self.vel[1] + self.acc * self.forward[1]
        
        # update position
        self.pos = pos_after_move(self.pos, self.vel)
   
        # update angle
        self.angle += self.angle_vel  
        
    def shoot(self):
        game.missile_set.add(new_missile())
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()		
        
    def draw(self, canvas):
        # draw image of Sprite
        if self.animated == True:
            canvas.draw_image(self.image, [self.image_center[0] + self.age * self.image_size[0], self.image_center[1]],
                              self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

    def update(self):
        # update Sprite's position 
        self.pos = pos_after_move(self.pos, self.vel)
        # update Sprite's angle
        self.angle += self.angle_vel
        # update the age
        self.age += 1        
           
def draw(canvas):
    global time, score, lives
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    
    canvas.draw_text(str(score), [WIDTH * 7 / 8, HEIGHT / 8], 20, "White")
    canvas.draw_text("score", [WIDTH * 7 / 8 - 15, HEIGHT / 8 - 30], 20, "White")
    canvas.draw_text(str(lives), [WIDTH / 8, HEIGHT / 8], 20, "White")
    canvas.draw_text("lives", [WIDTH / 8 - 15, HEIGHT / 8 - 30], 20, "White")

    # draw ship and sprites
    game.ship.draw(canvas)
    
    # update ship and sprites
    game.ship.update()
    
    # draw and update rocks_set
    draw_update_group(game.rocks_set, canvas)
    
    # draw and update missile_set
    draw_update_group(game.missile_set, canvas)
            
    # draw and update explosion_set
    draw_update_group(game.explosion_set, canvas)
    
    # collision of ship and rock
    if group_collision(game.rocks_set, game.ship):
        lives -= 1
        
    # collision of rocks and missiles
    score += group_group_collision(game.missile_set, game.rocks_set)
    
    if not game.begin:
        canvas.draw_image(splash_image, splash_info.get_center(), splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], splash_info.get_size())
    
    if lives == 0:
        game.begin = False
        game.timer.stop()
        game.rocks_set = set([])

def draw_update_group(obj_set, canvas):
    remove_set = set([])
    for obj in list(obj_set):
        obj.draw(canvas)
        obj.update()
        if obj.lifespan == obj.age:
            remove_set.add(obj)
    obj_set.difference_update(remove_set)
    
def group_collision(group, target):
    global game
    remove_set = set([])
    is_collision = False    
    for element in list(group):
        if dist(element.pos, target.pos) <= element.radius + target.radius:
            game.explosion_set.add(new_explosion(target.pos))
            is_collision = True
            remove_set.add(element)
    group.difference_update(remove_set)
    return is_collision
    
def group_group_collision(group, target_group):
    global game
    
    remove_set = set([])
    collision_count = 0
    for target in list(target_group):
        if group_collision(group, target):
            collision_count +=1
            remove_set.add(target)
    target_group.difference_update(remove_set)
    return collision_count    
    
# timer handler that spawns a rock
def rock_spawner():
    global game
    
    # maximun number of rock is 7
    if(len(game.rocks_set) < 12):
        # add rock to rocks_set
        game.rocks_set.add(new_rock())
        
        
# the class of game
class Game():
    def __init__(self):
        # create frame
        self.frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)
        # create ship
        self.ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
        # create timer
        self.timer = simplegui.create_timer(1000.0, rock_spawner)
        # register keyboard handlers
        self.frame.set_keydown_handler(self.key_down)
        self.frame.set_keyup_handler(self.key_up)
        # register mouse handler
        self.frame.set_mouseclick_handler(self.mouse_handler)
        # register drawe handler
        self.frame.set_draw_handler(draw)
        # keyboard_down_count
        self.key_down_count = 0        
        # create missiles set
        self.missile_set = set([])
        # create rocks set
        self.rocks_set = set([])
        # create explosion set
        self.explosion_set = set([])
        # game controller
        self.begin = False
        
    # draw handler
    def draw(self):
        
        pass
    
    # key_up handler
    def key_up(self, key):
        # release 'up', thrust is off
        if key == simplegui.KEY_MAP['up']:
            self.ship.thrust = False
        # release 'down' 
        elif key == simplegui.KEY_MAP['space']:
            pass
        else:
            self.key_down_count -= 1
            if self.key_down_count == 0:
                if key == simplegui.KEY_MAP['left']:          
                    self.ship.angle_vel = 0          
                if key == simplegui.KEY_MAP['right']:
                    self.ship.angle_vel = 0
       
        
    # key_down handler
    def key_down(self, key):
        # press 'up', thrust is on 
        if key == simplegui.KEY_MAP['up']:
            self.ship.thrust = True
        elif key == simplegui.KEY_MAP['space']:
            self.ship.shoot()
        else:
            self.key_down_count += 1

            # press 'left', spin clockwisely
            if key == simplegui.KEY_MAP['left']:
                self.ship.angle_vel = -ANGLE_VEL    
            
            #press 'right', spin counter-clockwisely
            if key == simplegui.KEY_MAP['right']:
                self.ship.angle_vel = ANGLE_VEL
        
    def mouse_handler(self, pos):
        global lives, score
        lives = 3
        score = 0
        self.begin = True        
        self.timer.start()
        
    # start handler
    def start(self):
         self.frame.start()
    
game = Game()
game.start()
    

