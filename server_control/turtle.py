import json

from websockets.sync.server import ServerConnection

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from server_control.mcp import Master_Control_Program

# sets the message that will indicate a disconnection
DISCONNECT_MESSAGE = "END-OF-LINE"

# defines data types used to identify outgoing data
TYPE_EXEC = "[e]"
TYPE_CLONE = "[c]"
TYPE_NAME = "[n]"


# defines data expressions for incoming data
TRUE = "{T}"
FALSE = "{F}"

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
    master_control_program: 'Master_Control_Program'
    parent: 'Turtle'

    gameID: int
    parentID: int

    queue: list[str]
    messages: list[dict]

    fuel: int

    task: str

    startx: int
    startz: int

    start_fuel: int

    is_deep: bool

    x_offset: int
    y_offset: int

    z_offset: int

    x: int
    y: int
    z: int

    heading: int

    type: str
    pyd_pos: int

    task: str

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
        self.task = "idle"

        # point where tunnling starts
        self.startx = 0
        self.startz = 0

        # fuel value at the start of the mining section
        self.start_fuel = 0

        # bool if the turtle can start tunneling
        self.is_deep = False

        # these values will store the x or z offset value for the block in front of the turtle
        self.x_offset = 0
        self.z_offset = 0

        # y offset for strip mining
        self.y_offset = 0

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

            if self.task == "idle":
                self.idle()

            elif self.task == "coaling":
                if self.mine(
                    yval=56,
                    yoffset=self.y_offset,
                    returning=self.fuel < self.start_fuel * (7 / 8),
                ):
                    if self.y_offset >= 1:
                        self.y_offset -= 1
                    else:
                        self.y_offset += 2
                    self.is_deep = False

    # turtle will prioritize mining at the indicated y level with the particular offset
    def mine(self, yval: int = 0, yoffset: int = 0, returning: bool = False):
        if self.y < yval + yoffset:
            self.up(True)
            self.turn(turns=4)

        elif self.y > yval + yoffset:
            self.down(True)
            self.turn(turns=4)

        else:
            if not self.is_deep:
                self.startx = self.x
                self.startz = self.z
                self.start_fuel = self.fuel
                self.is_deep = True
                return False

            if returning:
                if self.go_to(self.startx, self.y, self.startz):
                    self.turn(turns=2)
                    self.up(True)
                    if yoffset >= 1:
                        self.turn("left")
                        self.forward(True)
                        self.forward(True)
                        self.turn("right")
                    else:
                        self.up(True)
                        self.turn("left")
                        self.forward(True)
                        self.turn("right")

                    return True
            else:
                self.forward(True)
                self.turn()
                self.turn("left", 2)
                self.turn()

        return False

    # basic idle function, turtle will simply spin in place
    def idle(self):
        self.turn()

    # tells the turtle to move to the given coordinate points
    def go_to(self, x, y, z):
        for coordinate in self.line_3d(x, y, z):
            while not self.step_to(coordinate[0], coordinate[1], coordinate[2]):
                continue


    #######################################
    ########## BOILERPLATE CODE ###########
    #######################################


    # calling this will take one step to the specified coordinate point, x takes precedence
    # returns true if turtle is at the given coordinates, false if not
    def step_to(self, x, y, z) -> bool:

        # reutrns true if the turtle is at the specified coordinates
        if self.x == x and self.y == y and self.z == z:
            return True

        # checks if the x value of the turtle is correct, and moves accordingly if not
        if self.x != x:
            if self.sign(self.x_offset) != self.sign(x):
                self.turn(turns=2)
            elif self.abs(self.x - x) == self.abs(self.x + self.x_offset - x):
                if self.x > x:
                    self.turn("left")
                else:
                    self.turn("right")
        # once the x value is correct, take steps to correct the z value
        else:
            if self.sign(self.z_offset) != self.sign(z):
                self.turn(turns=2)
            elif self.abs(self.z - z) == self.abs(self.z + self.z_offset - z):
                if self.z > z:
                    self.turn("left")
                else:
                    self.turn("right")

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

    # options: "", up, down
    def dig(self, direction: str = ""):
        self.queue_instruction(f"turtle.dig{direction.capitalize()}()")

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

    # returns the x offset
    def getx_offset(self):
        return self.x_offset

    # return the z offset
    def getz_offset(self):
        return self.z_offset

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
            self.heading += 1
        elif command == "turtle.turnLeft()" and status:
            self.heading -= 1

        # handles rotation overflow
        self.heading %= 4

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
        if self.messages[1]["return"]["command"] == "return turtle.forward()":
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
        self.heading = 0
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
