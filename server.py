import asyncio
import websockets


PORT = 25565
HOST = "rx-78-2"

DISCONNECT_MESSAGE = "END-OF-LINE"


async def handler(websocket):
    print(f"CONNECTION RECIEVED")

    connected = True

    while connected:
        msg = await websocket.recv()
        if msg == DISCONNECT_MESSAGE:
            connected = False;
            break
        print(msg)
        await websocket.send(msg)

    print("CLOSING SOCKET")
    await websocket.close()




start_server = websockets.serve(handler, HOST, PORT, ssl=None, compression=None)
print("STARTING SERVER")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()