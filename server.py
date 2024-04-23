import asyncio
import aioconsole
import websockets.server
from websockets.sync.server import ServerConnection
from turtle_stuff.turtle import Turtle
from worlds import json_manager
from mcp import Master_Control_Program



# identifies the port
PORT = 3000

# identifies the hostname
HOST = "rx-78-2"

# sets the trust message that essentially acts as a secondary handshake
TURTLE_MESSAGE = "shake-my-hand-bro"

mcp = Master_Control_Program()

# handles a new connection
async def handle_connect(websocket: ServerConnection):
    print(f"CONNECTION RECIEVED @ {websocket.remote_address[0]}")

    # receives the secondary handshake
    first_msg = await websocket.recv() # type: ignore

    # accepts or denys the handshake
    if first_msg != TURTLE_MESSAGE:
        print("Connection Refused")
        await websocket.send("return print('Connection Refused')") # type: ignore
        await websocket.close() # type: ignore
    else:
        print("Connection Established")
        await websocket.send("return print('Connection Established')") # type: ignore

        # waits for the turtle to send up it's and it's parent's ID
        turtle_id = await websocket.recv() # type: ignore
        parent_id = await websocket.recv() # type: ignore
        turtle:Turtle = None # type: ignore
        parent:Turtle = None # type: ignore

        # a parentID of -1 indicates that this turtle needs to reconnect, and a new turtle class should not be created, except from json
        if parent_id == "-1":

            ### HANDLES TURTLE RECONNECTION ###

            # attempt to recconnect the turtle to it's websocket if it exists
            turtle = mcp.set_websocket(websocket, turtle_id) # type: ignore

            # if a turtle object doesn't exist, recover it from json
            if turtle == None:

                # gather data
                turtles_json = json_manager.restore_turtles()

                turtle_json = turtles_json[f"turtle{turtle_id}"]

                neo_parent_id = turtle_json["parentID"]

                parent = mcp.find_turtle(neo_parent_id)

                # create new instance with stored data
                turtle = Turtle(
                    websocket=websocket, 
                    parent=parent, 
                    gameID=turtle_id, 
                    parentID=neo_parent_id, 
                    json=turtle_json, 
                    is_recovering=True)

                # add the turtle to the arrays of turtles
                mcp.add_turtle(turtle)
                mcp.add_turtle(turtle)

        else:

            ### HANDLES INITIAL TURTLE CONNECTION ###

            parent = mcp.find_turtle(parent_id)

            turtle = Turtle(
                websocket=websocket, 
                parent=parent, 
                gameID=turtle_id,
                coords=mcp.get_start_coords())

            mcp.add_turtle(turtle)
            mcp.add_turtle(turtle)
            await turtle.set_name()

        while turtle.connected:
            await turtle.main()


        websocket.close()
    print("CLOSING SOCKET")

# this will get user input asynchronously
async def console():
    while True:
        line = await aioconsole.ainput('->')
        if line == "stop":
            json_manager.dump_turtles(mcp.get_turtles())
            asyncio.get_event_loop().stop()
        elif line == "save":
            json_manager.dump_turtles(mcp.get_turtles())
        elif line == "stats":
            print("SERVER STATISTICS")
            print(f"Connected Turtles: {len(mcp.get_turtles())}")

async def test():
    while True:
        mcp.main()
        await asyncio.sleep(0.125)

# the main function that will start the server and console
def main():
    start_server = websockets.server.serve(handle_connect, HOST, PORT, ssl=None, compression=None) # type: ignore
    print("STARTING SERVER")
    asyncio.gather(
        console(),
        test()
    )

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()