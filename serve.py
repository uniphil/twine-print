#!venv/bin/python
#!/usr/bin/env python

import asyncio
import websockets
from time import sleep
from serial import Serial
import json

UPDOWN_MASK = 1 << 2

def get_choice(s, n):
    msg = 'button options: {}\n\n\n'\
        .format(', '.join(map(str, range(n))))\
        .encode('ascii')
    while True:
        c = s.read(1)
        try:
            choice = int(c)
        except ValueError:
            s.write(msg)
            continue
        if choice < 0 or choice > n -1:
            s.write(msg)
            continue
        return choice


def play(s):

    async def handler(websocket, path):

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
            choice = get_choice(s, len(data['links']))

            passage = data['links'][choice]['passage']
            message = json.dumps({ 'passage': passage })
            await websocket.send(message)
    return handler


if __name__ == '__main__':
    import sys
    try:
        port = sys.argv[1]
    except IndexError:
        sys.stderr.write('missing serial port (probably /dev/tty.usbserial-something)\n')
        sys.exit(1)

    ser = Serial(port, 9600)

    asyncio.get_event_loop().run_until_complete(
        websockets.serve(play(ser), 'localhost', 5000))
    print('started websocket server')

    asyncio.get_event_loop().run_forever()
    print('bye!')
