#!/usr/bin/env python

import asyncio
import websockets
from serial import Serial
import json

UPDOWN_MASK = 1 << 2


async def play(websocket, path):
    s = Serial('/dev/cu.usbmodem461', 9600)

    s.write(0x00)
    s.write(0xFF)
    s.write(0x1B)  # esc
    s.write(0x21)  # '!'
    s.write(UPDOWN_MASK)

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
        choice = s.read(1)

        passage = data['links'][int(choice)]['passage']
        message = json.dumps({ 'passage': passage })
        await websocket.send(message)

asyncio.get_event_loop().run_until_complete(
    websockets.serve(play, 'localhost', 5000))
asyncio.get_event_loop().run_forever()

