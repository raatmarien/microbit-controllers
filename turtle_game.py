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

import turtle
sc = turtle.Screen()
sc.delay(1)
marien = turtle.Turtle()
ethan = turtle.Turtle()
print(type(sc))
while True:
    time.sleep(0.04)# sleep for setup time
    #print("Reading:")
    f = receive()
    #print(f)
    
    if(not len(f)==0):
        # print('Success')
        # print('S: ', f[0].controller_id, f[0].accelero.x, f[0].accelero.y,
        #       f[0].accelero.z, f[0].button_a_pressed)
        # print('P: ', f[1].controller_id, f[1].accelero.x, f[1].accelero.y,
        #       f[1].accelero.z, f[1].button_a_pressed)
        if f[0].button_a_pressed:
            marien.color('green','red')
        else:
            marien.color('red', 'red')
        if f[1].button_a_pressed:
            ethan.color('yellow','black')
        else:
            ethan.color('black', 'black')
            

        marien.left(f[0].accelero.x/35)
        marien.forward(-f[0].accelero.y/20)
        ethan.left(f[1].accelero.x/35)
        ethan.forward(-f[1].accelero.y/20)
    else:
        print('f was None')
