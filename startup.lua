prompt = string.format("blackdiamond@%s", os.getComputerLabel())

-- Greets User
settings.set("motd.enable", false)
textutils.slowPrint("\t\t{<>}\n\tBlackDiamond OS\nDon't look at my code unles you are a 5head ;)\nShould I startup? (y/n)\n")

passcode = "BlackDiamond"
-- Computer Safety!
function password_check(password)
    local pass_choice = read("*")
    if (pass_choice == password) then
        textutils.slowPrint("Password Correct: Access Granted!")
        return true
    else
        textutils.slowPrint("Password Incorrect: Access Denied.\nStop trying to look under my\nhood you sly dog, you.")
    end
end


-- Executes startup commands when the user is ready
function startup_request()
    local choice = read()
    while(choice ~= nil)
    do
        if (choice == "y") then
            textutils.slowPrint("Enter Passcode: ")
            if(password_check(passcode) == true) then
                textutils.slowPrint("Starting Up!")
                choice = nil
                return true
            end
        elseif (choice == "n") then
            textutils.slowPrint("Idling...\nEnter 'y' to start\nEnter 's' to shutdown")
            choice = read()
        elseif (choice == "s") then
            textutils.slowPrint("Goodbye :)                 ")
            os.shutdown()
            return false
        else
            textutils.slowPrint("Not an option!")
            choice = read()
        end
    end
end



-- Allows user to tell the turtle to do specific things
function command_center()
    if (is_on)then
        textutils.slowPrint("What would you like me to do?\nType 'help' for a list of commands")
        local choice = read()
        while (choice ~= nil) do
            if (choice == "help") then
                textutils.slowPrint([[List of commands you can use to interface with me:
    exit: Interface with the turtle like normal.
    mine: Use with mining turtle, mines for items of value.
    adjust: Adjusts the turtle to be fit to mine in a new spot
        adjust options: up, down, left, right. Intended for mining turtles.
    guard: Attacks any nearby enemies. Intended for melee turtles.
    change password: Temporarily changes your password.
    help: Lists all of the commands available to you.
    shutdown: Shuts down the Turtle.]])
                textutils.slowPrint("What would you like me to do?")
                choice = read()

            -- Section where Mining is used
            elseif (choice == "mine") then
                textutils.slowPrint("Starting the mining algorithm!\nThis is the fun part!!")
                choice = nil
                textutils.slowPrint("Place a chest in my bottom right inventory slot, and at least 15 coal in the 1st slot")
                while (turtle.getItemDetail(16) ~= "minecraft:chest" or turtle.getItemDetail(1) ~= ("minecraft:coal" or "minecraft:coal_block")) do
                    textutils.slowPrint("Waiting...                        ")
                end
                textutils.slowPrint("Would you like to mine manually, or autonomusly?")
                local mode_choice = read()
                if (mode_choice == "manual") then
                    mine_algo("manual")
                elseif (mode_choice == "auto") then
                    auto_done = false
                    while (auto_done == false) do
                        mine_algo("auto")
                        turtle.select(2)
                        turtle.digDown()
                        while (turtle.suckDown()) do end
                        turtle.digUp()
                        turtle.up()
                        turtle.digUp()
                        turtle.up()
                        turtle.turnLeft()
                        turtle.turnLeft()
                        for i = 2, 16 do
                            turtle.select(i)
                            local data = turtle.getItemDetail() 
                            if (data.name == "minecraft:chest") then
                                turtle.select(i)
                                turtle.transferTo(16, 1)
                            end
                        end
                    end
                else
                    textutils.slowPrint("Command not valid!\nOptions are 'manual' and 'auto'.")
                end
            -- Section end


            -- Adjust Section
            elseif (choice == "adjust") then
                turtle.select(2)
                turtle.digDown()
                while (turtle.suckDown()) do end
                textutils.slowPrint("Where should I adjust?")
                local adj_choice = read()
                if (adj_choice == "down") then
                    turtle.digDown()
                    turtle.down()
                    turtle.digDown()
                    turtle.down()
                    turtle.turnLeft()
                    turtle.turnLeft()
                elseif (adj_choice == "left") then
                    turtle.turnRight()
                    turtle.dig()
                    turtle.forward()
                    turtle.dig()
                    turtle.forward()
                    turtle.turnRight()
                elseif (adj_choice == "right") then
                    turtle.turnLeft()
                    turtle.dig()
                    turtle.forward()
                    turtle.dig()
                    turtle.forward()
                    turtle.turnLeft()
                elseif (adj_choice == "up") then
                    turtle.digUp()
                    turtle.up()
                    turtle.digUp()
                    turtle.up()
                    turtle.turnLeft()
                    turtle.turnLeft()
                elseif (adj_choice == "done") then
                    for i = 2, 16 do
                        turtle.select(i)
                        local data = turtle.getItemDetail() 
                        if (data.name == "minecraft:chest") then
                            turtle.select(i)
                            turtle.transferTo(16, 1)
                            command_center()    
                        end
                    end
                    choice = nil
                end
                -- Section End

            elseif (choice == "guard") then
                while true do
                    for i = 0, 4 do 
                    turtle.attack()
                    turtle.attackUp()
                    turtle.attackDown()
                    turtle.turnLeft()
                    end
                end
            elseif (choice == "change password") then
                password_change()
                choice = nil
            elseif (choice == "shutdown") then
                textutils.slowPrint("Shutting Down... Bye!        ")
                os.shutdown()
            elseif (choice == "exit") then
                textutils.slowPrint("Bringing you the the default turtle interface!\nBye!      ")
                choice = nil
            else
                textutils.slowPrint("Sorry, I don't know that command :/")
                choice = read()
            end
        end
    end
end











--[[
    Start of the many functions used 
    to make the mining algorithm possible
--]]

--The 'fun part'
function mine_algo(mode)
    local text = ""
    local finished = false
    is_mining = true
    textutils.slowPrint("\n\n\n\n\n\nDon't screw with me, I'm mining!\nIf you take any items, I will detect it, and you will be punished!\nStep in front of me to interact with me!.")
    turtle.digDown()
    turtle.select(16)
    turtle.placeDown()
    for i = 2, 16 do
        turtle.select(i)
        turtle.dropDown()
    end
    turtle.select(2)
    while is_mining do
        mine_forward(mode)
        check_refuel()
        
        for i = 2, 16 do
            if (turtle.getItemCount(i) == 64 and finished == false) then
                turtle.turnLeft()
                turtle.turnLeft()
                finished = true
            end
        end


       -- Stops the loop if player steps in front of the turtle
        if (turtle.attack()) then
            textutils.slowPrint("Enter Password: ")
            if (password_check(passcode)) then
                is_mining = false
                command_center()
            else
                textutils.slowPrint("Mining will resume.")
            end
        end
    end
end

--[[
    The main body of the mining algorithem
    Puts all of the functions together to 
    make a functional set of instructions
--]]
function mine_forward(mode)
    auto_done = false
    turtle.dig()
    turtle.forward()
    local block_list, block_pos = detect_blocks()
    for i = 0, #block_list do
        if (block_list[i] == "minecraft:chest") then
            for j = 2, 16 do
                turtle.select(j)
                if (turtle.dropDown() == true) then
                    auto_done = true
                end
            end
            is_mining = false
            if (mode ~= "auto") then
                command_center()
            end
        else
            mine_with_inv_management(block_list[i], block_pos[i])
        end
    end

end

-- Makes sure that coal is in slot 1 when mining
function mine_with_inv_management(item, direction)
    if (item == "minecraft:coal_ore") then
        turtle.select(1)
    else
        turtle.select(2)
    end

    if (direction == "forward") then
        turtle.dig()
    elseif (direction == "left") then
        turtle.turnLeft()
        turtle.dig()
        turtle.turnRight()
    elseif (direction == "right") then
        turtle.turnRight()
        turtle.dig()
        turtle.turnLeft()
    elseif (direction == "up") then
        turtle.digUp()
    elseif (direction == "down") then
        turtle.digDown()
    end
end

-- Stores all block values into a list
function detect_blocks()
    local blocks = {}
    local pos = {}
    local more_vein = true
    while (more_vein) do
        more_vein = false
        if (turtle.detect() or turtle.detectDown() or turtle.detectUp()) then
            if (test_value() ~= nil) then
                table.insert(blocks, test_value())
                table.insert(pos, "forward")
            end
            turtle.turnLeft()
            if (test_value() ~= nil) then
                table.insert(blocks, test_value())
                table.insert(pos, "left")
            end
            turtle.turnRight()
            turtle.turnRight()
            if (test_value() ~= nil) then
                table.insert(blocks, test_value())
                table.insert(pos, "right")
            end
            turtle.turnLeft()
            if (test_value("up") ~= nil) then
                table.insert(blocks, test_value("up"))
                table.insert(pos, "up")
            end
            if (test_value("down") ~= nil) then
                table.insert(blocks, test_value("down"))
                table.insert(pos, "down")
            end
        end
        return blocks, pos
    end
end

-- Tests the detected block for its value
function test_value(direction, mode)
    mode = mode or "normal"
    local value_blocks = {"minecraft:diamond_ore", "minecraft:iron_ore", "minecraft:redstone_ore", "minecraft:coal_ore", "minecraft:gold_ore", "minecraft:emerald_ore", "minecraft:deepslate_diamond_ore", "minecraft:deepslate_iron_ore", "minecraft:deepslate_redstone_ore", "minecraft:deepslate_coal_ore", "minecraft:deepslate_gold_ore", "minecraft:deepslate_emerald_ore", "minecraft:chest"}
    if (mode == "normal") then
        direction = direction or "forward"
        if (direction == "up") then
            is_block, data = turtle.inspectUp()
        elseif (direction == "forward") then
            is_block, data = turtle.inspect()
        elseif (direction == "down") then
            is_block, data = turtle.inspectDown()
        end

        if (is_block) then
            for i = 0, #value_blocks do
                if (value_blocks[i] == data.name) then 
                    return data.name
                end
            end
        end
    elseif (mode == "values") then
        return value_blocks
    end
end

--[[
    End of mining algorithm section
--]]





-- Misc Functions

-- Refuels the turtle if needed
function check_refuel()
    if (turtle.getFuelLevel() <= 500) then
        turtle.select(1)
        turtle.refuel()
        turtle.select(2)
    end
end


-- Allows the user to change their password
function password_change()
    textutils.slowPrint("Input numerical code to change your password\nNOTE: Only works as long as turtle is placed! If turtle is broken or turned off, password will reset.")
    if (password_check("12345")) then
        textutils.slowPrint("Input your new password! Your old password was " .. passcode)
        passcode = read()
        textutils.slowPrint("Done! Your new password is " .. passcode)
        command_center()
    end
end





-- Initial function calls
is_on = startup_request()
command_center()