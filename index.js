////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Main
////////////////////////////////////////////////////////////////////////////////////////////////////////////

var playerId = "";
var gameName = "";
var deckBuildingCode = location.search.substring(1);
var deckCode = document.getElementById("deckCode").value;
var deck = {"heroDescId" : deckCode.split("&")[0], "spellDescIdList" : deckCode.split("&").slice(1, 10), "companionDescIdList" : deckCode.split("&").slice(10, 14)};
var findState = "IDLE" // IDLE, FINDING
var createState = "IDLE" // IDLE, FINDING

$("#deckCode").val(deckBuildingCode);

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
    else if (cmdObj.cmd == "CANCEL_GAME_START")
    {
        errorLog("");
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
        deckCode = document.getElementById("deckCode").value;
        deck     = {"heroDescId" : deckCode.split("&")[0], "spellDescIdList" : deckCode.split("&").slice(1, 10), "companionDescIdList" : deckCode.split("&").slice(10, 14)};
        if (findState == "IDLE")
        {
            clientCmd = {"cmd" : "CREATE_GAME", "playerId" : playerId, "gameName" : gameName, "deck" : deck};
            createState = "FINDING";
            $("#createGame").css("background-color", "#FF0000");
            $("#createGame").text("Annuler");
        }
        else
        {
            clientCmd = {"cmd" : "CANCEL_CREATE_GAME", "playerId" : playerId};
            createState = "IDLE";
            $("#createGame").css("background-color", "#552fff");
            $("#createGame").text("Créer");
        }
        socket.send(JSON.stringify(clientCmd));
    }
}

function joinGame()
{
    if (checkArgs(["pseudo", "deckCode", "gameNameJoin"]))
    {
        playerId = document.getElementById("pseudo").value;
        gameName = document.getElementById("gameNameJoin").value;
        deckCode = document.getElementById("deckCode").value;
        deck     = {"heroDescId" : deckCode.split("&")[0], "spellDescIdList" : deckCode.split("&").slice(1, 10), "companionDescIdList" : deckCode.split("&").slice(10, 14)};
        clientCmd = {"cmd" : "JOIN_GAME", "playerId" : playerId, "gameName" : gameName, "deck" : deck};
        socket.send(JSON.stringify(clientCmd));
    }
}

function reconnectGame()
{
    if (checkArgs(["pseudo"]))
    {
        playerId = document.getElementById("pseudo").value;
        clientCmd = {"cmd" : "RECONNECT", "playerId" : playerId};
        socket.send(JSON.stringify(clientCmd));
    }
}

function findGame()
{
    if (checkArgs(["pseudo", "deckCode"]))
    {
        playerId = document.getElementById("pseudo").value;
        deckCode = document.getElementById("deckCode").value;
        deck     = {"heroDescId" : deckCode.split("&")[0], "spellDescIdList" : deckCode.split("&").slice(1, 10), "companionDescIdList" : deckCode.split("&").slice(10, 14)};
        console.log(deck)
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
            $("#findGame").text("Chercher");
        }
        socket.send(JSON.stringify(clientCmd));
    }
}