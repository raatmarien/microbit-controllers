from microbit import *
import radio

# Hardcode this ID differently for each controller right now, a more
# sophisticated approach might be letting the controllers choose a
# random number, or even negotiate one with the server, but this seems
# over complicated for now.
ID_CONSTANT = -1
CSV_SEPERATOR = ','

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

def checksum(st):
    x = 0
    for i in map(ord, st):
        x += i
    x = str(x)
    if len(x) == 1:
        return '0'+x
    return x

def seriestransmit(sendme, sendme2):
    message=('%s*%s*%s*%s*%s*%s*%s*%s*%s*%s*%s*%s' %
            (sendme.controller_id, sendme.accelero.x,
            sendme.accelero.y, sendme.accelero.z,
            int(sendme.button_a_pressed), int(sendme.button_b_pressed),
            sendme2.controller_id, sendme2.accelero.x,
            sendme2.accelero.y, sendme2.accelero.z,
            int(sendme2.button_a_pressed), int(sendme2.button_b_pressed)
            ))
    message = '&@'+str(len(message))+'!'+message+'!'+checksum(message)+'>?'
    uart.write(message)

uart.init(baudrate=115200)

state1 = SenseState()
state2 = SenseState()
radio.on()
radio.config(channel = 1, address=0x00000001, group=1)
display.show(Image.HAPPY)


while True:
    try:
        data1 = radio.receive()
    
        if data1 is not None and data1.split(CSV_SEPERATOR)[0] == '1':
            state1.update_from_csv(data1)
        elif data1 is not None and data1.split(CSV_SEPERATOR)[0] == '2':
            state2.update_from_csv(data1)

        seriestransmit(state1, state2)
        sleep(15)
        display.show(Image.DIAMOND)
    except Exception as e:
        display.show(Image.SAD)
        uart.write(str(e))
