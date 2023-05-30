// websocket variable
const ws = new WebSocket("ws://localhost:8080");

// moves thee turtle forward
function moveTurtleForward() {
    ws.send("return turtle.forward()");
}

// turns the turtle in the given direction, default is right
function turnTurtle(direction) {
    switch (direction) {
        case "left":
            ws.send("return turtle.turnLeft()");
        case "right":
            ws.send("return turtle.turnRight()");
        default:
            ws.send("return turtle.turnRight()")
    }
}