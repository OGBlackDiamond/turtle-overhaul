local uname = "blackdiamond"
-- defines a prompt that can be used if we want
Prompt = string.format("%s@%s>", uname, os.getComputerLabel())

-- gets the json library
json = require("json")

-- table to store the turtle's current data
local turtle_state = {}
local turtleInv = {
    inv_slot2 = {
        item_ammount = 0,
        item_name = ""
    },
    inv_slot1 = {
        item_ammount = 0,
        item_name = ""
    },
    inv_slot3 = {
        item_ammount = 0,
        item_name = ""
    },
    inv_slot4 = {
        item_ammount = 0,
        item_name = ""
    },
    inv_slot5 = {
        item_ammount = 0,
        item_name = ""
    },
    inv_slot6 = {
        item_ammount = 0,
        item_name = ""
    },
    inv_slot7 = {
        item_ammount = 0,
        item_name = ""
    },
    inv_slot8 = {
        item_ammount = 0,
        item_name = ""
    },
    inv_slot9 = {
        item_ammount = 0,
        item_name = ""
    },
    inv_slot10 = {
        item_ammount = 0,
        item_name = ""
    },
    inv_slot11 = {
        item_ammount = 0,
        item_name = ""
    },
    inv_slot12 = {
        item_ammount = 0,
        item_name = ""
    },
    inv_slot13 = {
        item_ammount = 0,
        item_name = ""
    },
    inv_slot14 = {
        item_ammount = 0,
        item_name = ""
    },
    inv_slot15 = {
        item_ammount = 0,
        item_name = ""
    },
    inv_slot16 = {
        item_ammount = 0,
        item_name = ""
    }
}

-- individual turtle data values to be set
local direction_facing = "north"
local current_pos = {0, 0, 0}

-- settings for the turtle to enable on startup
settings.set("motd.enable", false)
textutils.slowPrint("\t\t{<>}\n\tBlackDiamond OS\n\n")
if (binary_question("Should I connect to daddy websocket?")) then
    while (not password_check()) do end
    local wss, err = http.websocket("ws://localhost:8080")
    -- prints an error if one exists
    if err then
      print(err)
    elseif wss then
        -- Always be getting data from the socket
        while true do
          -- this should accept a string like "return turtle.[valid turtle function]"
          local message = wss.receive()
          if message == nil then
            break
          end
            -- parses the message
            local obj = json.parse(message)
            local func = loadstring(obj["func"])
            -- calls the function
            func()
            -- sends the current turtle data
            wss.send(json.stringify(turtle_state))
        end
    end
else
  -- a dumb version of the computer interface can go here
  textutils.slowPrint("Entering Offline Mode!\nMy functionality is limited in this mode. you can always connect me to daddy websocket if needed!")
end


-- Function that will get a response (yes or no) from the user
function binary_question(text)
    local input
    repeat
        textutils.slowPrint(text .. prompt)
        input = read()
    until (input ~= "y" or input ~= "n")
    print("\n")
    return input == "y"
end

-- Function that will ask for a password to keep non-5heads out
function password_check(password)
    textutils.slowPrint("Enter the password:\n")
    local pass_choice = read("*")
    if (pass_choice == password) then
        textutils.slowPrint("Password Correct: Access Granted!")
        return true
    else
        textutils.slowPrint("Password Incorrect: Access Denied.\nStop trying to use me you 3head!")
        return false
    end
end

-- this will contain instructions for whatever needs to happen to gather data for the server
function compile_turtle_data()
    getInventory()
    turtle_state = {direction_facing, current_pos[0], current_pos[1], current_pos[2], turtleInv}
end

function getInventory()
    for i,v in ipairs(turtleInv) do
        local slot_data = turtle.getItemDetail(i)
        turtleInv[i].item_ammount = slot_data.count
        turtleInv[i].item_name = slot.name
    end
end