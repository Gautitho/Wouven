////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Main
////////////////////////////////////////////////////////////////////////////////////////////////////////////

var playerId = "";
var gameName = "";
var deckCodeForm = "";
var findState = "IDLE" // IDLE, FINDING
var createState = "IDLE" // IDLE, FINDING
var pseudoInput = document.getElementById("pseudo");
var deckCodeInput = document.getElementById("deckCode");

socket          = new WebSocket('ws://93.19.92.161:3725/');
socket.onopen   = function(){};

setInterval(poll, 5000);

socket.onmessage = function(handler)
{
    console.log(handler.data)
    cmdObj = JSON.parse(handler.data)

    if (cmdObj.cmd === "ERROR")
    {
        errorLog(cmdObj.msg);
        createState = "IDLE";
        $("#createGame").css("background-color", "#552fff");
        $("#createGame").text("Créer");
        findState = "IDLE";
        $("#findGame").css("background-color", "#552fff");
        $("#findGame").text("Chercher");
    }
    else if (cmdObj.cmd === "WAIT_GAME_START")
    {
        errorLog("Waiting for an opponent ...");
    }
    else if (cmdObj.cmd === "CANCEL_GAME_START")
    {
        errorLog("");
    }
    else if (cmdObj.cmd === "GAME_START" || cmdObj.cmd === "GAME_RECONNECT")
    {
        window.location = "pages/board/board.html?" + cmdObj.name + "&" + playerId;
    }
}

pseudoInput.value = localStorage.getItem('playerId');
pseudoInput.addEventListener("change", ($event) => localStorage.setItem('playerId', $event.target.value));

deckCodeInput.value = localStorage.getItem('deckCode');
deckCodeInput.addEventListener("change", ($event) => localStorage.setItem('deckCode', $event.target.value));

////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////////////////////////////////////////

function checkArgs(argList)
{
    for (const arg of argList)
    {
        if (document.getElementById(arg).value === "")
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

function poll()
{
    clientCmd = {"cmd" : "POLL", "playerId" : playerId};
    socket.send(JSON.stringify(clientCmd));
}

function createDeck()
{
    if (findState === "FINDING")
    {
        clientCmd = {"cmd" : "CANCEL_FIND_GAME", "playerId" : playerId};
        findState = "IDLE";
        $("#findGame").css("background-color", "#552fff");
        $("#findGame").text("Chercher");
        $("#createGame").css("background-color", "#552fff");
        $("#createGame").text("Créer");
        socket.send(JSON.stringify(clientCmd));
    }

    window.location = "pages/deckBuild/deckBuild.html";
}

function createGame()
{
    if (checkArgs(["pseudo", "deckCode", "gameNameCreate"]))
    {
        playerId = pseudoInput.value;
        gameName = document.getElementById("gameNameCreate").value;
        deckCodeForm = deckCodeInput.value;
        deck     = {"heroDescId" : deckCodeForm.split("&")[0], "spellDescIdList" : deckCodeForm.split("&").slice(1, 10), "companionDescIdList" : deckCodeForm.split("&").slice(10, 14)};
        if (findState === "IDLE")
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
            $("#findGame").css("background-color", "#552fff");
            $("#findGame").text("Chercher");
        }
        socket.send(JSON.stringify(clientCmd));
    }
}

function joinGame()
{
    if (findState === "FINDING")
    {
        clientCmd = {"cmd" : "CANCEL_FIND_GAME", "playerId" : playerId};
        findState = "IDLE";
        socket.send(JSON.stringify(clientCmd));
        $("#findGame").css("background-color", "#552fff");
        $("#findGame").text("Chercher");
        $("#createGame").css("background-color", "#552fff");
        $("#createGame").text("Créer");
    }

    if (checkArgs(["pseudo", "deckCode", "gameNameJoin"]))
    {
        playerId = pseudoInput.value;
        gameName = document.getElementById("gameNameJoin").value;
        deckCodeForm = deckCodeInput.value;
        deck     = {"heroDescId" : deckCodeForm.split("&")[0], "spellDescIdList" : deckCodeForm.split("&").slice(1, 10), "companionDescIdList" : deckCodeForm.split("&").slice(10, 14)};
        clientCmd = {"cmd" : "JOIN_GAME", "playerId" : playerId, "gameName" : gameName, "deck" : deck};
        socket.send(JSON.stringify(clientCmd));
    }
}

function reconnectGame()
{
    if (findState === "FINDING")
    {
        clientCmd = {"cmd" : "CANCEL_FIND_GAME", "playerId" : playerId};
        findState = "IDLE";
        socket.send(JSON.stringify(clientCmd));
        $("#findGame").css("background-color", "#552fff");
        $("#findGame").text("Chercher");
        $("#createGame").css("background-color", "#552fff");
        $("#createGame").text("Créer");
    }

    if (checkArgs(["pseudo"]))
    {
        playerId = pseudoInput.value;
        clientCmd = {"cmd" : "RECONNECT", "playerId" : playerId};
        socket.send(JSON.stringify(clientCmd));
    }
}

function findGame()
{
    if (checkArgs(["pseudo", "deckCode"]))
    {
        playerId = pseudoInput.value;
        deckCodeForm = deckCodeInput.value;
        deck     = {"heroDescId" : deckCodeForm.split("&")[0], "spellDescIdList" : deckCodeForm.split("&").slice(1, 10), "companionDescIdList" : deckCodeForm.split("&").slice(10, 14)};
        if (findState === "IDLE")
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
            $("#createGame").css("background-color", "#552fff");
            $("#createGame").text("Créer");
        }
        socket.send(JSON.stringify(clientCmd));
    }
}
