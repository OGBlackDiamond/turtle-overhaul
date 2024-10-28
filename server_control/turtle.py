from enum import IntEnum
import json

from websockets.sync.server import ServerConnection

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server_control.mcp import Master_Control_Program

# sets the message that will indicate a disconnection
DISCONNECT_MESSAGE = "END-OF-LINE"

# defines data types used to identify outgoing data
TYPE_EXEC = "[e]"
TYPE_MINE = "[m]"
TYPE_CLONE = "[c]"
TYPE_NAME = "[n]"


# defines data expressions for incoming data
TRUE = "{T}"
FALSE = "{F}"

# heading numbers for refrence
"""
north = 0 - negative z
east = 1 - positive x
south = 2 - positive z
west = 3 - negative x
"""


class Turtle:

    class Heading(IntEnum):
        NORTH = 0
        EAST = 1
        SOUTH = 2
        WEST = 3

    class Status(IntEnum):
        IDLE = 0
        GOTO = 1
        MANUAL = 2
        

    connected: bool
    websocket: ServerConnection
    master_control_program: 'Master_Control_Program'
    parent: 'Turtle'

    gameID: int
    parentID: int

    queue: list[str]
    messages: list[dict]

    fuel: int

    task: Status 

    startx: int
    startz: int

    start_fuel: int

    is_deep: bool

    x: int
    y: int
    z: int

    heading: Heading 

    type: str
    pyd_pos: int

    line_stepper: int
    destination: list[tuple[int, int, int]]

    def __init__(
        self,
        websocket: ServerConnection,
        master_control_program: 'Master_Control_Program',
        parent: 'Turtle',
        gameID: int,
        parentID: int = -1,
        coords: list[int] = [0, 0, 0],
        json: dict = {},
        is_recovering: bool = False,
    ):

        # the connection satatus of the turtle, its websocket, and parent object
        self.connected = True
        self.websocket = websocket
        self.master_control_program = master_control_program
        self.parent = parent

        # the in-game id's of the turtle and it's parent
        self.gameID = gameID
        self.parentID = parentID

        # two lists to store the turtle's messages and the command queue
        self.queue = []
        self.messages = []

        self.fuel = 0

        # the current task of the turtle
        self.task = self.Status.IDLE

        # fuel value at the start of the mining section
        self.start_fuel = 0

        # bool if the turtle can start tunneling
        self.is_deep = False

        # global values that handle travel across the world
        self.line_stepper = 0
        self.destination = [(0, 0, 0)]

        # if this turtle is not recovering from json
        if is_recovering == False:

            # this turtle has no parent, it will be the master turtle
            if self.parent == None:
                self.start_master(coords[0], coords[1], coords[2])

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

        # if there are commands in the queue, execute them
        if len(self.queue) > 0:
            # gets the next command to execute from the stack
            command = self.queue.pop(0)
            # sends the command and awaits a response
            await self.exec(command)
            await self.recv()

        # if the queue is empty, allow new commands to be queued
        else:
            match (self.task):
                case self.Status.IDLE:
                    self.idle()
                case self.Status.GOTO:
                    self.go_to_destination()
                # this is kinda just so that the mcp can take a pause to queue other commands
                case self.Status.MANUAL:
                    pass

    # this needs to be re-implemented at some point
    def mine(self):
        pass

    # basic idle function, turtle will simply spin in place
    def idle(self):
        self.turn()

    # tells the turtle to move to the current destination value
    def go_to_destination(self):
        if self.step_to(self.destination[self.line_stepper][0], self.destination[self.line_stepper][1], self.destination[self.line_stepper][2]):
            self.line_stepper += 1
            print(f"{self.x}, {self.y}, {self.z}")

    # turtle tunnels for a certain length, optionally mining for goodies
    def tunnel(self, length: int, search: bool=True):
        for _ in range(length):
            if search : self.mine_valuables()
            self.forward()

    #######################################
    ############# HELPER CODE #############
    #######################################


    # calling this will take one step to the specified coordinate point, x takes precedence
    # returns true if turtle is at the given coordinates, false if not
    def step_to(self, x, y, z) -> bool:
        # reutrns true if the turtle is at the specified coordinates
        if self.x == x and self.y == y and self.z == z:
            return True

        turns = 0

        if self.x != x:
            turns = (3 if self.x > x else 1) - self.heading

        elif self.z != z:
            turns = (0 if self.z > z else 2) - self.heading
            

        self.turn("right" if turns > 0 else "left", self.abs(turns))

        self.forward(True)

        # moves the turtle to correct the y value
        if self.y > y:
            self.down(True)
        elif self.y < y:
            self.up(True)

        return False


    # generates a list of coordinate points from the turtle's position to the target
    def line_3d(self, x, y, z):
        points = []
        points.append((x, y, z))
        dx = abs(self.x - x)
        dy = abs(self.y - y)
        dz = abs(self.z - z)
        if (self.x > x):
            xs = 1
        else:
            xs = -1
        if (self.y > y):
            ys = 1
        else:
            ys = -1
        if (self.z > z):
            zs = 1
        else:
            zs = -1

        # Driving axis is X-axis"
        if (dx >= dy and dx >= dz):	 
            p1 = 2 * dy - dx
            p2 = 2 * dz - dx
            while (x != self.z):
                x += xs
                if (p1 >= 0):
                    y += ys
                    p1 -= 2 * dx
                if (p2 >= 0):
                    z += zs
                    p2 -= 2 * dx
                p1 += 2 * dy
                p2 += 2 * dz
                points.append((x, y, z))

        # Driving axis is Y-axis"
        elif (dy >= dx and dy >= dz):	 
            p1 = 2 * dx - dy
            p2 = 2 * dz - dy
            while (y != self.y):
                y += ys
                if (p1 >= 0):
                    x += xs
                    p1 -= 2 * dy
                if (p2 >= 0):
                    z += zs
                    p2 -= 2 * dy
                p1 += 2 * dx
                p2 += 2 * dz
                points.append((x, y, z))

        # Driving axis is Z-axis"
        else:	 
            p1 = 2 * dy - dz
            p2 = 2 * dx - dz
            while (z != self.z):
                z += zs
                if (p1 >= 0):
                    y += ys
                    p1 -= 2 * dz
                if (p2 >= 0):
                    x += xs
                    p2 -= 2 * dz
                p1 += 2 * dy
                p2 += 2 * dx
                points.append((x, y, z))

        points.reverse()

        return points

    # series of functions that give the turtle direct instructions
    # this is simply to make my life programming easier
    def queue_instruction(self, instructions: str):
        self.queue.append(instructions)

    # moves the turtle forward, optionally digs
    def forward(self, dig: bool = False):
        if dig:
            self.dig()
        self.queue_instruction("turtle.forward()")

    # moves the turtle backwards
    def back(self):
        self.queue_instruction("turtle.back()")

    # options: right, left
    def turn(self, direction: str = "right", turns: int = 1):
        for _ in range(turns):
            self.queue_instruction(f"turtle.turn{direction.capitalize()}()")

    # moves the turtle up, optionally digs
    def up(self, dig: bool = False):
        if dig:
            self.dig("up")
        self.queue_instruction("turtle.up()")

    # moves the turtle down, optionally digs
    def down(self, dig: bool = False):
        if dig:
            self.dig("down")
        self.queue_instruction("turtle.down()")

    # tells the turtle to check and mine if valuables are near
    def mine_valuables(self):
        self.queue_instruction(TYPE_MINE)

    # options: "", up, down
    def directional_command(self, command: str, direction: str = ""):
        if (direction in ("up", "down", "")): 
            print("[ERROR] Invalid direction for directional command!")
            return
        self.queue_instruction(f"turtle.{command.lower()}{direction.capitalize()}()")

    def dig(self, direction: str = ""):
        self.directional_command("dig", direction)

    def drop(self, direction: str = ""):
        self.directional_command("drop", direction)

    def suck(self, direction: str = ""):
        self.directional_command("suck", direction)

    def check_inv(self, item: str) -> dict:
        return_json= {
            "count": -1,
            "index": -1
        }

        for index, slot in enumerate(self.messages[0]["inventory"].values()):
            if item == slot["name"]:
                return_json["count"] = slot["count"]
                return_json["index"] = index 

        return return_json

    # handles the x and z offset for in front of the turtle
    def handle_offset(self):
        self.x_offset = 0
        self.z_offset = 0

        if self.heading == 0:
            self.z_offset = -1
        elif self.heading == 1:
            self.x_offset = 1
        elif self.heading == 2:
            self.z_offset = 1
        elif self.heading == 3:
            self.x_offset = -1

    # handles coordinate and heading updates when moving
    def handle_movement(self, command: str, status: bool):

        command = command[7:]

        self.handle_offset()

        # handles turtle forward movement
        if command == "turtle.forward()" and status:
            self.x += self.x_offset
            self.z += self.z_offset

        # handles turtle reverse movement
        elif command == "turtle.back()" and status:
            self.x -= self.x_offset
            self.z -= self.z_offset

        # handles turtle vertical movement
        elif command == "turtle.up()" and status:
            self.y += 1
        elif command == "turtle.down()" and status:
            self.y -= 1

        # handles rotations
        elif command == "turtle.turnRight()" and status:
            self.heading = self.Heading(self.heading + 1)
        elif command == "turtle.turnLeft()" and status:
            self.heading = self.Heading(self.heading - 1)

        # handles rotation overflow
        self.heading = self.Heading(self.heading % 4)

    # handles message sending
    async def exec(self, message: str):
        await self.websocket.send(f"{TYPE_EXEC}return {message}")  # type: ignore

    # handles incoming messages
    async def recv(self) -> bool:
        # clears out message data so that there are only 5 messages in the list at a time
        if len(self.messages) > 5:
            self.messages.pop()

        data = await self.websocket.recv()  # type: ignore

        # if the turtle is disconnecting, disconnect
        if data == DISCONNECT_MESSAGE:
            self.connected = False
            return True

        # loads the data as a json object
        data_json = json.loads(data)

        # add the json object to the message queue
        self.messages.insert(0, data_json)

        # gets the blocks in front of the turtle
        down = data_json["down"]
        front = data_json["front"]
        up = data_json["up"]

        # tell the mcp the turtle's position in 3d space
        self.master_control_program.set_block(
            self.x, self.y, self.z, "computercraft:turtle_normal"
        )

        # give mcp newly discovered world data
        self.master_control_program.set_block(
            self.x, self.y - 1, self.z, down if down != "nil" else "minecraft:air"
        )

        self.master_control_program.set_block(
            self.x + self.x_offset,
            self.y,
            self.z + self.z_offset,
            front if front != "nil" else "minecraft:air",
        )

        self.master_control_program.set_block(
            self.x, self.y + 1, self.z, up if up != "nil" else "minecraft:air"
        )

        # if there the turtle just moved past a space, set the block behind it to air
        if self.messages[1 if len(self.messages) > 1 else 0]["return"]["command"] == "return turtle.forward()":
            self.master_control_program.set_block(
                self.x - self.x_offset, self.y, self.z - self.z_offset, "minecraft:air"
            )

        # parse the json for the status
        status = data_json["return"]["status"]

        # sets the fuel value
        self.fuel = data_json["fuel"]

        # returns a python boolean value
        if status == TRUE:
            status = True
        else:
            status = False

        # update odometry based on the command and its success
        self.handle_movement(data_json["return"]["command"], status)

        return status

    # gets the message at a particular index
    def get_message(self, index=0):
        return self.messages[index]

    # returns the length of the queue
    def get_queue_length(self):
        return len(self.queue)

    def checkFuel(self, used: int) -> bool:
        return self.fuel >= used

    # return the absolute value of num
    def abs(self, num: int):
        if num > 0:
            return num
        else:
            return num * -1

    # return the sign (+/-) of num
    def sign(self, num: int):
        if num > 0:
            return 1
        else:
            return -1

    # sends formatted name data
    async def set_name(self):
        await self.websocket.send(f"{TYPE_NAME}{self.type}.{self.pyd_pos}-{self.ucount}")  # type: ignore

    # sends the clone command
    async def clone(self):
        await self.websocket.send(TYPE_CLONE)  # type: ignore
        # checks if the cloning succeeded or not
        if await self.websocket.recv() == TRUE:  # type: ignore
            self.ucount += 1
            await self.set_name()

    #######################################
    ######### CONSTRUCTOR OPTIONS #########
    #######################################

    def start_master(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z
        self.heading = self.Heading(0)
        self.type = "M"
        self.pyd_pos = 0

    def parent_exists(self):
        self.heading = self.parent.heading

        self.handle_offset()
        # correctly gives world coordinates based on heading
        self.x = self.parent.x + self.x_offset * -1
        self.z = self.parent.z + self.z_offset * -1

        self.y = self.parent.y

        self.type = "U"
        self.pyd_pos = self.parent.pyd_pos + 1

    def recover_from_json(self, json: dict):
        self.x = json["coords"]["x"]
        self.y = json["coords"]["y"]
        self.z = json["coords"]["z"]

        self.heading = json["heading"]

        self.type = json["type"]

        self.pyd_pos = json["pyd_pos"]

        self.ucount = json["ucount"]

        self.queue = json["io"]["messages"]

        self.queue = json["io"]["queue"]
