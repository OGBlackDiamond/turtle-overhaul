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

    def __init__(self, websocket, parent):
        self.connected = True;
        self.websocket = websocket
        self.queue = []
        self.messages = []
        self.parent = parent

        if self.parent == None:
            self.x = 0
            self.y = 0
            self.z = 0
            self.heading = 0
            self.type = "M"
            self.pyd_pos = 0

        else:
            self.heading = parent.heading

            # correctly gives world coordinates based on heading
            if self.heading == 0:
                self.z = parent.z - 1
            elif self.heading == 1:
                self.x = parent.x + 1
            elif self.heading == 2:
                self.z = parent.z + 1
            elif self.heading == 3:
                self.x = parent.x - 1
            self.y = parent.y

            self.type = "U"
            self.pyd_pos = parent.pyd_pos + 1

        self.ucount = 0


    async def main(self):

        command = ""

        if (len(self.queue) > 0):
            command = self.queue.pop(0)
        else:
            command = "print(\"waiting for instructions\")"

        await self.exec(command)

        response = await self.recv()

        if response == DISCONNECT_MESSAGE:
            self.connected = False

        # checks if the turtle moved an updates its coordinates
        self.handle_movement(command, response)

    def queue_instruction(self, instructions):
        self.queue.append(instructions)

    # handles coordinate and heading updates when moving
    def handle_movement(self, command, status):

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
        elif command == "turtle.down()" and status:
            self.y -= 1;

        # handles rotations
        elif command == "turtle.turnRight()" and status:
            self.heading += 1
        elif command == "turtle.turnLeft()" and status:
            self.heading -= 1

        # handles rotation overflow
        if self.heading > 3:
            self.heading -= 4
        elif self.heading < 0:
            self.heading += 4



    # handles message sending 
    async def exec(self, message):
        await self.websocket.send(f"{TYPE_EXEC}return {message}")

    # handles incoming messages
    async def recv(self):
        self.messages.append(await self.websocket.recv())

    # sends formatted name data
    async def set_name(self):
        await self.websocket.send(f"{TYPE_NAME}{self.type}.{self.pyd_pos}-{self.ucount}")

    # sends the clone command
    async def clone(self):
        await self.websocket.send(TYPE_CLONE)
        # checks if the cloning succeeded or not
        if await self.websocket.recv() == TRUE:
            self.ucount += 1
            self.set_name()