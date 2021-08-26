socket      = new WebSocket('ws://localhost:50000/');
playerId    = Math.random().toString(36).substring(4);

socket.onopen = function(){};

socket.onmessage = function(handler)
{
    removeTooltips();
    console.log(handler.data)
    cmdObj = JSON.parse(handler.data)

    if (cmdObj.cmd == "INIT")
    {
        team = cmdObj.team;
        window.location = "html/board.html"; //Use ? to pass playerId to next page
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

function createGame()
{
    clientCmd = {"cmd" : "CREATE_GAME", "playerId" : playerId, "gameName" : "Barabara"};
    socket.send(JSON.stringify(clientCmd));
}

function joinGame()
{
    clientCmd = {"cmd" : "JOIN_GAME", "playerId" : playerId, "gameName" : "Barabara"};
    socket.send(JSON.stringify(clientCmd));
}

function reconnectGame()
{
    
}

function endTurn()
{
    clientCmd = {"cmd" : "ENDTURN", "playerId" : playerId};
    socket.send(JSON.stringify(clientCmd));
}

function move()
{
    clientCmd = {"cmd" : "MOVE", "playerId" : playerId, "entityId" : selectedEntity, "path" : boardTileList};
    socket.send(JSON.stringify(clientCmd));
}

function spell()
{
    clientCmd = {"cmd" : "SPELL", "playerId" : playerId, "spellId" : selectedSpell, "targetPositionList" : boardTileList};
    socket.send(JSON.stringify(clientCmd));
}

function summon()
{
    clientCmd = {"cmd" : "SUMMON", "playerId" : playerId, "companionId" : selectedMyCompanion, "summonPositionList" : boardTileList};
    socket.send(JSON.stringify(clientCmd));
}

function usePaStock()
{
    clientCmd = {"cmd" : "USE_RESERVE", "playerId" : playerId};
    socket.send(JSON.stringify(clientCmd));
}