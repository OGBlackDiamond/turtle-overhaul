# import json
# import time

world = {
    1: {
        2: {
            3: "wef"
        }
    }
}

# world[1][3] = world[1].get(3,{2: "unknown"})
world[1][2][4] = world[1][2].get(4, "unknown")

print(world)
# time.sleep(1)
# print("balls")

# with open("test.json", "w") as file:
#     json.dump(world, file)
#     file.close()
    
# with open("test.json", "r") as file:
#     e = json.load(file)
#     print(e[f"{-1}"])
