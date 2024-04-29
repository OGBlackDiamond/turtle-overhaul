from websockets.sync.server import ServerConnection
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

    task:str

    def __init__(self, websocket: ServerConnection, master_control_program,
                 parent, gameID: int, parentID: int=-1,
                 coords: list[int]=[0, 0, 0], json: dict={}, is_recovering: bool=False):

        # the connection satatus of the turtle, its websocket, and parent object
        self.connected = True;
        self.websocket = websocket
        self.master_control_program = master_control_program
        self.parent = parent

        # the in-game id's of the turtle and it's parent
        self.gameID = gameID
        self.parentID = parentID

        # two lists to store the turtle's messages and the command queue
        self.queue = []
        self.messages = []

        # the current task of the turtle
        self.task = "coaling"

        # these values will store the x or z offset value for the block in front of the turtle
        self.x_offset = 0
        self.z_offset = 0

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
                self.coaling()




    # turtle will prioritize mining for coal
    def coaling(self, offset: int=0):
        if self.y < 56 + offset:
            self.up(True)
            self.turn(turns=4)

        elif self.y > 56 + offset:
            self.down(True)
            self.turn(turns=4)

        else:
            self.forward(True)
            self.turn()
            self.turn("left", 2)
            self.turn()

    # basic idle function, turtle will simply spin in place
    def idle(self):
        self.turn()













#######################################
########## BOILERPLATE CODE ###########
#######################################



    # series of functions that give the turtle direct instructuons
    # this is simply to make my life programming easier
    def queue_instruction(self, instructions: str):
        self.queue.append(instructions)

    # moves the turtle forward, optionally digs
    def forward(self, dig: bool=False):
        if dig:
            self.dig()
        self.queue_instruction("turtle.forward()")

    # moves the turtle backwards
    def back(self):
        self.queue_instruction("turtle.back()")

    # options: right, left
    def turn(self, direction: str="right", turns: int=1):
        for i in range(turns):
            self.queue_instruction(f"turtle.turn{direction.capitalize()}()")

    # moves the turtle up, optionally digs
    def up(self, dig: bool=False):
        if dig:
            self.dig("up")
        self.queue_instruction("turtle.up()")

    # moves the turtle down, optionally digs
    def down(self, dig: bool=False):
        if dig:
            self.dig("down")
        self.queue_instruction("turtle.down()")

    # options: "", up, down
    def dig(self, direction: str=""):
        self.queue_instruction(f"turtle.dig{direction.capitalize()}()")


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

        # handles turtle forward movement
        if command == "turtle.forward()" and status:
            self.x += self.x_offset
            self.z += self.z_offset

        # handles turtle reverse movement
        elif command == "turtle.back()" and status:
            self.x += self.x_offset * -1
            self.z += self.z_offset * -1

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
        self.heading %= 4

    # handles message sending 
    async def exec(self, message: str):
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

        # tell the mcp the turtle's position in 3d space
        self.master_control_program.set_block(self.x, self.y, self.z, "computercraft:turtle_normal")

        # give mcp newly discovered world data
        self.master_control_program.set_block(self.x, self.y - 1, self.z, data_json["down"])

        self.master_control_program.set_block(self.x + self.x_offset, self.y, self.z + self.z_offset, data_json["front"])

        self.master_control_program.set_block(self.x, self.y + 1, self.z, data_json["up"])



        # parse the json for the status
        status = data_json["return"]["status"]

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