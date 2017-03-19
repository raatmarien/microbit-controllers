# Wireless microbit controllers

This allows you to use BBC Microbits as wireless controllers. It
includes two classic multiplayer games: Pong and Tron.

# How it works

One Microbit works as a server. It is connected with a PC through USB
and facilitates the communication between the controllers and the
game. The other Microbits act like a wireless controller. They send
their state to the server over radio. The server then receives their
states and communicates it to the PC (and the game that is playing on
the PC) through serial with UART.

All the Microbits controllers are thin clients, they don't store any
state. This makes them rubost and fast, moving all the complexity to
the PC, which is several orders of magnitude faster.

# Building it

### Physical requirements

* Two BBC Microbits (three if you want two controllers, four if you
want three controllers, etcetera)
* Batteries for the Microbits that you want to use as controllers
* A PC or laptop to run the games on and to flash the microbits

### Software requirements

* python3
* python3-serial
* pygame for python3 (you'll need to compile it yourself,
[see here](http://askubuntu.com/questions/401342/how-to-download-pygame-in-python3-3))

### Flashing the Microbits

You can compile `microbit-server.py` and `microbit-controller.py`
online at
[python.microbit.org](http://python.microbit.org/editor.html#).

1. Compile and download the hex files for `microbit-server.py` and
`microbit-controller.py`
2. Flash the hex from `microbit-server.py` to the Microbit you want to
use at server, by dragging it on the device in a file manager.
3. Flash the hex from `microbit-controller.py` to the Microbits you
want to use at servers, by dragging it on the device in a file
manager.


### Running the games

1. Plug in the Microbit server using USB
2. Run the game you want to play with python3. You may need to change
the device path, which is `/dev/ttyACM0`, to the path of your Microbit
server
3. Enjoy :)
