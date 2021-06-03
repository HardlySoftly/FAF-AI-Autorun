local YeOldeDoGameResult = DoGameResult
function DoGameResult(armyIndex, result)
    LOG("AutoRunEndResult|"..tostring(armyIndex).."|"..tostring(result))
    YeOldeDoGameResult(armyIndex, result)
end