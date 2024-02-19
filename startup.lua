-- connect to the server
ws, err = http.websocket("ws://rx-78-2.ogblackdiamond.dev:25565")

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

    ws.send("I AM HERE! CLICK ME!")

    -- MAIN CODE
    while true do
        print("cp1")
        local msg = ws.receive()
        print("cp2")
        if msg == nil then
            break
        end
        local command = loadstring(msg)
        print("cp3")
        command()
        print("cp4]")
    end
