import * as React from "react";
import Turtle from '../UI'
import Grid from '@mui/material/Grid';
import Item from "@mui/material/ListItem";
export default class TurtleInv extends React.Component<Turtle, {}> {
constructor (props: Turtle){
  super(props);
}



render() {

  return (  
    <div>
      <h1>Turtle Inventory</h1>
      <Grid>
        <Grid>
          <Item>xs=8</Item>
        </Grid>
        <Grid item xs={4}>
          <Item>xs=4</Item>
        </Grid>
        <Grid item xs={4}>
          <Item>xs=4</Item>
        </Grid>
        <Grid item xs={8}>
          <Item>xs=8</Item>
        </Grid>
      </Grid>
    </div>
    );
  }
}