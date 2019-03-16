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

press the `reset` button on the arduino to reset the story, or if things stop responding.


## including images

1. copy the image inside the `images/` folder from the github stuff
2. include it in a passage using this syntax: `{{filename.jpg}}`.

eg., if your image is at `images/hello.png`, do `{{hello.png}}` in the passage text where you want it.

- large images will automatically be scaled down to 384 px wide. to print smaller, resize them in a graphics program.
- boring-but-pretty-good dithering is applied for half-toning. I'd like to make that configurable -- if you really want noise dither or regular thresholding lmk.


----

not helpful probably just for phil:

nix-shell -p python36Packages.pyserial python36Packages.websockets python36Packages.pillow
