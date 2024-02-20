import asyncio
import websockets


# identifies the port
PORT = 25565

# identifies the hostname
HOST = "rx-78-2"

# sets the trust message that essentially acts as a secondary handshake
TRUST_MESSAGE = "Shake my hand bro"

# sets the message that will indicate a disconnection 
DISCONNECT_MESSAGE = "END-OF-LINE"

# handles a new connection
async def handler(websocket):
    print(f"CONNECTION RECIEVED")

    connected = True

    first_msg = await websocket.recv()
    if first_msg != TRUST_MESSAGE:
        connected = False
        print("Blud did not shake my hand lmao")
        websocket.close()
        return


    while connected:
        msg = await websocket.recv()
        if msg == DISCONNECT_MESSAGE:
            connected = False;
            break
        print(msg)
        await websocket.send("return turtle.turnRight()")

    print("CLOSING SOCKET")




start_server = websockets.serve(handler, HOST, PORT, ssl=None, compression=None)
print("STARTING SERVER")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()