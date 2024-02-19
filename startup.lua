ws, err = assert(http.websocket("ws://rx-78-2.ogblackdiamond.dev"))

DISCONNECT_MESSAGE = "END-OF-LINE"

function disconnect()
    ws.send(DISCONNECT_MESSAGE)
    ws.close()
end

if not err then
    ws.send("Hello!") -- Send a message
    print(ws.receive()) -- And receive the reply
    disconnect()