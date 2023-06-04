import * as React from "react";
import * as ReactDOM from "react-dom";
import TurtleInv from "./components/TurtleInv";
import selectedTurtle from "./server";

// renders the scene in control_pannel.html
ReactDOM.render(
    <div>
        <h1>Remote Control Turtle Interface</h1>
        <TurtleInv
         invSlot1={selectedTurtle.turtleData.inventory.invSlot1.itemAmmount}
         invSlot2={selectedTurtle.turtleData.inventory.invSlot2.itemAmmount}
         invSlot3={selectedTurtle.turtleData.inventory.invSlot3.itemAmmount}
         invSlot4={selectedTurtle.turtleData.inventory.invSlot4.itemAmmount}
         invSlot5={selectedTurtle.turtleData.inventory.invSlot5.itemAmmount}
         invSlot6={selectedTurtle.turtleData.inventory.invSlot6.itemAmmount}
         invSlot7={selectedTurtle.turtleData.inventory.invSlot7.itemAmmount}
         invSlot8={selectedTurtle.turtleData.inventory.invSlot8.itemAmmount}
         invSlot9={selectedTurtle.turtleData.inventory.invSlot9.itemAmmount}
         invSlot10={selectedTurtle.turtleData.inventory.invSlot10.itemAmmount}
         invSlot11={selectedTurtle.turtleData.inventory.invSlot11.itemAmmount}
         invSlot12={selectedTurtle.turtleData.inventory.invSlot12.itemAmmount}
         invSlot13={selectedTurtle.turtleData.inventory.invSlot13.itemAmmount}
         invSlot14={selectedTurtle.turtleData.inventory.invSlot14.itemAmmount}
         invSlot15={selectedTurtle.turtleData.inventory.invSlot15.itemAmmount}
         invSlot16={selectedTurtle.turtleData.inventory.invSlot16.itemAmmount}
        />
    </div>,
    document.getElementById("root")
);