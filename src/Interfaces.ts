export interface InvSlot {
    itemAmmount: number
    itemName: string
}


export interface TurtleInv {
    invSlot1: InvSlot
    invSlot2: InvSlot
    invSlot3: InvSlot
    invSlot4: InvSlot
    invSlot5: InvSlot
    invSlot6: InvSlot
    invSlot7: InvSlot
    invSlot8: InvSlot
    invSlot9: InvSlot
    invSlot10: InvSlot
    invSlot11: InvSlot
    invSlot12: InvSlot
    invSlot13: InvSlot
    invSlot14: InvSlot
    invSlot15: InvSlot
    invSlot16: InvSlot
}

export interface TurtleData {
    name: string
    inventory: TurtleInv
}