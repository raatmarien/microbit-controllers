import pygame
import time
import sys

#Code for receiving the serial
import serial

ID_CONSTANT = -1
def checksum(st):
    x = 0
    for i in map(ord, st):
        x += i
    x = str(x)
    if len(x) == 1:
        return '0'+x
    return x

class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class SenseState:
    # The constructor sets the defaults
    def __init__(self):
        self.controller_id = ID_CONSTANT
        self.message = ''
        self.accelero = Vector3(0, 0, 0)
        self.init = False
        self.button_a_pressed = False
        self.button_b_pressed = False
        self.num_button_a_presses = 0
        self.num_button_b_presses = 0

    def to_string(self):
        return (
            ('id: %s, msg: %s, (a: %s, %s, %s)' %
             (self.controller_id, self.message, self.accelero.x,
              self.accelero.y, self.accelero.z)) +
            (', init: %s, ap: %s, bp: %s, an: %s, bn: %s' %
             (self.init, self.button_a_pressed, self.button_b_pressed,
              self.num_button_a_presses, self.num_button_b_presses)))

ser = serial.Serial(port='/dev/ttyACM0',timeout=0.002, baudrate=115200)
print('Reading from',ser.name)

def parsecheck(msg):
    #print(msg)
    try:
        if msg[:2] != '&@' or msg[-2:] != '>?':
            print('rejected  no good start and end')
            return -1
        msg=msg[2:-2]
        parts = msg.split('!')
        if len(parts) != 3:
            print('rejected no three data elems')
            return -1
        if len(parts[1]) != int(parts[0]):
            print('rejected incorrect data length')
            return -1
        if checksum(parts[1]) != parts[2]:
            print('rejected failed checksum')
            return -1
        parts = parts[1].split('*')
        if len(parts)==12:
            return parts
    except:
        print('-1 because of excep')
        return -1
    print('program ran out')
    return -1

def receive():
    buf = ser.read(100)
    ser.reset_input_buffer()
    #print(buf)
    buf = buf.decode('utf-8').rsplit('>?',1)[0]+'>?'
    if buf[-2:]=='>?':
        a = buf.rfind('&@')
        #print(888)
        if a==-1:
            return []
        msg = buf[a:]
        msg = parsecheck(msg) # check that msg has integrity and is in order
        #print(999)
        if msg==-1:
            return []
        #print(777)
        s = SenseState()
        p = SenseState()
        s.controller_id = msg[0]
        s.accelero.x = int(msg[1])
        s.accelero.y = int(msg[2])
        s.accelero.z = int(msg[3])
        s.button_a_pressed = bool(int(msg[4]))
        s.button_b_pressed = bool(int(msg[5]))
        
        p.controller_id = msg[6]
        p.accelero.x = int(msg[7])
        p.accelero.y = int(msg[8])
        p.accelero.z = int(msg[9])
        p.button_a_pressed = bool(int(msg[10]))
        p.button_b_pressed = bool(int(msg[11]))
        
        return [s,p]
    else:
        return []

# end


#set screen height and screen width
screenWidth = 800
screenHeight = 500
# initialising stuff 
pygame.init()
pygame.font.init()
myfont = pygame.font.SysFont('Calibri', 50)
screen = pygame.display.set_mode((screenWidth, screenHeight))
done = False
clock = pygame.time.Clock()
# set the colors of the two rectangles as variables
blue = (0, 128,255)
orange = (255, 100,0)
class rect():
    rId = 0 # id to distinguish between different rectangles
    curDir = 0 # current direction in which the rectangle points (0=up, 1=right, 2=down, 3=left)
    curX = 0 # current x-position
    curY = 0 # current y-position
    sideLen = 10; # side length of the rectangle
    color = (0,0,0)
    counter = 0
    def __init__(self, newId, startX, startY, sideLen, color, startDir):
        self.rect = pygame.Rect(startX, startY, sideLen, sideLen)
        self.rId = newId
        self.curX = startX
        self.curY = startY
        self.sideLen = sideLen
        self.color = color
        self.curDir = startDir
    def getColor(self):
        return self.color
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
    def crash(self, color):
        crashed = False
        if (self.curDir == 0):
            if self.curY > 0 and screen.get_at((self.curX, self.curY - 1)) == color:
                crashed = True
            elif self.curY <=0:
                crashed = True
                
        elif (self.curDir == 1):
            if self.curX < (screenWidth -1 - self.sideLen) and screen.get_at((self.curX +1 + self.sideLen , self.curY)) == color:
                crashed = True
            elif self.curX >= (screenWidth -1 - self.sideLen):
                crashed = True
                
        elif (self.curDir == 2):
            if self.curY < (screenHeight -1 - self.sideLen) and screen.get_at((self.curX, self.curY +1 + self.sideLen)) == color:
                crashed = True
            elif self.curY >= (screenHeight -1 - self.sideLen):
                crashed = True
                
        elif (self.curDir == 3):
            if self.curX > 0 and screen.get_at((self.curX -1, self.curY)) == color:
                crashed = True
            elif self.curX <= 0:
                crashed = True 
                
        if crashed:
            return True
        else:
            return False
            
        
    def move(self):
        self.counter += 1
        if (self.counter > 15):
            try:
                sense_list = receive()

                if len(sense_list) != 0:
                    sense = sense_list[1]
                    if self.rId == 1:
                        sense = sense_list[0]
                        if sense.button_a_pressed:
                            print(sense.button_a_pressed)

                    if sense.button_a_pressed:
                        print('A pressed')
                        self.curDir = (self.curDir-1)%4
                        self.counter = 0
                    elif sense.button_b_pressed:
                        print('B pressed')
                        self.curDir = (self.curDir+1)%4
                        self.counter = 0
            except:
                pass
                    
                    
        # movement according to the current direction
        if self.curDir == 3 and self.curX > 0:
            self.rect.move_ip(-1, 0)
            self.curX-= 1
        elif self.curDir == 1 and self.curX < screenWidth - 1 - self.sideLen: # since the rectangle is located by it's upper left corner
            self.rect.move_ip(1, 0)
            self.curX += 1
        elif self.curDir == 0 and self.curY > 0:
            self.rect.move_ip(0, -1)
            self.curY -= 1
        elif self.curDir == 2 and self.curY < screenHeight - 1 - self.sideLen: # since the rectangle is located by it's upper left corner
            self.rect.move_ip(0, 1)
            self.curY += 1

# create the two rectangles
rect1 = rect(1, (screenWidth//2)-10, (screenHeight//2),10, blue, 0)
rect2 = rect(2, (screenWidth//2)+10, (screenHeight//2) , 10, orange, 0)
# display the two rectangles
rect1.draw(screen)
rect2.draw(screen)
pygame.display.update()
while not done:
        # check if the game was closed
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True
        # moving the rectangles
        if (rect1.crash(rect1.getColor()) or rect1.crash(rect2.getColor())) and (rect2.crash(rect1.getColor()) or rect2.crash(rect2.getColor())):
            textSurface = myfont.render('Draw!', False, (255, 255, 255))
            screen.blit(textSurface,(200,200))
            done = True
        elif rect1.crash(rect1.getColor()) or rect1.crash(rect2.getColor()):
            textSurface = myfont.render('Orange Wins!', False, (255, 255, 255))
            screen.blit(textSurface,(200,200))
            done = True 
        else:
            rect1.move()
            if rect2.crash(rect1.getColor()) or rect2.crash(rect2.getColor()):
                textSurface = myfont.render('Blue Wins!', False, (255, 255, 255))
                screen.blit(textSurface,((screenWidth//2)-50, (screenHeight//2)-50))
                done = True 
            else:
                rect2.move()
        # refresh the screen
        rect1.draw(screen)
        rect2.draw(screen)  
        pygame.display.update()
        clock.tick(100)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
