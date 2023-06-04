import WebSocket, { RawData } from "ws";
import { InvSlot } from "./Interfaces";
import { TurtleInv } from "./Interfaces";
import { TurtleData } from "./Interfaces";

const firstNames: string[] = [
    "Asher",
    "Zephyr",
    "Orion",
    "Axel",
    "Phoenix",
    "Maddox",
    "Kingston",
    "Jaxon",
    "Ryder",
    "Beckett",
    "Aurora",
    "Luna",
    "Nova",
    "Everly",
    "Seraphina",
    "Harper",
    "Willow",
    "Aria",
    "Quinn",
    "Freya",
]

// where all of the fun things with the turtle will happen
export class Turtle {

    private name: string;
    private turtleData: TurtleData;
    private ws: WebSocket;

    constructor(ws: WebSocket) {
        this.ws = ws;
        this.name = firstNames[Math.random() * firstNames.length];
        // initialize the interface for the turtles's inventory
        this.turtleData = {
            name: this.name,
            inventory: {
                invSlot1: {
                    itemAmmount: 0,
                    itemName: ""
                },
                invSlot3: {
                    itemAmmount: 0,
                    itemName: ""
                },
                invSlot2: {
                    itemAmmount: 0,
                    itemName: ""
                },
                invSlot4: {
                    itemAmmount: 0,
                    itemName: ""
                },
                invSlot5: {
                    itemAmmount: 0,
                    itemName: ""
                },
                invSlot6: {
                    itemAmmount: 0,
                    itemName: ""
                },
                invSlot7: {
                    itemAmmount: 0,
                    itemName: ""
                },
                invSlot8: {
                    itemAmmount: 0,
                    itemName: ""
                },
                invSlot9: {
                    itemAmmount: 0,
                    itemName: ""
                },
                invSlot10: {
                    itemAmmount: 0,
                    itemName: ""
                },
                invSlot11: {
                    itemAmmount: 0,
                    itemName: ""
                },
                invSlot12: {
                    itemAmmount: 0,
                    itemName: ""
                },
                invSlot13: {
                    itemAmmount: 0,
                    itemName: ""
                },
                invSlot14: {
                    itemAmmount: 0,
                    itemName: ""
                },
                invSlot15: {
                    itemAmmount: 0,
                    itemName: ""
                },
                invSlot16: {
                    itemAmmount: 0,
                    itemName: ""
                }
            }
        }
    }

    // updates the current turtle data
    public updateData(data: any): void {
        this.turtleData = data;
    }

    public sendCommand(ws: WebSocket, command: RawData): void {

    }

    // this function will eventually handle all of the logic for the turtle
    private executeTurtleCommand(command: RawData, isCommand: boolean): void {
        // if the command is a single command, shoot it to the turtle
        if (isCommand) {
            // sends the data of the function to be run to the turtle
            this.ws.send(JSON.stringify({func:command}));
        } else {
            // this will handle more complex tasks that need multiple commands, such as starting the mining algorithm, etc.
            var instruction = command.toString();
        }
    }

    private scanInventory(): void {
        

    }
}