-- defines software version
VERSION = 0.65

HOST = "ws://rx-78-2"

PORT = "3000"

-- defines data types used to identify how incoming data should be interpreted
TYPE_EXEC = "[e]"
TYPE_CLONE = "[c]"
TYPE_NAME = "[n]"

-- defines data types to send data expressions between languages
TRUE = "{T}"
FALSE = "{F}"

-- create trust message
TRUST_MESSAGE = "shake-my-hand-bro"

-- create disconnect message
DISCONNECT_MESSAGE = "END-OF-LINE"

VALUABLE_RESOURCES = {"minecraft:coal_ore", "minecraft:deepslate_coal_ore", 
                        "minecraft:iron_ore", "minecraft:deepslate_iron_ore",
                        "minecraft:gold_ore", "minecraft:deepslate_gold_ore",
                        "minecraft:redstone_ore", "minecraft:deepslate_redstone_ore",
                        "minecraft:diamond_ore", "minecraft:deepslate_diamond_ore",
                        "minecraft:lapis_ore", "minecraft:deepslate_lapis_ore"}

-- disconnects the client from the server
function disconnect()
    ws.send(DISCONNECT_MESSAGE)
    ws.close()
end

-- gets the index of an item
function getItemIndex(itemName)
	for slot = 1, 16, 1 do
		local item = turtle.getItemDetail(slot)
		if(item ~= nil) then
			if(item["name"] == itemName) then
				return slot
			end
		end
	end
end

-- returns two arrays, one with the names of each block, and one with the count
function getInventory()
    local names = {}
    local counts = {}

    for slot = 1, 16, 1 do
        local item = turtle.getItemDetail(slot)
        if (item ~= nil) then
            names[slot] = item["name"]
            counts[slot] = item["count"]
        else
            names[slot] = nil
            counts[slot] = -1
        end
    end

    return names, counts
end

-- returns the name of the block in the inspected direction, nil if there is no block
function inspectBlock(direction)
    local direction = direction or ""
    command = loadstring(string.format("return turtle.inspect%s()", direction))
    local stat, name = command()
    return name["name"]
end

-- sets the name of the turtle
function setName(name_data)
    -- set the turtle name
    os.setComputerLabel(string.format("%s-%.2f", name_data, VERSION))
end

-- spawn and boot up another turtle
function clone()
    -- places the disk drive
    turtle.select(getItemIndex("computercraft:disk_drive"))
    turtle.dig()
    local step1 = turtle.place()

    -- inserts the disk
    turtle.select(getItemIndex("computercraft:disk"))
    local step2 = turtle.drop()

    os.sleep(1)

    -- updates the boot file
    shell.run("rm", "disk/startup.lua")
    local step3 = shell.run("wget", "https://raw.githubusercontent.com/OGBlackDiamond/turtle-overhaul/main/minecraft/startup.lua", "disk/startup.lua")

    -- updates turtle
    shell.run("cp", "disk/startup.lua", "startup.lua")

    -- moves the turtle up
    turtle.digUp()
    local step4 = turtle.up()

    -- places the new turtle
    turtle.select(getItemIndex("computercraft:turtle_normal"))
    turtle.dig()
    local step5 = turtle.place()

    -- get give the new turtle some coal
    turtle.select(1)
    turtle.drop(math.floor(turtle.getItemCount() / 2))

    -- turns it on
    peripheral.call("front", "turnOn")

    -- waits for clone turtle to identify its parent
    os.sleep(5)

    -- move the turtle back down
    turtle.down()

    -- take my disk drive back
    turtle.suck()
    turtle.dig()

    if step1 and step2 and step3 and step4 and step5 then
        return TRUE
    else
        return FALSE
    end
end

-- will mine for any valuable resources when moving
function mineValuables() 
    local up = inspectBlock("Up")
    local forward = inspectBlock()
    local down = inspectBlock("Down")

    -- mine up
    for index, value in ipairs(VALUABLE_RESOURCES) do
        if value == up then
            turtle.select(getItemIndex(up))
            turtle.digUp()
        end
    end

    -- mine forward
    for index, value in ipairs(VALUABLE_RESOURCES) do
        if value == forward then
            turtle.select(getItemIndex(forward))
            turtle.dig()
        end
    end

    -- mine down
    for index, value in ipairs(VALUABLE_RESOURCES) do
        if value == down then
            turtle.select(getItemIndex(down))
            turtle.digDown()
        end
    end
end


--[[
    The main function of the websocket
    This is in a method because it will be called after the parent data has been aquired from its maker
--]]
function websocketStart(turtleID, parentID)
    -- connect to the server
    repeat
        print("attempting websocket connection")
        sleep(2)
        ws, err = http.websocket(HOST .. ":" .. PORT)
    until ws ~= false


    -- sends the secondary handshake
    ws.send(TRUST_MESSAGE)
    -- print the status of the handshake
    shake_status = ws.receive()
    pcall(loadstring(shake_status))

    -- sends the ingame IDs of the two turtles
    ws.send(turtleID)
    ws.send(parentID)

    -- MAIN CODE
    while true do

        -- gets a message from the server and setds a defualt response value
        local data = ws.receive(5)

        -- won't do anything if the recv times out
        if data ~= nil then
            -- parses the data for its type and content
            local data_type = string.sub(data, 1, 3)
            data_content = string.sub(data, 4)

            -- performs the appropriate action based on data type

            -- executes the command in data_content
            if data_type == TYPE_EXEC then
                command = loadstring(data_content)
                status, return_data = command()

            -- performs a clone
            elseif data == TYPE_CLONE then
                status = clone()

            -- sets the name to data_content
            elseif data_type == TYPE_NAME then
                setName(data_content)

            -- the message recieved did not have a recognizable type
            else
                print("Unrecognized data formatting")
            end

        end

        -- send the response of the command into something the server can read
        if status == true or status == 1 then
            res_status = TRUE
        elseif status == false or status == 0 then
            res_status = FALSE
        end

        mineValuables()

        -- gets the names and counts of the inveneto
        local inv_names, inv_counts = getInventory()

        -- compiles the static data being sent to the server in a payload
        local payload = string.format([[
            {
                "return": {
                    "status": "%s",
                    "data": "%s",
                    "command": "%s"
                },
                "fuel": %d,
                "up": "%s",
                "front": "%s",
                "down": "%s",
                "inventory": {]],
            res_status,
            return_data,
            data_content,
            turtle.getFuelLevel(),
            inspectBlock("Up"),
            inspectBlock(),
            inspectBlock("Down")
        )

        -- appends each inventory slot to the json package
        for i = 1, 16, 1 do
            payload = payload .. string.format('\n\t\t"slot%d": {"name": "%s", "count": %d}', i, inv_names[i], inv_counts[i]) .. (i ~= 16 and "," or "\n\t}") 
        end
        payload = payload .. "\n}"

        -- sends the string-like json to the server
        ws.send(payload)
    end
end

-- gets the turtles' id and label
turtleID = os.getComputerID()
turtle_name = os.getComputerLabel()

--[[
    if the turtle name has not been set, it has never connected to the websocket.
    it should check behind it for the turtle that spawned it and get it's ID.
--]]
if turtle_name == nil then
    -- gets the parent id from behind the turtle
    parentID = peripheral.call("back", "getID")
    -- copies data to turtle
    shell.run("cp", "disk/startup.lua", "/startup.lua")
else 
    -- if the name is set, we know it has connected, and it will be reconnected
    parentID = -1
end

-- start the websocket
websocketStart(turtleID, parentID)