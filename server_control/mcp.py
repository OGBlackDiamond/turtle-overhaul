from websockets.sync.server import ServerConnection

import server_control.types as Types

from typing import TYPE_CHECKING
if TYPE_CHECKING: from server_control.turtle import Turtle

# this will handle all logic in the autonomous funciton of the turtle swarm
# essentially, turtle orchestration
class Master_Control_Program:

    turtles: list['Turtle']

    # only used if the world hasn't been generated yet
    starting_coords: list[int]
    box_direction: str

    world: dict
    world_data: dict

    # initializes with the origional coordinates that the turtle will spawn at
    def __init__(self, starting_coords: list, box_direction: str):
        self.turtles = []
        # the world will be populated with existing data in server.py
        self.world = {}

        # these will only be used if the world does not exist
        self.starting_coords = starting_coords
        self.box_direction = box_direction

    # for now, this just continues to generate the world around the turtles
    def main(self):
        for turtle in self.turtles:
            self.gen_world(turtle)
            self.decide_task(turtle)
            self.decide_instructions(turtle)


    def decide_task(self, turtle: 'Turtle'):
        if not turtle.startup_chores_complete: return
        if not turtle.task == Types.Task_Status.IDLE: return

        if (turtle.fuel < 500):
            if (turtle.task == Types.Task_Status.COAL): return
            turtle.task = Types.Task_Status.COAL
            turtle.set_destination(turtle.x, 56, turtle.z)
            turtle.set_instruction(Types.Instruction_Status.GOTO)


    def decide_instructions(self, turtle: 'Turtle'):
        if turtle.instruction != Types.Instruction_Status.IDLE: return

        match (turtle.task):

            case(Types.Task_Status.IDLE):
                turtle.set_instruction(Types.Instruction_Status.IDLE)
                
            case(Types.Task_Status.COAL):

                match (turtle.prev_instruction):

                    case(Types.Instruction_Status.GOTO):
                        self.tunnel(turtle)

                    case(Types.Instruction_Status.TUNNLING):
                        pass # TODO: choose how to follow the mining algorithm

                        # finds a valid tunnling location
                        step = 0
                        while (self.check_bounding_wall(
                            True,
                            (turtle.x if True else turtle.z) + (2 * step if step % 2 == 0 else 1 * step),
                            turtle.y - (2 * step if step % 2 == 0 else - 1 * step),
                            )) == -1: 
                            step += 1

                        turtle.set_destination(turtle.x, turtle.y, turtle.z)
                        turtle.set_instruction(Types.Instruction_Status.GOTO)


                

    def controller(self):
        pass


    def tunnel(self, turtle: 'Turtle'):

        turtle_position = turtle.x if (self.world["bounding_box"]["infinite_dimension"] == "z") else turtle.z
        left_wall: bool = abs(turtle_position - self.world["bounding_box"]["box_range"][0]) < abs(turtle_position - self.world["bounding_box"]["box_range"][1])

        heading: int = 0 if turtle.z == turtle_position else 1
        if not left_wall: heading += 2

        turtle.turn_to(heading)

        dist = turtle.fuel - len(turtle.line_3d(
            self.world["deposit_block"][0],
            self.world["deposit_block"][1],
            self.world["deposit_block"][2]
        )) - 10

        turtle.tunnel(int(dist / 8))

        turtle.set_instruction(Types.Instruction_Status.TUNNLING)

        self.world["bounding_box"]["left" if left_wall else "right"][f"{turtle_position},{turtle.y}"] = int(dist/8)



    def check_bounding_wall(self, is_left_wall: bool, x: int, y: int) -> int:
        return self.world["bounding_box"]["left" if is_left_wall else "right"].get(f"{x},{y}", -1)



    #######################################
    ########## BOILERPLATE CODE ###########
    #######################################


    # returns the block at the given x y z coordinates
    def get_block(self, x: int, y: int, z: int) -> str:
        try:
            return self.world_data[f"{x},{y},{z}"]
        except KeyError:
            print("[ERROR] Requested world block does not exist yet.")
            return "unknown"

    # sets the block's value at the given x y z coordinates
    def set_block(self, x: int, y: int, z: int, value: str):
        try:
            self.world_data[f"{x},{y},{z}"] = value
        except KeyError:
            print("[ERROR] World block does not exist yet.")

    def gen_world(self, turtle: 'Turtle'):
        # loads new unknown block values in where the turtle could potentially detect and assign block values
        self.world_data[f"{turtle.x},{turtle.y},{turtle.z}"] = self.world_data.get(
            f"{turtle.x},{turtle.y},{turtle.z}", "computercraft:turtle_normal"
        )

        self.world_data[f"{turtle.x},{turtle.y + 1},{turtle.z}"] = self.world_data.get(
            f"{turtle.x},{turtle.y + 1},{turtle.z}", "unknown"
        )
        self.world_data[f"{turtle.x},{turtle.y - 1},{turtle.z}"] = self.world_data.get(
            f"{turtle.x},{turtle.y - 1},{turtle.z}", "unknown"
        )

        self.world_data[f"{turtle.x + turtle.x_offset},{turtle.y},{turtle.z + turtle.z_offset}"] = self.world_data.get(
            f"{turtle.x + turtle.x_offset},{turtle.y},{turtle.z + turtle.z_offset}", "unknown"
        )

    # adds a turtle to the array
    def add_turtle(self, turtle: 'Turtle'):
        self.turtles.append(turtle)

    # returns the array of turtles
    def get_turtles(self) -> list['Turtle']:
        return self.turtles

    # returns the world
    def get_world(self) -> dict:
        return self.world

    # returns a turtle with the given id
    def find_turtle(self, id: int) -> 'Turtle':
        # loops through the list of turtles
        for turtle in self.turtles:
            # returns the turtle that matches the id
            if turtle.gameID == id:
                return turtle

        return None  # type: ignore

    # sets the websocket class to the turtle at the given id
    def set_websocket(self, websocket: ServerConnection, id: int) -> 'Turtle | None':
        for i in range(0, len(self.turtles)):
            if self.turtles[i].gameID == id:
                self.turtles[i].websocket = websocket
                return self.turtles[i]

        return None  # type: ignore

    # returns the starting coords
    def get_start_coords(self) -> list[int]:
        return self.starting_coords

    # sets the starting coordinates for the master turtle
    def set_start_coords(self, coords: list[int]):
        self.starting_coords = coords



    # sets the world, this should only be used in construction.
    def set_world(self, world: dict):
        self.world = world

        # generate virtual areas if the world is empty
        if world == {}:

            # finds the bounds on the axis 
            def find_box_range() -> list[int]:
                    
                    arr_index = -1
                    match self.box_direction.upper():
                        case "X":
                            arr_index = 2
                        case "Z":
                            arr_index = 0
                        case _:
                            print(f"[ERROR] invalid bounding box direction: {self.box_direction}\nQuitting...")
                            quit()

                    return [self.starting_coords[arr_index] - 5, self.starting_coords[arr_index] + 5]

                            
            # initialize the bounding box
            self.world["bounding_box"] = {
                "infinite_dimension": self.box_direction,
                "box_range": find_box_range(),
                "tunnel_sites": {
                    "left": {},
                    "right": {}
                }
            }

            # the block that resources will be deposited in
            self.world["deposit_block"] = self.starting_coords
            self.world["deposit_block"][1] += 1

            # creates an empty world
            self.world["world_data"] = {}


        self.world_data = self.world["world_data"]




