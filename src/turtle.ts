import WebSocket from "ws";


// where all of the fun things with the turtle will happen

export class Turtle {
    turtleData: any = {};

    constructor(ws: WebSocket) {
        ws;
    }

    public updateData(data: any): void {
        this.turtleData = data;
    }
}