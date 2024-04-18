import json
import os

file = os.path.join(os.path.dirname(__file__), "json_dump.json")

def dump_turtles(turtles):
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

    with open(file, "w") as turtle_dump:
        json.dump(turtle_json, turtle_dump, indent=4)
        turtle_dump.close()

def restore_turtles():
    turtle_json = {}
    if os.path.exists(file):
        with open(file, "r") as json_file:
            turtle_json = json.load(json_file)
            json_file.close()

    return turtle_json

