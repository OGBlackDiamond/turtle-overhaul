from websockets.sync.server import ServerConnection
import asyncio
import json

# sets the message that will indicate a disconnection 
DISCONNECT_MESSAGE = "END-OF-LINE"

# defines data types used to identify outgoing data
TYPE_EXEC = "[e]"
TYPE_CLONE = "[c]"
TYPE_NAME = "[n]"


# defines data expressions for incoming data
TRUE = "{T}"
FALSE = "{F}"


"""
Turtle naming convention:
{type}.{pyramid position}-{number}-{revision}

Type:
    The type of turtle:

M: Master - the first turtle, acts like an overlord
O: Overlord - controls a subset of other turtles and largely handles incoming resources from the underlings
U: Underling - standard worker drone, the first underling a turtle creates should be equipped with the necessary ability to clone

    An underling gets promoted to an overlord when it has 3 underlings that have cloned from it
    Only 1 master turtle can exist for any given websocket.

Pyramid position:
    The position of the turtle on the pyramid. 
    Example: Master turtle is level 0, because it is the tip. 
    An underling that master creates would be 1, and underling that it creates is 2, and so on.

Number:
    A count of how many underlings exist under a particular turtle.
    Example: The first underling a turtle creates will be named "U.X-1-X" The second one it creates would be "U.X-2-X" and so on.

Revision:
    This number represents the version of 'startup.lua' that a particular turtle is running.

    For example, the Master turtle will probably be running ver 1.0, while a newly created underling might be running version 2.3


Example names w/ description

"M.0-7-1.0" - The master turtle, with 7 underlings, running version 1.0 of the turtle code.

"O.2-3-1.3" - An overlord turtle, which has 3 turtles above it, 3 underlings, running version 1.3 of the turtle code.

"U.5-1-2.4" - An underling turtle, which has 6 turtles above it, 1 underling, running version 2.4 of the turtle code.
"""


# heading numbers for refrence
"""
north = 0
east = 1
south = 2
west = 3
"""

class Turtle:

    connected: bool
    websocket: ServerConnection

    gameID: int
    parentID: int

    queue: list[str]
    messages: list[dict]

    x: int
    y: int
    z: int

    heading: int

    type: str
    pyd_pos: int

    def __init__(self, 
                 websocket: ServerConnection,
                 parent,
                 gameID: int,
                 parentID: int=-1,
                 coords: list[int]=[0, 0, 0],
                 json: dict={},
                 is_recovering: bool=False
                ):

        # the connection satatus of the turtle, its websocket, and parent object
        self.connected = True;
        self.websocket = websocket
        self.parent = parent

        # the in-game id's of the turtle and it's parent
        self.gameID = gameID
        self.parentID = parentID

        self.queue = []
        self.messages = []

        # if this turtle is not recovering from json
        if is_recovering == False:

            # this turtle has no parent, it will be the master turtle
            if self.parent == None:
                self.start_master(coords[0], coords[1], coords[3])

            # a parent turtle exists, it's telemetry will be translated to it
            else:
                self.parent_exists()

            self.ucount = 0

        # turtle recovery from json
        else:
           self.recover_from_json(json)




###########################
##### MAIN CODE START #####
###########################


    async def main(self):

        self.queue_instruction("print('greetings program')")

        if len(self.queue) > 0:
            # gets the next command to execute from the stack
            command = self.queue.pop(0)

            # sends the command and awaits a response
            await self.exec(command)
            await self.recv()

        await asyncio.sleep(0.25)























#######################################
########## BOILERPLATE CODE ###########
#######################################



    # series of functions that give the turtle direct instructuons
    # this is simply to make my life programming easier
    def queue_instruction(self, instructions):
        self.queue.append(instructions)

    def forward(self):
        self.queue_instruction("turtle.forward()")

    def back(self):
        self.queue_instruction("turtle.back()")

    # options: right, left
    def turn(self, direction="right"):
        self.queue_instruction(f"turtle.turn{direction.capitalize()}()")

    def up(self):
        self.queue_instruction("turtle.Up()")

    def down(self):
        self.queue_instruction("turtle.Down()")

    # options: "", up, down
    def dig(self, direction=""):
        self.queue_instruction(f"turtle.dig{direction.capitalize()}()")


    # handles coordinate and heading updates when moving
    def handle_movement(self, command, status):

        command = command[7:]

        # handles turtle forward movement
        if command == "turtle.forward()" and status:
            if self.heading == 0:
                self.z -= 1
            elif self.heading == 1:
                self.x += 1
            elif self.heading == 2:
                self.z += 1
            elif self.heading == 3:
                self.x -= 1

        # handles turtle reverse movement
        elif command == "turtle.back()" and status:
            if self.heading == 0:
                self.z += 1
            elif self.heading == 1:
                self.x -= 1
            elif self.heading == 2:
                self.z -= 1
            elif self.heading == 3:
                self.x += 1

        # handles turtle vertical movement
        elif command == "turtle.up()" and status:
            self.y += 1
        elif command == "turtle.down()":
            self.y -= 1;

        # handles rotations
        elif command == "turtle.turnRight()" and status:
            self.heading += 1
        elif command == "turtle.turnLeft()" and status:
            self.heading -= 1

        # handles rotation overflow
        self.heading %= 4

    # handles message sending 
    async def exec(self, message):
        await self.websocket.send(f"{TYPE_EXEC}return {message}") #type: ignore

    # handles incoming messages
    async def recv(self):
        # clears out message data so that there are only 5 messages in the list at a time
        if len(self.messages) > 5:
            self.messages.pop()

        data = await self.websocket.recv() #type: ignore

        # if the turtle is disconnecting, disconnect
        if data == DISCONNECT_MESSAGE:
            self.connected = False
            return


        # loads the data as a json object
        data_json = json.loads(data)

        # add the json object to the message queue
        self.messages.insert(0, data_json)

        # parse the json for the status
        status = data_json["return"]["status"]

        # returns a python boolean value
        if status == TRUE:
            status = True
        else:
            status = False

        self.handle_movement(data_json["return"]["command"], status)


        return status

    # gets the message at a particular index
    def get_message(self, index=0):
        return self.messages[index]

    # returns the length of the queue
    def get_queue_length(self):
        return len(self.queue)

    # sends formatted name data
    async def set_name(self):
        await self.websocket.send(f"{TYPE_NAME}{self.type}.{self.pyd_pos}-{self.ucount}") #type: ignore

    # sends the clone command
    async def clone(self):
        await self.websocket.send(TYPE_CLONE) #type: ignore
        # checks if the cloning succeeded or not
        if await self.websocket.recv() == TRUE: #type: ignore
            self.ucount += 1
            await self.set_name()




#######################################
######### CONSTRUCTOR OPTIONS #########
#######################################

    def start_master(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.heading = 0
        self.type = "M"
        self.pyd_pos = 0

    def parent_exists(self):
        self.heading = self.parent.heading
        # correctly gives world coordinates based on heading
        if self.heading == 0:
            self.x = self.parent.x
            self.z = self.parent.z - 1
        elif self.heading == 1:
            self.z = self.parent.z
            self.x = self.parent.x + 1
        elif self.heading == 2:
            self.x = self.parent.x
            self.z = self.parent.z + 1
        elif self.heading == 3:
            self.z = self.parent.z
            self.x = self.parent.x - 1

        self.y = self.parent.y

        self.type = "U"
        self.pyd_pos = self.parent.pyd_pos + 1

    def recover_from_json(self, json):
        self.x = json["coords"]["x"]
        self.y = json["coords"]["y"]
        self.z = json["coords"]["z"]

        self.heading = json["heading"]

        self.type = json["type"]

        self.pyd_pos = json["pyd_pos"]

        self.ucount = json["ucount"]

        self.queue = json["io"]["messages"]

        self.queue = json["io"]["queue"]