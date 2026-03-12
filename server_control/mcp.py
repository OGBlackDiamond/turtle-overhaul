from websockets.sync.server import ServerConnection
import random

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

    ore_levels: dict[str, int]
    y_band: int

    fuel_values: dict[str, int]
    emergency_refuel: bool
    low_fuel_level: int
    try_refuel_buffer: int
    refuel_ammount: int

    coal_buffer: int
    max_swarm_size: int
    inventory_full_threshold: int
    smelt_recipes: dict[str, str]
    reproduce_materials: dict[str, int]
    craft_materials: dict[str, int]
    resource_priority: list[str]

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
            #self.controller(turtle)
            print("loop finished")


    # decision tree for assigning a turtle's next task
    # priority order: REFUEL > DEPOSIT > MINE_FUEL > MINE_RESOURCES > SMELT > CRAFT > REPRODUCE > IDLE
    def decide_task(self, turtle: 'Turtle'):
        if not turtle.startup_chores_complete: return
        if not turtle.task == Types.Task_Status.IDLE: return

        print("deciding task")

        if self.should_refuel(turtle):
            turtle.task = Types.Task_Status.REFUEL

        elif self.should_deposit(turtle):
            turtle.task = Types.Task_Status.DEPOSIT

        elif self.should_mine_fuel(turtle):
            turtle.task = Types.Task_Status.MINE_FUEL

        elif self.should_mine_resources(turtle):
            turtle.task = Types.Task_Status.MINE_RESOURCES

        elif self.should_smelt(turtle):
            turtle.task = Types.Task_Status.SMELT

        elif self.should_craft(turtle):
            turtle.task = Types.Task_Status.CRAFT

        elif self.should_reproduce(turtle):
            turtle.task = Types.Task_Status.REPRODUCE


    ###########################################
    ##### DECISION TREE CONDITION CHECKS ######
    ###########################################

    # critically low fuel -- turtle must refuel immediately or it will be stranded
    def should_refuel(self, turtle: 'Turtle') -> bool:
        return turtle.fuel < self.low_fuel_level

    # inventory is nearly full -- need to go deposit before mining more
    def should_deposit(self, turtle: 'Turtle') -> bool:
        occupied_slots = 0
        if len(turtle.messages) > 0:
            for slot in turtle.messages[0]["inventory"].values():
                if slot["count"] > 0:
                    occupied_slots += 1
        return occupied_slots >= self.inventory_full_threshold

    # coal reserves in inventory are getting low -- proactively mine more
    def should_mine_fuel(self, turtle: 'Turtle') -> bool:
        coal = turtle.check_inv("minecraft:coal")
        return coal["count"] < self.coal_buffer

    # default productive activity -- always mine valuables if nothing else is needed
    def should_mine_resources(self, turtle: 'Turtle') -> bool:
        return True

    # turtle has raw ores that need smelting into ingots
    def should_smelt(self, turtle: 'Turtle') -> bool:
        for raw_ore in self.smelt_recipes:
            if turtle.check_inv(raw_ore)["count"] > 0:
                return True
        return False

    # master turtle has all materials to craft a new turtle (master only, crafty turtle)
    def should_craft(self, turtle: 'Turtle') -> bool:
        if turtle.type != "M":
            return False

        for item, needed in self.craft_materials.items():
            if turtle.check_inv(item)["count"] < needed:
                return False
        return True

    # mcp decides the swarm needs more turtles and the turtle has the items to clone
    def should_reproduce(self, turtle: 'Turtle') -> bool:
        if turtle.type != "M":
            return False

        if len(self.turtles) >= self.max_swarm_size:
            return False

        for item, needed in self.reproduce_materials.items():
            if turtle.check_inv(item)["count"] < needed:
                return False
        return True


    # picks the optimal Y-level to mine at based on what the turtle needs most
    # returns an int (Y-level from ore-y-levels config)
    def choose_mine_target(self, turtle: 'Turtle') -> int:

        # if master and swarm isn't full, mine what's most deficient for crafting
        if turtle.type == "M" and len(self.turtles) < self.max_swarm_size:
            worst_ore = ""
            worst_ratio = float("inf")

            for item, needed in self.craft_materials.items():
                # strip "minecraft:" prefix and "_ingot" suffix to get ore key
                ore_name = item.removeprefix("minecraft:").removesuffix("_ingot")

                # skip materials we can't mine (stone, glass_pane, chest, etc.)
                if ore_name not in self.ore_levels:
                    continue

                count = turtle.check_inv(item)["count"]
                ratio = count / needed
                if ratio < worst_ratio:
                    worst_ratio = ratio
                    worst_ore = ore_name

            if worst_ore:
                return self.ore_levels[worst_ore]

        # fallback: mine by value priority
        for ore_name in self.resource_priority:
            if ore_name in self.ore_levels:
                return self.ore_levels[ore_name]

        return self.ore_levels["diamond"]


    def decide_instructions(self, turtle: 'Turtle'):
        if not turtle.instruction == Types.Instruction_Status.IDLE: return

        print("deciding instruction")

        match (turtle.task):

            case(Types.Task_Status.IDLE):
                turtle.set_instruction(Types.Instruction_Status.IDLE)
                
            case(Types.Task_Status.MINE):

                match (turtle.prev_instruction): 

                    case(Types.Instruction_Status.GOTO):
                        self.tunnel(turtle)
                        print("done done done")

                    case(Types.Instruction_Status.TUNNLING):
                        # TODO: find a better way to follow the mining algo?

                        # finds a valid tunnling location
                        left_wall: bool = self.check_close_wall_left(turtle)
                        z_wall: bool = self.check_inf_dimension_z()

                        x_steps: int = 0
                        y_steps: int = 0

                        while (self.check_bounding_wall(
                                left_wall,
                                (turtle.z if z_wall else turtle.x) + x_steps,
                                turtle.y + y_steps)
                            ) == -1: 

                            
                            if (random.randint(0, 1)):
                                x_steps += -2
                                y_steps += 1
                            else:
                                x_steps += 1
                                y_steps += 2


                        turtle.set_destination(
                            turtle.x + (0 if z_wall else x_steps),
                            turtle.y + y_steps, 
                            turtle.z + (x_steps if z_wall else 0)
                        )
                        turtle.set_instruction(Types.Instruction_Status.GOTO)


            case(Types.Task_Status.REFUEL):
                # TODO: navigate to coal Y-level, mine coal, then self-refuel
                # once refueled, set task back to IDLE
                pass

            case(Types.Task_Status.DEPOSIT):
                # TODO: navigate to deposit block, drop off valuable items
                # reclaim inventory space, then set task back to IDLE
                pass

            case(Types.Task_Status.MINE_FUEL):
                # TODO: navigate to coal Y-level, tunnel specifically for coal
                # similar to MINE but targeted at fuel replenishment
                pass

            case(Types.Task_Status.MINE_RESOURCES):
                # TODO: pick best ore to mine based on inventory needs
                # navigate to its Y-level, tunnel and collect valuables
                pass

            case(Types.Task_Status.SMELT):
                # TODO: navigate to base furnace, insert raw ore and fuel
                # wait for smelting to complete, collect ingots
                # furnace interaction: drop from above for input, drop from side for fuel
                # suck from side/below for output
                pass

            case(Types.Task_Status.CRAFT):
                # TODO: master turtle arranges materials in crafting grid
                # craft computer first (7 stone, 1 redstone, 1 glass pane)
                # craft chest (8 planks)
                # craft turtle (7 iron, 1 computer, 1 chest)
                # requires crafty turtle peripheral
                pass

            case(Types.Task_Status.REPRODUCE):
                # TODO: trigger the clone sequence
                # turtle must have: crafted turtle item, disk drive, disk, coal
                # calls turtle.clone() which handles placement and boot
                pass

    def controller(self, turtle: 'Turtle'):
        if (turtle.fuel < self.low_fuel_level + self.try_refuel_buffer):
            turtle.refuel(self.refuel_ammount)


    def tunnel(self, turtle: 'Turtle'):

        print("tunnling")

        turtle_position = turtle.x if (self.world["bounding_box"]["infinite_dimension"] == "z") else turtle.z
        left_wall: bool = self.check_close_wall_left(turtle)

        heading: int = 0 if turtle.z == turtle_position else 1
        if not left_wall: heading += 2

        turtle.turn_to(heading)

        dist = turtle.fuel - len(turtle.line_3d(
            self.world["deposit_block"][0],
            self.world["deposit_block"][1],
            self.world["deposit_block"][2]
        )) - 10

        print("sending turt tunnel")
        turtle.tunnel(int(dist / 8))

        print("setting instruction")
        turtle.set_instruction(Types.Instruction_Status.TUNNLING)
        
        print("done")

        self.world["bounding_box"]["left" if left_wall else "right"][f"{turtle_position},{turtle.y}"] = int(dist/8)

        print("done done")


    def check_bounding_wall(self, is_left_wall: bool, x: int, y: int) -> int:
        return self.world["bounding_box"]["left" if is_left_wall else "right"].get(f"{x},{y}", -1)

    def check_inf_dimension_z(self) -> bool:
        return self.world["bounding_box"]["infinite_dimension"] == "z"

    def check_close_wall_left(self, turtle: 'Turtle') -> bool:
        turtle_position = turtle.x if (self.world["bounding_box"]["infinite_dimension"] == "z") else turtle.z
        return abs(turtle_position - self.world["bounding_box"]["box_range"][0]) < abs(turtle_position - self.world["bounding_box"]["box_range"][1])

    def check_mine_band(self, turtle: 'Turtle', ore:str) -> bool:
        return abs(turtle.destination[-1][1] - self.ore_levels[ore]) < self.y_band 



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


    def set_config(self, config: dict):

        self.ore_levels = config["ore-y-levels"]

        self.y_band = config["acceptable-drift"]

        self.fuel_values = config["fuel-values"]

        self.emergency_refuel = config["emergency-refueling"]

        self.low_fuel_level = config["low-fuel-level"]

        self.try_refuel_buffer = config["try-refuel-buffer"]

        self.refuel_ammount = config["refuel-ammount"]

        self.coal_buffer = config["coal-buffer"]

        self.max_swarm_size = config["max-swarm-size"]

        self.inventory_full_threshold = config["inventory-full-threshold"]

        self.smelt_recipes = config["smelt-recipes"]

        self.reproduce_materials = config["reproduce-materials"]

        self.craft_materials = config["craft-materials"]

        self.resource_priority = config["resource-priority"]


