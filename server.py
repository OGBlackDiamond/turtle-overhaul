import asyncio
import aioconsole
import websockets.server
from websockets.sync.server import ServerConnection
from turtle_stuff.turtle import Turtle
from worlds.json_manager import Json_Manager
from mcp import Master_Control_Program

class Server:

    def __init__(self, 
                 json_manager: Json_Manager, 
                 mcp: Master_Control_Program
                 ):

        # defines the json manager and mcp
        self.mcp = mcp
        self.json_manager = json_manager

        # hands the selected world data to the mcp to be loaded
        self.mcp.set_world(self.json_manager.get_world())

        # identifies the hostname
        self.HOST = "rx-78-2"
        # identifies the port
        self.PORT = 3000

        # sets the trust message that essentially acts as a secondary handshake
        self.TURTLE_MESSAGE = "shake-my-hand-bro"

    # handles a new connection
    async def handle_connect(self, websocket: ServerConnection):
        print(f"CONNECTION RECIEVED @ {websocket.remote_address[0]}")

        # receives the secondary handshake
        first_msg = await websocket.recv() # type: ignore

        # accepts or denys the handshake
        if first_msg != self.TURTLE_MESSAGE:
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
                turtle = self.mcp.set_websocket(websocket, turtle_id) # type: ignore

                # if a turtle object doesn't exist, recover it from json
                if turtle == None:

                    # gather data
                    turtles_json = self.json_manager.restore_turtles()

                    turtle_json = turtles_json[f"turtle{turtle_id}"]

                    neo_parent_id = turtle_json["parentID"]

                    parent = self.mcp.find_turtle(neo_parent_id)

                    # create new instance with stored data
                    turtle = Turtle(
                        websocket=websocket, 
                        master_control_program=self.mcp,
                        parent=parent, 
                        gameID=turtle_id, 
                        parentID=neo_parent_id, 
                        json=turtle_json, 
                        is_recovering=True)

                    # add the turtle to the arrays of turtles
                    self.mcp.add_turtle(turtle)

            else:

                ### HANDLES INITIAL TURTLE CONNECTION ###

                parent = self.mcp.find_turtle(parent_id)

                turtle = Turtle(
                    websocket=websocket, 
                    master_control_program=self.mcp,
                    parent=parent, 
                    gameID=turtle_id,
                    coords=self.mcp.get_start_coords())

                self.mcp.add_turtle(turtle)
                await turtle.set_name()

            while turtle.connected:
                await turtle.main()
                await asyncio.sleep(0.25)


            websocket.close()
        print("CLOSING SOCKET")

    # this will get user input asynchronously
    async def console(self):
        while True:
            line = await aioconsole.ainput('->')
            if line == "stop":
                self.json_manager.dump_turtles(self.mcp.get_turtles())
                self.json_manager.write_to_world(self.mcp.get_world())
                asyncio.get_event_loop().stop()
            elif line == "save":
                self.json_manager.dump_turtles(self.mcp.get_turtles())
                self.json_manager.write_to_world(self.mcp.get_world())
            elif line == "stats":
                print("SERVER STATISTICS")
                print(f"Connected Turtles: {len(self.mcp.get_turtles())}")

    async def start_mcp(self):
        while True:
            self.mcp.main()
            self.json_manager.dump_turtles(self.mcp.get_turtles())
            self.json_manager.write_to_world(self.mcp.get_world())
            await asyncio.sleep(0.25)

    # the main function that will start the server and console
    def main(self):
        start_server = websockets.server.serve(self.handle_connect, self.HOST, self.PORT, ssl=None, compression=None) # type: ignore
        print("STARTING SERVER")
        asyncio.gather(
            self.console(),
            self.start_mcp()
        )

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()