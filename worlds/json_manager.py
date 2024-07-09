import json
import os

from server_control.turtle import Turtle


# interaction with data storage files happens through this class
class Json_Manager:

    directory: str
    world_file: str
    turtle_file: str

    # selects the given world on construction
    def __init__(self, world="world"):

        self.select_world(world)

    # loads the directory and files of the selected world
    def select_world(self, world: str):

        self.directory = os.path.join(os.path.dirname(__file__), f"{world}")

        self.world_file = os.path.join(self.directory, "world.json")

        self.turtle_file = os.path.join(self.directory, "turtle_data.json")

        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
            with open(self.turtle_file, "w") as f:
                f.write("{}")
                f.close()
            with open(self.world_file, "w") as f:
                f.write("{}")
                f.close()

    # returns the world from its json file as a dictionary
    def get_world(self) -> dict:
        with open(self.world_file, "r") as file:
            return json.loads(file.read())

    # writes a given dictionary to the world file
    def write_to_world(self, world: dict):
        with open(self.world_file, "w") as file:
            file.write(json.dumps(world, indent=4))

    # parses data from the turtles it's passed and stores them in json
    def save_turtle_data(self, turtles: list[Turtle]):
        turtle_json = {}

        # iderate over the turtles
        for turtle in turtles:

            # parse and store the needed data as a dictionary
            turtle_dir = f"turtle{turtle.gameID}"
            turtle_json[turtle_dir] = {}

            # defines a local directory in the json tree for easier typing
            local_dir = turtle_json[turtle_dir]

            # handles turtle and parent ids
            local_dir["turtleID"] = turtle.gameID
            local_dir["parentID"] = turtle.parentID

            # handles coordinates
            local_dir["coords"] = {}
            local_dir["coords"]["x"] = turtle.x
            local_dir["coords"]["y"] = turtle.y
            local_dir["coords"]["z"] = turtle.z

            # handles heading
            local_dir["heading"] = turtle.heading

            # handles type
            local_dir["type"] = turtle.type

            # handles pyramid position
            local_dir["pyd_pos"] = turtle.pyd_pos

            # handles underling count
            local_dir["ucount"] = turtle.ucount

            # handles io
            local_dir["io"] = {}
            local_dir["io"]["messages"] = turtle.messages
            local_dir["io"]["queue"] = turtle.queue

        # writes the dictionary to the turtle data file
        with open(self.turtle_file, "w") as file:
            file.write(json.dumps(turtle_json, indent=4))

    # pulls data from its json file
    def restore_turtles(self) -> dict:
        with open(self.turtle_file, "r") as file:
            return json.loads(file.read())
