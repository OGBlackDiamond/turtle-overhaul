VERSION = 0.1

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
function set_name(name_data)
    -- set the turtle name
    os.setComputerLabel(string.format("%s-%d", name_data, VERSION))
end

-- spawn and boot up another turtle
function clone()
    shell.run("rm", "/disk/startup.lua")
    shell.run("wget", "https://raw.githubusercontent.com/OGBlackDiamond/turtle-overhaul/main/minecraft/startup.lua", "/disk/startup.lua")
    shell.run("cp", "/disk/startup.lua", "/startup.lua")
end

-- checks if the connection failed
if err then
    print("Failed to connect to the websocket. Power me off and try again.")
else

    -- sends the secondary handshake
    ws.send(TRUST_MESSAGE)
    -- print the status of the handshake
    shake_status = ws.receive()
    pcall(loadstring(shake_status))

    -- sets the turtle type
    local name_data = ws.receive()
    set_name(name_data)


    -- MAIN CODE
    while true do
        local msg = ws.receive(5)
        local response = nil
        if msg ~= nil then
            command = loadstring(msg)
            response = command()
        end
        ws.send(response)
    end
end