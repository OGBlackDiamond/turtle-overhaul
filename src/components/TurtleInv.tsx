import * as React from "react";
import Turtle from '../Interfaces'
import Grid from '@mui/material/Grid';
import Item from "@mui/material/ListItem";
import { UIStyle } from "../styles/UIStyle"
export default class TurtleInv extends React.Component<Turtle, {}> {
constructor (props: Turtle){
  super(props);
}

render() {
  let styles = new UIStyle();
  let gridStyle = styles.GridStyle;
  let itemStyle = styles.ItemStyle;
  return (  
    <div>
      <h1>Turtle Inventory</h1>
      <Grid container style={gridStyle} id="top row">
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot1}</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot2}</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot3}</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot4}</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot5}</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot6}</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot7}</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot8}</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot9}</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot10}</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot11}</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot12}</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot13}</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot14}</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot15}</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>{this.props.invSlot16}</Item>
        </Grid>
      </Grid>
    </div>
    );
  }
}