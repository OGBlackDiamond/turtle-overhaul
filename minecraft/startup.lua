VERSION = "0.1"

-- connect to the server
ws, err = http.websocket("ws://rx-78-2:3000")

-- create trust message
TRUST_MESSAGE = "Shake my hand bro"

-- create disconnect message
DISCONNECT_MESSAGE = "END-OF-LINE"

-- disconnects the client from the server
function disconnect()
    ws.send(DISCONNECT_MESSAGE)
    ws.close()
end

-- sets the name of the turtle
function set_name(type, pyramid_pos, underling_count)
    os.setComputerLabel(string.format("%s.%s-%s-%s", type, pyramid_pos, underling_count, VERSION))
end

-- spawn and boot up another turtle
function clone()
    shell.run("rm", "/disk/startup.lua")
    shell.run("wget", "https://raw.githubusercontent.com/OGBlackDiamond/turtle-overhaul/main/minecraft/startup.lua", "/disk/startup.lua")
end

-- checks if the connection failed
if err then
    print("Failed to connect to the websocket. Power me off and try again.")
else

    -- sends the secondary handshake
    ws.send(TRUST_MESSAGE)
    -- print the status of the handshake
    pcall(loadstring(ws.receive()))

    -- sets the turtle type
    local type = ws.receive(5)
    -- sets the turtle pyramid position
    local pyd_pos = ws.receive(5)
    -- sets the underling count
    local ucount = ws.receive(5)
    -- set the turtle name
    pcall(set_name, type, pyd_pos, ucount)

    -- MAIN CODE
    while true do
        local msg = ws.receive(5)
        local command = 0
        if msg ~= nil then
            command = loadstring(msg)
            response = command()
        end
        ws.send(response)
    end
end