import json
import os

class Json_Manager:

    directory: str
    world_file: str
    turtle_file: str

    def __init__(self, world="world"):

        self.select_world(world)


    def select_world(self, world):

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



    def get_world(self):
        with open(self.world_file, "r") as file:
            return json.loads(file.read())


    def write_to_world(self, world):
        with open(self.world_file, "w") as file:
            file.write(json.dumps(world, indent=4))

    def dump_turtles(self, turtles):
        turtle_json = {}

        for turtle in turtles:

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

        with open(self.turtle_file, "w") as file:
            file.write(json.dumps(turtle_json, indent=4))

    def restore_turtles(self):
        with open(self.turtle_file, "r") as file:
            return json.loads(file.read())

