////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Main
////////////////////////////////////////////////////////////////////////////////////////////////////////////

var playerId = "";
var gameName = "";
var deckCode = location.search.substring(1);

$("#deckCode").val(deckCode);

socket          = new WebSocket('ws://localhost:50000/');
socket.onopen   = function(){};

socket.onmessage = function(handler)
{
    console.log(handler.data)
    cmdObj = JSON.parse(handler.data)

    if (cmdObj.cmd == "ERROR")
    {
        errorLog(cmdObj.msg);
    }
    else if (cmdObj.cmd == "WAIT_GAME_START")
    {
        errorLog("Waiting for an opponent ...");
    }
    else if (cmdObj.cmd == "GAME_START")
    {
        window.location = "pages/board/board.html?" + gameName + "&" + playerId;
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////////////////////////////////////////

function errorLog(message)
{
    $("#errorLog").text(message);
}

function createDeck()
{
    window.location = "pages/deckBuild/deckBuild.html";
}

function createGame()
{
    playerId = document.getElementById("pseudo").value;
    gameName = document.getElementById("gameNameCreate").value;
    clientCmd = {"cmd" : "CREATE_GAME", "playerId" : playerId, "gameName" : gameName};
    socket.send(JSON.stringify(clientCmd));
}

function joinGame()
{
    playerId = document.getElementById("pseudo").value;
    gameName = document.getElementById("gameNameJoin").value;
    clientCmd = {"cmd" : "JOIN_GAME", "playerId" : playerId, "gameName" : gameName};
    socket.send(JSON.stringify(clientCmd));
}

function reconnectGame()
{
    
}