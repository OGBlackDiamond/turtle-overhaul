import { RawData, Server } from 'ws';
import { connect } from 'ngrok';
import { Turtle } from './turtle';

const wss = new Server({ port: 8080 });
let turtles: Turtle[];
let turtleCount: number = 0;
let selectedTurtle: Turtle;

// this will run when a user connects to the server
wss.on('connection', function connection(ws) {
    console.log("Someone connected");
    // passes the websocket to a new turtle instance
    turtles[turtleCount] = new Turtle(ws);
    turtleCount++;
    // will automatically select the first turtle if no other ones exist
    if (turtles[1] == null) {
        selectedTurtle = turtles[0];
    }

    // error handling
    ws.on('error', function error(err) {
        console.log(err);
    });

    // this will run when the server is messaged from the webpage with data about how the turtle should move
    ws.on('message', function message(msg) {
        // msg will be given externally via the webpage
        var data: string = msg.toString();
        // any data sent to the server will have a prefix to identify where it is coming from 
        if (data.slice(0, 1) == 'c') {
            // executes the command on the turtle
            selectedTurtle.sendCommand(ws, msg);
        } else if (data.slice(0, 1) == 'd') {
            // updates the current turtle data
            getTurtleData(msg);
        } else {
            ws.send("Message ${data} is not formatted correctly!\nIt will not be sent or recieved.");
            console.log("Message ${data} is not formatted correctly!\nIt will not be sent or recieved.");
        }
    });
    //ws.send('test');
});

// asynchronously waits for a connection on the listening port
(async ()  => {
    const url: string = await connect(8080);
    console.log(url);
})();

// this function will get data from the turtle, and pass it into 
function getTurtleData(message: RawData) {
    let data: string = JSON.stringify(message);
    // passes the data to the turtle
    selectedTurtle.updateData(data);
}