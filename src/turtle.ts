import WebSocket, { RawData } from "ws";


// where all of the fun things with the turtle will happen

export class Turtle {
    turtleData: any = {};
    ws: WebSocket;

    constructor(ws: WebSocket) {
        this.ws = ws;
    }

    // updates the current turtle data
    public updateData(data: any): void {
        this.turtleData = data;
    }

    // this function will eventually handle all of the logic for the turtle
    public  executeTurtleCommand(ws: WebSocket, command: RawData, isCommand: boolean) {
        // if the command is a single command, shoot it to the turtle
        if (isCommand) {
            // sends the data of the function to be run to the turtle
            ws.send(JSON.stringify({func:command}));
        } else {
            // this will handle more complex tasks that need multiple commands, such as starting the mining algorithm, etc.
            var instruction = command.toString();
        }
    }
}