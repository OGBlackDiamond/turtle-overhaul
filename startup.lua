-- connect to the server
ws, err = http.websocket("ws://rx-78-2.ogblackdiamond.dev:25565")

-- create disconnect message
DISCONNECT_MESSAGE = "END-OF-LINE"

-- disconnects the client from the server
function disconnect()
    ws.send(DISCONNECT_MESSAGE)
    ws.close()
end

-- will endlessly try to connect to the server if it isn't already
while err do
    ws, err = http.websocket("ws://rx-78-2.ogblackdiamond.dev:25565")
end

ws.send("I AM HERE! CLICK ME!")

-- MAIN CODE
while true do
    local msg = ws.receive()
    if message == nil then
        break
    end

    msg()


