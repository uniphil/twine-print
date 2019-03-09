pritner kit h:

5-pin connector with red wire end goes into printer
(end with 3 wires is for arduino)

3-wire end:
- black wire to gnd
- yellow wire to arduino digital pin 9

buttons:
- button 0: arduino digital pin 4
- button 1: arduino digital pin 5

(other wire from buttons goes to arduino gnd)


running twine things
====================


## python

1. open terminal and `cd` to the python code
2. run `ls /dev/tty.*` and find the one that says 'usbserial' or 'usbmodem' and sounds like an arduino
3. run: `./serve.py /dev/tty-usbserial-something` (with the 'usbserial' from last time)

## twine

- make sure the story format is sugarcube 2x
- copy `twine.js` into the story javascript
- play the story (after starting python)

for now, you might need to restart python and the story each time it comes to the end.



----

not helpful probably:

nix-shell -p python36Packages.pyserial python36Packages.websockets
