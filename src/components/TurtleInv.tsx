import * as React from "react";
import Turtle from '../UI'
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
          <Item>1</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>2</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>3</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>4</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>5</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>6</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>7</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>8</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>9</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>10</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>11</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>12</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>13</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>14</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>15</Item>
        </Grid>
        <Grid item style={itemStyle}>
          <Item>16</Item>
        </Grid>
      </Grid>

    </div>
    );
  }
}