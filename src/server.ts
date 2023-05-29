import WebSocket, { RawData, Server } from 'ws';
import { connect } from 'ngrok';
import { Turtle } from './turtle';

const wss = new Server({ port: 8080 });
let turtle: Turtle;
let turtleState: any = {};
let command: string;

wss.on('connection', function connection(ws) {
    console.log("Server online");
    turtle = new Turtle(ws);

    ws.on('error', function error(err) {
        console.log(err);
    });

    ws.on('message', function message(msg) {
        turtleState = getTurtleData(msg);
        // command will be given externally, it should be something like "return turtle.[valid turtle function]"
        executeTurtleCommand(ws, command);
        turtle.updateData(turtleState);
    });

    //ws.send('test');
});

(async ()  => {
    const url = await connect(8080);
    console.log(url);
})();

function executeTurtleCommand(ws: WebSocket, command: string) {
    // sends the data of the function to be run to the turtle
    ws.send(JSON.stringify({func:command}));
}

function getTurtleData(message: RawData) {
    let data: string = JSON.stringify(message);
    return data;
}