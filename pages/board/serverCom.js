socket      = new WebSocket('ws://localhost:50000/');

var gameName = location.search.substring(1).split("&")[0];
var playerId = location.search.substring(1).split("&")[1];

socket.onopen = function()
{
    clientCmd = {"cmd" : "RECONNECT", "playerId" : playerId, "gameName" : gameName};
    socket.send(JSON.stringify(clientCmd));
};

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
    else if (cmdObj.cmd == "END_GAME")
    {
        window.location = PROJECT_ROOT_PATH + "pages/endScreen/endScreen.html?" + cmdObj.result;
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