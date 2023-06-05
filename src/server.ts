import { RawData, Server } from 'ws';
//import { connect } from 'ngrok';
import { connect } from "node:net"
import { Turtle } from './turtle';

const wss = new Server({ port: 8080 });
let turtle: Turtle;

// this will run when a user connects to the server
wss.on('connection', function connection(ws) {
    console.log("Someone connected");
    // passes the websocket to a new turtle instance
    turtle = new Turtle(ws);

    // error handling
    ws.on('error', function error(err) {
        console.log(err);
    });

    // this will run when the server is messaged from the webpage with data about how the turtle should move
    ws.on('message', function message(msg) {
        // msg will be given externally via the webpage
        var data = msg.toString()
        /*
            Any message sent from the webpage will begin with 'return'
            We can use this attribute to differentiate between requests from the turtle, and that of the webpage
        */ 
        if (data.slice(0, 6) == "return") {
            // executes the command on the turtle
            turtle.executeTurtleCommand(ws, msg, false);
        } else {
            // updates the current turtle data
            getTurtleData(msg);
        }

    });
    //ws.send('test');
});

// asynchronously waits for a connection on the listening port
(async ()  => {
    const url = await connect(8080);
    console.log(url);
})();

// this function will get data from the turtle, and pass it into 
function getTurtleData(message: RawData) {
    let data: string = JSON.stringify(message);
    // passes the data to the turtle
    turtle.updateData(data);
    //return data;
}