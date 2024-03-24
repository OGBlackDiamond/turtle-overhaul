-- defines software version
VERSION = 0.35

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

-- sets the name of the turtle
function set_name(name_data)
    -- set the turtle name
    os.setComputerLabel(string.format("%s-%.2f", name_data, VERSION))
end

-- spawn and boot up another turtle
function clone()
    if turtle.getFuelLevel() > 1 then
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

        turtle.select(1)
        turtle.drop(math.floor(turtle.getItemCount() / 2))

        -- turns it on
        peripheral.call("front", "turnOn")

        -- waits for clone turtle to identify its parent
        os.sleep(5)

        if step1 and step2 and step3 and step4 and step5 then
            return TRUE
        else
            return FALSE
        end
    end
    print("not enough fuel to clone")
    return FALSE
end



--[[
    The main function of the websocket
    This is in a method because it will be called after the parent data has been aquired from its maker
--]]
function websocket_start(turtleID, parentID)
    -- connect to the server
    repeat
        print("attempting websocket connection")
        ws, err = http.websocket("ws://rx-78-2:3000")
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

        local data = ws.receive(5)
        local response = nil

        -- won't do anything if the recv times out
        if data ~= nil then
            -- parses the data for its type and content
            local data_type = string.sub(data, 1, 3)
            local data_content = string.sub(data, 4)

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
                set_name(data_content)

            -- the message recieved did not have a recognizable type
            else
                print("Unrecognized data formatting")
            end

        end

        -- variable that will store the string type for the received message
        local res_status

        -- send the response of the command back to the server
        if status == true then
            res_stat = TRUE
        elseif status == false then
            res_stat = FALSE
        end

        ws.send(string.format("%s%s", res_stat, return_data))
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

websocket_start(turtleID, parentID)