////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Main
////////////////////////////////////////////////////////////////////////////////////////////////////////////

var playerId = "";
var gameName = "";
var deckCode = location.search.substring(1);
var deck = {"heroDescId" : deckCode.split("&")[0], "spellDescIdList" : deckCode.split("&").slice(1, 10), "companionDescIdList" : deckCode.split("&").slice(10, 14)};
var findState = "IDLE" // IDLE, FINDING

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

function checkArgs(argList)
{
    for (const arg of argList)
    {
        console.log(arg)
        if (document.getElementById(arg).value == "")
        {
            errorLog(arg + " field must be completed");
            return false;
        }
    }
    return true
}

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
    if (checkArgs(["pseudo", "deckCode", "gameNameCreate"]))
    {
        playerId = document.getElementById("pseudo").value;
        gameName = document.getElementById("gameNameCreate").value;
        clientCmd = {"cmd" : "CREATE_GAME", "playerId" : playerId, "gameName" : gameName, "deck" : deck};
        socket.send(JSON.stringify(clientCmd));
    }
}

function joinGame()
{
    if (checkArgs(["pseudo", "deckCode", "gameNameJoin"]))
    {
        playerId = document.getElementById("pseudo").value;
        gameName = document.getElementById("gameNameJoin").value;
        clientCmd = {"cmd" : "JOIN_GAME", "playerId" : playerId, "gameName" : gameName, "deck" : deck};
        socket.send(JSON.stringify(clientCmd));
    }
}

function reconnectGame()
{
    if (checkArgs(["pseudo", "gameNameReconnect"]))
    {
        playerId = document.getElementById("pseudo").value;
        gameName = document.getElementById("gameNameReconnect").value;
        clientCmd = {"cmd" : "RECONNECT", "playerId" : playerId, "gameName" : gameName};
        socket.send(JSON.stringify(clientCmd));
    }
}

function findGame()
{
    if (checkArgs(["pseudo", "deckCode"]))
    {
        playerId = document.getElementById("pseudo").value;
        if (findState == "IDLE")
        {
            clientCmd = {"cmd" : "FIND_GAME", "playerId" : playerId, "deck" : deck};
            findState = "FINDING";
            $("#findGame").css("background-color", "#FF0000");
            $("#findGame").text("Annuler");
        }
        else
        {
            clientCmd = {"cmd" : "CANCEL_FIND_GAME", "playerId" : playerId};
            findState = "IDLE";
            $("#findGame").css("background-color", "#552fff");
            $("#findGame").text("Trouver une partie");
        }
        socket.send(JSON.stringify(clientCmd));
    }
}