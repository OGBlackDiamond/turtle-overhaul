prompt = string.format("blackdiamond@%s>", os.getComputerLabel())

settings.set("motd.enable", false)
textutils.slowPrint("\t\t{<>}\n\tBlackDiamond OS\n\n")
if (binary_question("Should I connect to daddy websocket?")) then
    local wss, err = http.websocket("ws://localhost:8080")
    -- prints an error if one exists
    if err then
        print(err)
    elseif wss then
        -- Always be getting data from the server
        while true do
            -- this should accept a string like "return turtle.[valid turtle function]"
            local message = wss.receive()
            if message == nil then
                break
            end
            local obj = json.decode(message)
            local func = loadstring(obj["func"])
            func()
        end
    end
else
    -- offline code goes here
end



-- Function that will get a response (yes or no) from the user
function binary_question(text, private)
    local input
    repeat
        textutils.slowPrint(text .. prompt)
        input = private and read(*) or read()
    until (input ~= "y" or input ~= "n") do
    print("\n")
    return input == y and true or false
end

-- Function that will ask for a password to keep 
function password_check(password)
    local pass_choice = read("*")
    if (pass_choice == password) then
        textutils.slowPrint("Password Correct: Access Granted!")
        return true
    else
        textutils.slowPrint("Password Incorrect: Access Denied.\nStop trying to ")
    end
end