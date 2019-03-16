#!venv/bin/python
#!/usr/bin/env python

import asyncio
import websockets
from time import sleep
from serial import Serial
from serial.tools import list_ports
from PIL import Image
import json
import re

DOTS = 6
HEAT_TIME = 180
HEAT_INTERVAL = 127
PRINT_DENSITY = 0b001
PRINT_BREAK_TIME = 0b00011

class RequestRestart(Exception):
    pass


def im_row(width):
    """note: width is in bytes (x8 pixels)"""
    if (width <= 0):
        raise ValueError('row must be at least 1 byte wide')
    if (width > 48):
        raise ValueError('width: {} -- can only print rows up to 48 bytes (384px) wide'.format(
            width))
    return bytearray([
        0x12,  # [DC2]
        ord('*'),
        1,  # height
        width
    ])


def printer_config(s):
    s.write(bytearray([
        27,
        55,
        DOTS,
        HEAT_TIME,
        HEAT_INTERVAL,
    ]))
    s.write(bytearray([
        18,
        35,
        (PRINT_DENSITY << 5) | PRINT_BREAK_TIME,
    ]))


def show_im(s, filename):
    im = Image.open('images/{}'.format(filename))
    print('[printing image images/{}]'.format(filename))
    printer_config(s)

    if im.width > 384:
        ratio = im.height / im.width
        im = im.resize((384, round(384 * ratio)), resample=Image.LANCZOS)
    im = im.convert('1')

    x_pad = 8 - (im.width % 8) if im.width % 8 > 0 else 0
    x_bytes = (im.width + x_pad) // 8

    for y in range(im.height):
        out = im_row(x_bytes)
        for xi in range(0, im.width, 8):
            b = 0
            for i in range(8):
                b <<= 1
                px = im.getpixel((xi + i, y)) if xi + i < im.width else 255
                black = px < 128
                b |= black
            out.append(b)
        ser.write(out)
        sleep(0.05)


def get_choice(s, n, w):
    msg = 'available options: {}\n\n\n'\
        .format(', '.join(map(str, range(n))))\
        .encode('ascii')
    while True:
        c = s.read(1)
        try:
            choice = int(c)
        except ValueError:
            if c == b'\xFF':
                raise RequestRestart()
            s.write(msg)
            continue
        if choice < 0 or choice > n -1:
            s.write(msg)
            continue
        return choice


def play(s):

    async def handler(websocket, path):
        print('twine connected.')

        def show(m, inject_images=False):
            if inject_images:
                for i, content in enumerate(re.split(r'\{\{(.*)\}\}', m)):
                    if i % 2 == 0:
                        show(content)
                    else:
                        try:
                            show_im(s, content)
                        except FileNotFoundError:
                            show('{{{{{}|not found}}}}'.format(content))
            else:
                print(m)
                s.write(m.encode('ascii'))
                s.write(b'\n')

        async for message in websocket:
            data = json.loads(message)
            show(data['text'], inject_images=True)
            show('\n')
            for i, o in enumerate(data['links']):
                show('{}) {}'.format(i, o['name']))

            show('\n\n\n')
            s.reset_input_buffer()
            if len(data['links']) == 0:
                continue
            try:
                choice = get_choice(s, len(data['links']), websocket)
            except RequestRestart:
                message = json.dumps({ 'restart': 'please' })
                show('[restart]\n')
                await websocket.send(message)
                continue

            passage = data['links'][choice]['passage']
            message = json.dumps({ 'passage': passage })
            await websocket.send(message)

        print('disconnected.\nwaiting for twine connection... (may need to restart twine)')
    return handler


if __name__ == '__main__':
    import sys
    try:
        port = sys.argv[1]
    except IndexError:
        maybes = list(list_ports.grep('usb'))
        if len(maybes) == 0:
            sys.stderr.write('missing serial port (probably /dev/tty.usbserial-something)\n')
            sys.exit(1)
        if len(maybes) > 1:
            sys.stderr.write('not sure which serial port to use. likely candidates:\n{}\n'.format(
                '\n'.join(map(lambda m: '{}\t{}\t{}'.format(m.device, m.description, m.manufacturer), maybes))))
            sys.exit(1)
        port = maybes[0].device

    ser = Serial(port, 9600)
    sleep(1)  # ignore first reset
    printer_config(ser)

    asyncio.get_event_loop().run_until_complete(
        websockets.serve(play(ser), 'localhost', 5000))
    print('started websocket server\nwaiting for twine connection... (may need to restart twine)')

    asyncio.get_event_loop().run_forever()
    print('bye!')
