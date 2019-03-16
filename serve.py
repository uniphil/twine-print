#!venv/bin/python
#!/usr/bin/env python

import asyncio
import websockets
from time import sleep
from serial import Serial
from serial.tools import list_ports
import json

class RequestRestart(Exception):
    pass


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

        def show(m):
            print(m)
            s.write(m.encode('ascii'))
            s.write(b'\n')

        async for message in websocket:
            data = json.loads(message)
            show(data['text'])
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

    asyncio.get_event_loop().run_until_complete(
        websockets.serve(play(ser), 'localhost', 5000))
    print('started websocket server\nwaiting for twine connection... (may need to restart twine)')

    asyncio.get_event_loop().run_forever()
    print('bye!')
