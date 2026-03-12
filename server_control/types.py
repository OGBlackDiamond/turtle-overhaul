from enum import IntEnum

class Instruction_Status(IntEnum):
    IDLE = 0
    GOTO = 1
    MANUAL = 2
    STARTUP_CHORES = 3
    TUNNLING = 4

class Task_Status(IntEnum):
    IDLE = 0
    MINE = 1
    REFUEL = 2
    DEPOSIT = 3
    MINE_FUEL = 4
    MINE_RESOURCES = 5
    SMELT = 6
    CRAFT = 7
    REPRODUCE = 8

class Heading(IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
   

