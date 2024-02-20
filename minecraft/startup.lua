-- connect to the server
ws, err = http.websocket("ws://rx-78-2.ogblackdiamond.dev:25565")

-- create trust message
TRUST_MESSAGE = "Shake my hand bro"

-- create disconnect message
DISCONNECT_MESSAGE = "END-OF-LINE"

-- disconnects the client from the server
function disconnect()
    ws.send(DISCONNECT_MESSAGE)
    ws.close()
end

if err then
    print(err)
else

    ws.send(TRUST_MESSAGE)

    -- MAIN CODE
    while true do
        local msg = ws.receive()
        if msg == nil then
            break
        end
        local command = loadstring(msg)
        command()
    end
