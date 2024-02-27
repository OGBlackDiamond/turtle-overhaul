import asyncio
import websockets

async def hello(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            await websocket.send("Hello there from 2")
            greeting = await websocket.recv()
            print(f"Received: {greeting}")

asyncio.run(hello('ws://rx-78-2:3000'))