from microbit import *
import radio
# Hardcode this ID differently for each controller right now, a more
# sophisticated approach might be letting the controllers choose a
# random number, or even negotiate one with the server, but this seems
# over complicated for now.
ID_CONSTANT = 1
CSV_SEPERATOR = ','
# initialize these ones for the animation method 
#img = [[0]*5]*5
#imgX = [[0]*5]*5
#imgY = [[0]*5]*5
class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
def list_to_csv(arg_list):
    csv = ''
    for arg in arg_list:
        csv += str(arg) + CSV_SEPERATOR
    return csv[:len(csv)-1]
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
    def to_csv(self):
        return list_to_csv([self.controller_id,
                            self.accelero.x,
                            self.accelero.y,
                            self.accelero.z,
                            self.button_a_pressed,
                            self.button_b_pressed,
                            self.num_button_a_presses,
                            self.num_button_b_presses])
    def update_from_csv(self, csv_string):
        if type(csv_string) is not str:
            return
        try:
            args = csv_string.split(CSV_SEPERATOR)
            self.controller_id = int(args[0])
            self.init = True
            self.accelero.x = int(args[1])
            self.accelero.y = int(args[2])
            self.accelero.z = int(args[3])
            self.button_a_pressed = args[4] == 'True'
            self.button_b_pressed = args[5] == 'True'
            self.num_button_a_presses = int(args[6])
            self.num_button_b_presses = int(args[7])
        except:
            return False
def get_current_sense_state():
    state = SenseState()
    state.accelero = Vector3(accelerometer.get_x(),
                             accelerometer.get_y(),
                             accelerometer.get_z())
    state.init = True
    state.button_a_pressed = button_a.is_pressed()
    state.button_b_pressed = button_b.is_pressed()
    state.num_button_a_presses = button_a.get_presses()
    state.num_button_b_presses = button_b.get_presses()
    return state
 
# this animation method should be included into the 'main'-method 
def animate():
    #retrieve x- and y-accelerometer data
    accelX = accelerometer.get_x()//100
    accelY = accelerometer.get_y()//100
    
    #update x-image
    if accelX > 0:
        for x in range(5):
            for y in range(5):
                term = accelX + x - 5
                if term >= 0 and term <=9:
                    imgX[x][y]= term
                elif (term < 0):
                    imgY[x][y]=0
                elif (term > 0):
                    imgY[x][y]=9
                
    elif accelX < 0:
        for x in range(5):
            for y in range(5):
                term = (-accelX -1 - x)
                if term >= 0 and term <= 9:
                    imgX[x][y]= term
                elif (term < 0):
                    imgX[x][y]=0
                elif (term > 0):
                    imgX[x][y]=9
                
    elif accelX == 0:
        for x in range(5):
            for y in range(5):
                imgX[x][y] = 0
     # update the y-image
    if accelY > 0:
       for x in range(5):
           for y in range(5):
               term = accelY + y - 5
               if term >= 0 and term <=9:
                   imgY[x][y]= term           
               elif (term < 0):
                   imgY[x][y]=0
               elif (term > 0):
                    imgY[x][y]=9
     
    elif accelY < 0:
        for x in range(5):
            for y in range(5):
                term = (-accelY -1 - y)
                if term >= 0 and term <= 9:
                    imgY[x][y]= term
                elif (term < 0):
                    imgY[x][y]=0
                elif (term > 0):
                    imgY[x][y]=9
     
    elif accelY == 0:
       for x in range(5):
           for y in range(5):
               imgX[x][y] = 0
                
    # combine the two images
    for x in range(5):
        for y in range(5):
            img[x][y] = (imgX[x][y] + imgY[x][y]) //2
            display.set_pixel(x,y,img[x][y])
uart.init(baudrate=115200)
radio.on()
radio.config(channel = 1, address=0x00000001, group=1)
display.show(Image.HAPPY)
while True:
    #animate() # updates the controller's animation
    contr1 = get_current_sense_state()
    radio.send(contr1.to_csv())
    sleep(52)
