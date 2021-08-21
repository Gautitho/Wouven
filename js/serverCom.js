socket      = new WebSocket('ws://localhost:50000/');
playerId    = Math.random().toString(36).substring(4);

authCmd = {"cmd" : "AUTH", "playerId" : playerId};
socket.onopen = function() {socket.send(JSON.stringify(authCmd));};

socket.onmessage = function(handler)
{
    removeTooltips();
    console.log(handler.data)
    cmdObj = JSON.parse(handler.data)

    if (cmdObj.cmd == "INIT")
    {
        team = cmdObj.team;
        errorLog("");
    }
    else if (cmdObj.cmd == "STATUS")
    {
        turn            = cmdObj.turn;
        myPlayer        = cmdObj.myPlayer;
        opPlayer        = cmdObj.opPlayer;
        entities        = cmdObj.entitiesDict;

        if (turn == team)
        {
            updateState("IDLE");
        }
        else
        {
            updateState("LOCKED");
        }
        errorLog("");
    }
    else if (cmdObj.cmd == "ERROR")
    {
        errorLog(cmdObj.msg);
    }

    if (state != "INIT")
    {
        updateBoard();
        updateMyStatus();
        updateOpStatus();
        for (i = 0; i < COMPANIONS; i++)
        {
            updateMyCompanion(i);
        }
        updateHandBar();
    }
};

function endTurn()
{
    endTurnCmd = {"cmd" : "ENDTURN", "playerId" : playerId};
    socket.send(JSON.stringify(endTurnCmd));
}

function move()
{
    moveCmd = {"cmd" : "MOVE", "playerId" : playerId, "entityId" : selectedEntity, "path" : boardTileList};
    socket.send(JSON.stringify(moveCmd));
}

function spell()
{
    spellCmd = {"cmd" : "SPELL", "playerId" : playerId, "spellId" : selectedSpell, "targetPositionList" : boardTileList};
    socket.send(JSON.stringify(spellCmd));
}

function summon()
{
    summonCmd = {"cmd" : "SUMMON", "playerId" : playerId, "companionId" : selectedMyCompanion, "summonPositionList" : boardTileList};
    socket.send(JSON.stringify(summonCmd));
}

function usePaStock()
{
    useCmd = {"cmd" : "USE_RESERVE", "playerId" : playerId};
    socket.send(JSON.stringify(useCmd));
}

function createGame()
{

}

function joinGame()
{

}

function reconnectGame()
{
    
}