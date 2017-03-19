import pygame
import pygame.locals
import sys
import random
import serial
import time
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
    buf = ser.read(80)
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


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500

PADLE_WIDTH = 20
PADLE_HEIGHT = 100
PADLE_MOVE = 10
PADLE_CURVE = 0.25

BALL_SPEED = 9
BALL_SIZE = 20
BALL_Y_HOLD = 0.35

BARS = 8
BAR_WIDTH = 5

def collides(rect1, rect2):
    r1 = pygame.Rect(rect1[0], rect1[1], rect1[2], rect1[3])
    r2 = pygame.Rect(rect2[0], rect2[1], rect2[2], rect2[3])
    return r1.colliderect(r2)

class Padle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speedx = 0
        self.speedy = 0

    def update(self):
        self.x += self.speedx
        self.y += self.speedy

        if self.y < PADLE_HEIGHT / 2:
            self.y = PADLE_HEIGHT / 2
        if self.y > SCREEN_HEIGHT - PADLE_HEIGHT / 2:
            self.y = SCREEN_HEIGHT - PADLE_HEIGHT / 2

    def get_rect(self):
        return (self.x, self.y - (PADLE_HEIGHT / 2),
                PADLE_WIDTH, PADLE_HEIGHT)


    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.get_rect())


class Ball:
    def __init__(self, x, y, speedx, speedy):
        self.x = x
        self.y = y
        self.speedx = speedx
        self.speedy = speedy

    # Returns who scores a point or None
    def update(self, left, right):
        self.x += self.speedx
        self.y += self.speedy

        if self.y < BALL_SIZE / 2:
            if self.speedy < 0:
                self.speedy *= -1
            self.y = BALL_SIZE / 2 + self.speedy

        if self.y > SCREEN_HEIGHT - BALL_SIZE / 2:
            if self.speedy > 0:
                self.speedy *= -1
            self.y = SCREEN_HEIGHT - BALL_SIZE / 2 + self.speedy

        if collides(self.get_rect(), left.get_rect()):
            self.x = left.x + PADLE_WIDTH + BALL_SIZE / 2
            if self.speedx < 0:
                self.speedx *= -1
            self.speedy *= BALL_Y_HOLD
            self.speedy = (PADLE_CURVE * (self.y - left.y)) * (1 - BALL_Y_HOLD)
        elif self.x < BALL_SIZE / 2 + PADLE_WIDTH:
            return right

        if collides(self.get_rect(), right.get_rect()):
            self.x = right.x - PADLE_WIDTH + BALL_SIZE / 2
            if self.speedx > 0:
                self.speedx *= -1
            self.speedy *= BALL_Y_HOLD
            self.speedy = (PADLE_CURVE * (self.y - right.y)) * (1 - BALL_Y_HOLD)
        elif self.x > SCREEN_WIDTH - BALL_SIZE / 2 - PADLE_WIDTH:
            return left

        return None


    def get_rect(self):
        return (self.x - BALL_SIZE / 2,
                self.y - BALL_SIZE / 2,
                BALL_SIZE, BALL_SIZE)


    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.get_rect())

def handle_win(left_score, right_score, screen, font):
    if left_score >= 10 or right_score >= 10:
        text = (('Left' if left_score >= 10 else 'Right') +
                ' wins!')
        while True:
            handle_events()
            screen.fill(BLACK)
            size = font.size(text)
            label = font.render(text, 1, WHITE)
            screen.blit(label,
                        ((SCREEN_WIDTH - size[0]) / 2,
                         (SCREEN_HEIGHT - size[1]) / 2))
            pygame.display.update()

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

def handle_keys(left, right):
    try:
        sense_list = receive()
        
        moved_1 = moved_2 = False
        if len(sense_list) != 0:
            if sense_list[0].accelero.x < -20:
                left.speedy = -PADLE_MOVE * (-sense_list[0].accelero.x / 1000)
                moved_1 = True
            if sense_list[0].accelero.x > 20:
                left.speedy = PADLE_MOVE * (sense_list[0].accelero.x / 1000)
                moved_1 = True
            if sense_list[1].accelero.x < -20:
                right.speedy = -PADLE_MOVE * (-sense_list[1].accelero.x / 1000)
                moved_2 = True
            if sense_list[1].accelero.x > 20:
                right.speedy = PADLE_MOVE * (sense_list[1].accelero.x / 1000)
                moved_2 = True
    except Exception as e:
        print(str(e))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        right.speedy = -PADLE_MOVE
    elif keys[pygame.K_DOWN]:
        right.speedy = PADLE_MOVE

    if keys[pygame.K_w]:
        left.speedy = -PADLE_MOVE
    elif keys[pygame.K_s]:
        left.speedy = PADLE_MOVE


def get_start_ball():
    if random.randint(0, 1) == 0:
        xspeed = BALL_SPEED
    else:
        xspeed = -BALL_SPEED

    yspeed = (random.random() * 1.5) * BALL_SPEED
    if random.randint(0, 1) == 0:
        yspeed *= -1

    return Ball(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, xspeed, yspeed)


pygame.init()


if __name__ == '__main__':
    # Initialization code
    font = pygame.font.SysFont("monospace", 50)
    scoreFont = pygame.font.SysFont("monospace", 100)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill(BLACK)

    left = Padle(0, SCREEN_HEIGHT / 2)
    right = Padle(SCREEN_WIDTH - PADLE_WIDTH, SCREEN_HEIGHT / 2)

    left_score = right_score = 0

    ball = get_start_ball()

    while True:
        handle_win(left_score, right_score, screen, scoreFont)
        handle_events()
        handle_keys(left, right)

        left.update()
        right.update()

        who_scores = ball.update(left, right)
        if who_scores is not None:
            if who_scores == left:
                left_score += 1
                text = 'Left scored!'
            elif who_scores == right:
                text = 'Right scored!'
                right_score += 1

            handle_win(left_score, right_score, screen, font)

            left = Padle(0, SCREEN_HEIGHT / 2)
            right = Padle(SCREEN_WIDTH - PADLE_WIDTH, SCREEN_HEIGHT / 2)
            ball = get_start_ball()

            # Show the text who scored
            screen.fill(BLACK)
            label = scoreFont.render(text, 1, WHITE)
            screen.blit(label,
                        ((SCREEN_WIDTH / 2 - scoreFont.size(text)[0] / 2),
                        (SCREEN_HEIGHT / 2 - scoreFont.size(text)[1] / 2)))
            pygame.display.update()

            pygame.time.wait(1000)

            # Show the ball and let the player prepare
            for i in range(0, 50):
                handle_events()
                handle_keys(left, right)
                left.update()
                right.update()

                screen.fill(BLACK)
                left.draw(screen)
                right.draw(screen)
                ball.draw(screen)

                arrow_size = (ball.speedx / BALL_SPEED * 60, ball.speedy / BALL_SPEED * 60)
                startPos = ((SCREEN_WIDTH) / 2,
                            (SCREEN_HEIGHT) / 2)

                # Draw the direction of the ball
                pygame.draw.line(screen, WHITE, startPos,
                                 (startPos[0] + arrow_size[0], startPos[1] + arrow_size[1]),
                                 3)

                time = 1 - (i / 50)
                time_text = str(time)[0:3]
                size = font.size(time_text)
                label = font.render(time_text, 1, WHITE)
                screen.blit(label, ((SCREEN_WIDTH - size[0]) / 2, 20,
                            size[0], size[1]))

                pygame.display.update()

                pygame.time.wait(20)


            continue


        screen.fill(BLACK)

        left.draw(screen)
        right.draw(screen)

        ball.draw(screen)

        for i in range(0, BARS):
            pygame.draw.rect(screen, WHITE,
                             ((SCREEN_WIDTH - BARS) / 2, (i+0.25) * SCREEN_HEIGHT / BARS,
                              BAR_WIDTH, SCREEN_HEIGHT / (BARS * 1.5)))

        score_text = str(left_score) + '   ' + str(right_score)
        score = font.render(score_text, 1, WHITE)
        screen.blit(score,
                    (SCREEN_WIDTH / 2 - font.size(score_text)[0] / 2, 20))

        pygame.display.update()

        pygame.time.wait(15)
