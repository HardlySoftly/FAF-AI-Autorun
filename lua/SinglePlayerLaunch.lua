-- Logic and defaults for launching non-skirmish sessions
local Prefs = import('/lua/user/prefs.lua')
local MapUtils = import('/lua/ui/maputil.lua')
local aiTypes = import('/lua/ui/lobby/aitypes.lua').aitypes

function GetRandomName(faction, aiKey)
    WARN('GRN: ',faction)
    local aiNames = import('/lua/ui/lobby/ainames.lua').ainames
    local factions = import('/lua/factions.lua').Factions

    faction = faction or (math.random(table.getn(factions)))

    local name = aiNames[factions[faction].Key][math.random(table.getn(aiNames[factions[faction].Key]))]

    if aiKey then
        local aiName = "AI"
        for index, value in aiTypes do
            if aiKey == value.key then
                aiName = value.name
            end
        end
        name = name .. " (" .. LOC(aiName) .. ")"
    end

    return name
end

function GetRandomFaction()
    return math.random(table.getn(import('/lua/factions.lua').Factions))
end

function VerifyScenarioConfiguration(scenarioInfo)
    if scenarioInfo == nil then
        error("VerifyScenarioConfiguration - no scenarioInfo")
    end

    if scenarioInfo.Configurations == nil or scenarioInfo.Configurations.standard == nil or scenarioInfo.Configurations.standard.teams == nil then
        error("VerifyScenarioConfiguration - scenarios require the standard team configuration")
    end

    if scenarioInfo.Configurations.standard.teams[1].name ~= 'FFA' then
        error("VerifyScenarioConfiguration - scenarios require all teams be set up as FFA")
    end

    if scenarioInfo.Configurations.standard.teams[1].armies == nil then
        error("VerifyScenarioConfiguration - scenarios require at least one army")
    end
end



-- Note that the map name must include the full path, it won't try to guess the path based on name
function SetupCampaignSession(scenario, difficulty, inFaction, campaignFlowInfo, isTutorial)
    local factions = import('/lua/factions.lua').Factions
    local faction = inFaction or 1
    if not scenario then
        error("SetupCampaignSession - scenario required")
    end
    VerifyScenarioConfiguration(scenario)

    if not difficulty then
        error("SetupCampaignSession - difficulty required")
    end

    local sessionInfo = {}

    sessionInfo.playerName = Prefs.GetFromCurrentProfile('Name') or 'Player'
    sessionInfo.createReplay = false
    sessionInfo.scenarioInfo = scenario

    local armies = sessionInfo.scenarioInfo.Configurations.standard.teams[1].armies

    sessionInfo.teamInfo = {}

    for index, name in armies do
        sessionInfo.teamInfo[index] = import('/lua/ui/lobby/lobbyComm.lua').GetDefaultPlayerOptions(sessionInfo.playerName)
        if index == 1 then
            sessionInfo.teamInfo[index].PlayerName = sessionInfo.playerName
            sessionInfo.teamInfo[index].Faction = faction
        else
            sessionInfo.teamInfo[index].PlayerName = name
            sessionInfo.teamInfo[index].Human = false
            sessionInfo.teamInfo[index].Faction = 1
        end
        sessionInfo.teamInfo[index].ArmyName = name
    end

    sessionInfo.scenarioInfo.Options = {}
    sessionInfo.scenarioInfo.Options.FogOfWar = 'explored'
    sessionInfo.scenarioInfo.Options.Difficulty = difficulty
    sessionInfo.scenarioInfo.Options.DoNotShareUnitCap = true
    sessionInfo.scenarioInfo.Options.Timeouts = -1
    sessionInfo.scenarioInfo.Options.GameSpeed = 'normal'
    sessionInfo.scenarioInfo.Options.FACampaignFaction = factions[faction].Key
    -- Copy campaign flow information for the front end to use when ending the game
    -- or when restoring from a saved game
    if campaignFlowInfo then
        sessionInfo.scenarioInfo.campaignInfo = campaignFlowInfo
    end

    if isTutorial and (isTutorial == true) then
        sessionInfo.scenarioInfo.tutorial = true
    end

    Prefs.SetToCurrentProfile('LoadingFaction', faction)

    sessionInfo.scenarioMods = import('/lua/mods.lua').GetCampaignMods(sessionInfo.scenarioInfo)
    LOG('sessioninfo: ', repr(sessionInfo.teamInfo))
    return sessionInfo
end




function FixupMapName(mapName)
    if (not string.find(mapName, "/")) and (not string.find(mapName, "\\")) then
        mapName = "/maps/" .. mapName .. "/" .. mapName .. "_scenario.lua"
    end
    return mapName
end


local defaultOptions = {
    FogOfWar = 'explored',
    NoRushOption = 'Off',
    PrebuiltUnits = 'Off',
    Difficulty = 2,
    DoNotShareUnitCap = true,
    Timeouts = -1,
    GameSpeed = 'normal',
    UnitCap = '500',
    Victory = 'sandbox',
    CheatsEnabled = 'true',
    CivilianAlliance = 'enemy',
}

local function GetCommandLineOptions(isPerfTest)
    local options = table.copy(defaultOptions)

    if isPerfTest then
        options.FogOfWar = 'none'
    elseif HasCommandLineArg("/nofog") then
        options.FogOfWar = 'none'
    end

    local norush = GetCommandLineArg("/norush", 1)
    if norush then
        options.NoRushOption = norush[1]
    end

    if HasCommandLineArg("/predeployed") then
        options.PrebuiltUnits = 'On'
    end

    local victory = GetCommandLineArg("/victory", 1)
    if victory then
        options.Victory = victory[1]
    end

    local diff = GetCommandLineArg("/diff", 1)
    if diff then
        options.Difficulty = tonumber(diff[1])
    end

    return options
end


function SetupBotSession(mapName)
    if not mapName then
        error("SetupBotSession - mapName required")
    end

    mapName = FixupMapName(mapName)

    local sessionInfo = {}

    sessionInfo.playerName = Prefs.GetFromCurrentProfile('Name') or 'Player'
    sessionInfo.createReplay = false

    sessionInfo.scenarioInfo = import('/lua/ui/maputil.lua').LoadScenario(mapName)
    if not sessionInfo.scenarioInfo then
        error("Unable to load map " .. mapName)
    end

    VerifyScenarioConfiguration(sessionInfo.scenarioInfo)

    local armies = sessionInfo.scenarioInfo.Configurations.standard.teams[1].armies

    sessionInfo.teamInfo = {}

    local numColors = table.getn(import('/lua/gameColors.lua').GameColors.PlayerColors)

    local ai
    local aiopt = GetCommandLineArg("/ai", 1)
    if aiopt then
        ai = aiopt[1]
    else
        ai = aitypes[1].key
    end

    LOG('ai=' .. repr(ai))

    for index, name in armies do
        sessionInfo.teamInfo[index] = import('/lua/ui/lobby/lobbyComm.lua').GetDefaultPlayerOptions(sessionInfo.playerName)
        sessionInfo.teamInfo[index].PlayerName = name
        sessionInfo.teamInfo[index].ArmyName = name
        sessionInfo.teamInfo[index].Faction = GetRandomFaction()
        sessionInfo.teamInfo[index].Human = false
        sessionInfo.teamInfo[index].PlayerColor = math.mod(index, numColors)
        sessionInfo.teamInfo[index].ArmyColor = math.mod(index, numColors)
        sessionInfo.teamInfo[index].AIPersonality = ai
    end

    sessionInfo.scenarioInfo.Options = GetCommandLineOptions(false)
    sessionInfo.scenarioMods = import('/lua/mods.lua').GetCampaignMods(sessionInfo.scenarioInfo)

    local seed = GetCommandLineArg("/seed", 1)
    if seed then
        sessionInfo.RandomSeed = tonumber(seed[1])
    end

    return sessionInfo
end

-- Has lua not heard of a split function?
local SplitString = import('/lua/AI/sorianutilities.lua').split

local function SetupCommandLineSkirmish(scenario, isPerfTest)
    --[[]]

    local faction = GetRandomFaction()

    VerifyScenarioConfiguration(scenario)

    scenario.Options = GetCommandLineOptions(isPerfTest)

    sessionInfo = { }
    sessionInfo.playerName = Prefs.GetFromCurrentProfile('Name') or 'Player'
    sessionInfo.createReplay = true
    sessionInfo.scenarioInfo = scenario
    sessionInfo.teamInfo = {}
    sessionInfo.scenarioMods = import('/lua/mods.lua').GetCampaignMods(scenario)

    local seed = GetCommandLineArg("/seed", 1)
    if seed then
        sessionInfo.RandomSeed = tonumber(seed[1])
    elseif isPerfTest then
        sessionInfo.RandomSeed = 2071971
    end

    local armies = sessionInfo.scenarioInfo.Configurations.standard.teams[1].armies

    local numColors = table.getn(import('/lua/gameColors.lua').GameColors.PlayerColors)

    local maxGameTime = tonumber(GetCommandLineArg("/maxtime", 1)[1])

    -- Custom config string, formatted as a comma separated list of '<spawn index>:<AI key>:<faction number>' strings
    local confString = GetCommandLineArg("/aitest", 1)[1]
    local aiTable = {}
    LOG("Config is: "..tostring(confString))
    if confString then
        -- I rather presuppose here that the AI keys don't contain ':' or ','.  If they do then they don't deserve to be supported frankly.
        for _, conf in SplitString(confString,",") do
            local fields = {}
            for _, field in SplitString(conf,":") do
                table.insert(fields,field)
            end
            local faction = tonumber(fields[3])
            if faction == 0 then
                faction = math.random(1,4)
            end
            table.insert(aiTable,{ Spawn = tonumber(fields[1]), AIPersonality = fields[2], Faction = faction, Team = tonumber(fields[4])})
        end
    end
    
    for _, v in aiTable do
        sessionInfo.teamInfo[v.Spawn] = import('/lua/ui/lobby/lobbyComm.lua').GetDefaultPlayerOptions(sessionInfo.playerName)
        sessionInfo.teamInfo[v.Spawn].AIPersonality = v.AIPersonality
        sessionInfo.teamInfo[v.Spawn].Faction = v.Faction
        if v.Team > 0 then
            sessionInfo.teamInfo[v.Spawn].Team = v.Team
        end
        sessionInfo.teamInfo[v.Spawn].PlayerName = tostring(v.Spawn).."_"..v.AIPersonality
        sessionInfo.teamInfo[v.Spawn].Human = false
        sessionInfo.teamInfo[v.Spawn].ArmyName = armies[v.Spawn]
        sessionInfo.teamInfo[v.Spawn].PlayerColor = math.mod(v.Spawn, numColors)
        sessionInfo.teamInfo[v.Spawn].ArmyColor = math.mod(v.Spawn, numColors)
    end

    local extras = MapUtils.GetExtraArmies(sessionInfo.scenarioInfo)
    if extras then
        for k,armyName in extras do
            local index = table.getn(sessionInfo.teamInfo) + 1
            sessionInfo.teamInfo[index] = import('/lua/ui/lobby/lobbyComm.lua').GetDefaultPlayerOptions("civilian")
            sessionInfo.teamInfo[index].PlayerName = 'civilian'
            sessionInfo.teamInfo[index].Civilian = true
            sessionInfo.teamInfo[index].ArmyName = armyName
            sessionInfo.teamInfo[index].Human = false
        end
    end

    sessionInfo.scenarioInfo.Options.Victory = "demoralization"
    sessionInfo.scenarioInfo.Options.AllowObservers = true
    sessionInfo.scenarioInfo.Options.UnitCap = "1000"
    sessionInfo.scenarioInfo.Options.GameSpeed = "fast"
    sessionInfo.scenarioInfo.Options.AIThreatDisplay = 'threatOff'
    sessionInfo.createReplay = true

    Prefs.SetToCurrentProfile('LoadingFaction', faction)

    ForkThread( 
        function()
            local N = 100
            while not WorldIsPlaying() do
                LOG("Waiting for session start....")
                coroutine.yield(N)
            end
            coroutine.yield(N)
            LOG("Setting game speed to be 10...")
            SetGameSpeed(10)
            if maxGameTime then
                while GetGameTimeSeconds() < maxGameTime do
                    coroutine.yield(N)
                end
                SessionEndGame()
            end
        end
    )

    return sessionInfo
end


function StartCommandLineSession(mapName, isPerfTest)
    if not mapName then
        error("SetupCommandLineSession - mapName required")
    end

    mapName = FixupMapName(mapName)

    local scenario = import('/lua/ui/maputil.lua').LoadScenario(mapName)
    if not scenario then
        error("Unable to load map " .. mapName)
    end

    local sessionInfo
    if scenario.type == 'campaign' then
        local difficulty = 2
        if HasCommandLineArg("/diff") then
            difficulty = tonumber(GetCommandLineArg("/diff", 1)[1])
        end
        local faction = false
        if HasCommandLineArg("/faction") then
            faction = GetCommandLineArg("/faction", 1)[1]
        end
        sessionInfo = SetupCampaignSession(scenario, difficulty, faction)
    else
        sessionInfo = SetupCommandLineSkirmish(scenario, isPerfTest)
    end
    LaunchSinglePlayerSession(sessionInfo)
end



