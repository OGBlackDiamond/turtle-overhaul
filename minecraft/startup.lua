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

function set_name(type, pyramid_pos, underling_count)
    os.setComputerLabel(string.format("%s.%s-%s-%s", type, pyramid_pos, underling_count, VERSION))
end

-- checks if the connection failed
if err then
    print("Failed to connect to the websocket. Power me off and try again.")
else


    -- sends the secondary handshake
    ws.send(TRUST_MESSAGE)
    ws.receive()
    local 1 = ws.receive(5)
    local 2 = ws.receive(5)
    local 3 = ws.receive(5)
    pcall(set_name, 1, 3, 3)

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