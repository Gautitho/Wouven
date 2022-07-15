socket      = new WebSocket('ws://localhost:50000/');

var gameName = decodeURI(location.search.substring(1).split("&")[0]);
var playerId = decodeURI(location.search.substring(1).split("&")[1]);

var startGameAudio = new Audio(PROJECT_ROOT_PATH + "pages/board/startGame.mp3");

var turn = "blue";
var team = "blue";
var selectedEntity      = -1;
var selectedSpell       = -1;
var selectedMyCompanion = -1;
var entities = {};
var myPlayer = {};
var opPlayer = {};
var boardTileList = [];
var tooltipArray = [];
var actionList = [];

socket.onopen = function()
{
    clientCmd = {"cmd" : "GET_SPECTATOR_INIT", "playerId" : playerId};
    socket.send(JSON.stringify(clientCmd));
};

socket.onmessage = function(handler)
{
    removeTooltips();
    console.log(handler.data)
    cmdObj = JSON.parse(handler.data)

    if (cmdObj.cmd === "INIT")
    {
        team = cmdObj.team;
        errorLog("");
        startGameAudio.play();
    }
    else if (cmdObj.cmd === "STATUS")
    {
        turn            = cmdObj.turn;
        player0         = cmdObj.player0;
        player1         = cmdObj.player1;
        entities        = cmdObj.entitiesDict;

        errorLog("");
    }
    else if (cmdObj.cmd === "HISTORIC")
    {
        actionList = cmdObj.actionList;
        updateHistoric();
    }
    else if (cmdObj.cmd === "ERROR")
    {
        errorLog(cmdObj.msg);
    }
    else if (cmdObj.cmd === "END_GAME")
    {
        window.location = PROJECT_ROOT_PATH + "pages/endScreen/endScreen.html?" + "finished&" + cmdObj.result;
    }
    else if (cmdObj.cmd === "DELETED_GAME")
    {
        window.location = PROJECT_ROOT_PATH + "pages/endScreen/endScreen.html?" + "deleted&" + cmdObj.gameId;
    }

    updateTurn();
    updateBoard();
    updateStatus();
    for (i = 0; i < COMPANIONS; i++)
    {
        updateCompanion(i);
    }
    updateHandBar();
};

function errorLog(message)
{
    $("#errorLog").text(message);
}

function removeTooltips()
{
    for(i = 0; i < tooltipArray.length; i++)
    {
        tooltipArray[i].destructor()
    }
    tooltipArray = [];
}

function updateHistoric()
{
    for (i = 0; i < ACTION_LIST_LEN; i++)
    {
        $("#historic0_" + i).css("background-image", "");
        $("#historic0_" + i).css("border-color", "");
        $("#historic1_" + i).css("background-image", "");
        $("#historic1_" + i).css("border-color", "");
        $("#historic2_" + i).css("background-image", "");
        $("#historic2_" + i).css("border-color", "");
    }
    for (i = 0; i < actionList.length; i++)
    {
        if (actionList[i].type === "move")
        {
            $("#historic0_" + i).css("background-image", "url(" + PROJECT_ROOT_PATH + actionList[i].source.spritePath + ")");
            $("#historic0_" + i).css("border-color", actionList[i].source.team);
            tooltipArray.push(new Tooltip(document.getElementById("historic0_" + i), PROJECT_ROOT_PATH + actionList[i].source.descSpritePath, "img"));
            $("#historic1_" + i).css("background-image", "url(" + PROJECT_ROOT_PATH + "img/utils/move.png)");
            if (actionList[i].targetList.length > 0)
            {
                $("#historic2_" + i).css("background-image", "url(" + PROJECT_ROOT_PATH + actionList[i].targetList[0].spritePath + ")");
                $("#historic2_" + i).css("border-color", actionList[i].targetList[0].team);
                tooltipArray.push(new Tooltip(document.getElementById("historic2_" + i), PROJECT_ROOT_PATH + actionList[i].targetList[0].descSpritePath, "img"));
            }
        }
        else if (actionList[i].type === "spellCast")
        {
            $("#historic0_" + i).css("background-image", "url(" + PROJECT_ROOT_PATH + actionList[i].source.spritePath + ")"); // TODO : Normaliser ce comportement (ne plus utiliser les data bases dans le client et passer les spritePath par commandes)
            $("#historic0_" + i).css("border-color", actionList[i].source.team);
            tooltipArray.push(new Tooltip(document.getElementById("historic0_" + i), PROJECT_ROOT_PATH + actionList[i].source.descSpritePath, "img"));
            if (actionList[i].targetList.length > 0)
            {
                $("#historic1_" + i).css("background-image", "url(" + PROJECT_ROOT_PATH + actionList[i].targetList[0].spritePath + ")");
                $("#historic1_" + i).css("border-color", actionList[i].targetList[0].team);
                tooltipArray.push(new Tooltip(document.getElementById("historic1_" + i), PROJECT_ROOT_PATH + actionList[i].targetList[0].descSpritePath, "img"));
            }
            if (actionList[i].targetList.length > 1)
            {
                $("#historic2_" + i).css("background-image", "url(" + PROJECT_ROOT_PATH + actionList[i].targetList[1].spritePath + ")");
                $("#historic2_" + i).css("border-color", actionList[i].targetList[1].team);
                tooltipArray.push(new Tooltip(document.getElementById("historic2_" + i), PROJECT_ROOT_PATH + actionList[i].targetList[1].descSpritePath, "img"));
            }
        }
        else if (actionList[i].type === "summon")
        {
            $("#historic0_" + i).css("background-image", "url(" + PROJECT_ROOT_PATH + actionList[i].source.spritePath + ")");
            $("#historic0_" + i).css("border-color", actionList[i].source.team);
            tooltipArray.push(new Tooltip(document.getElementById("historic0_" + i), PROJECT_ROOT_PATH + actionList[i].source.descSpritePath, "img"));
        }
        else if (actionList[i].type === "useReserve")
        {
            $("#historic0_" + i).css("background-image", "url(" + PROJECT_ROOT_PATH + "img/utils/paStock.png)");
            $("#historic0_" + i).css("border-color", actionList[i].source.team);
        }
    }
}

function updateBoard()
{
    for (y = 0; y < BOARD_ROWS; y++)
    {
        for (x = 0; x < BOARD_COLS; x++)
        {
            $("#board_" + x + "_" + y).css("background-color", "#FFFFFF");
            $("#board_" + x + "_" + y).css("background-image", "");
            $("#board_" + x + "_" + y).css("border-color", "#F0F0F0");
        }
    }
    for (entityId in entities)
    {
        var imgStr = "";
        for (stateId = 0; stateId < entities[entityId].states.length; stateId++)
        {
            imgStr = imgStr + "url(" + PROJECT_ROOT_PATH + "img/states/" + entities[entityId].states[stateId].feature + ".png), ";
        }
        if (entities[entityId].elemState != "")
        {
            imgStr = imgStr + "url(" + PROJECT_ROOT_PATH + "img/states/" + entities[entityId].elemState + ".png), ";
        }
        if (entities[entityId].aura.type != "")
        {
            imgStr = imgStr + "url(" + PROJECT_ROOT_PATH + entities[entityId].aura.spritePath + "), ";
        }
        imgStr = imgStr + "url(" + PROJECT_ROOT_PATH + entities[entityId].spritePath + ")";
        $("#board_" + entities[entityId].x + "_" + entities[entityId].y).css("background-image", imgStr);
        $("#board_" + entities[entityId].x + "_" + entities[entityId].y).css("border-color", entities[entityId].team);

        tooltipStr = "PV : " + entities[entityId].pv + " / " + entities[entityId].maxPv + "\n" +
                     "Armure : " + entities[entityId].armor + "\n" +
                     "ATK : " + entities[entityId].atk + "\n" +
                     "PM : " + entities[entityId].pm;
        if (entities[entityId].elemState != "")
        {
            tooltipStr = tooltipStr + "\n" + "Etat élémentaire : " + entities[entityId].elemState;
        }
        if (entities[entityId].states.length > 0)
        {
            tooltipStr = tooltipStr + "\n" + "Etats : ";
            for (stateId = 0; stateId < entities[entityId].states.length; stateId++)
            {
                tooltipStr = tooltipStr + entities[entityId].states[stateId].feature
                if (stateId < entities[entityId].states.length - 1)
                {
                    tooltipStr = tooltipStr + ", ";
                }
            }
        }
        if (entities[entityId].aura.type != "")
        {
            tooltipStr = tooltipStr + "\n" + "Aura : " + entities[entityId].aura.name + " (" + entities[entityId].aura.nb + ")";
        }
        tooltipArray.push(new Tooltip(document.getElementById("board_" + entities[entityId].x + "_" + entities[entityId].y), tooltipStr, "txt"));
    }
}

function updateStatus()
{
    $("#player0Status").css("border-color", player0.team);
    $("#player0StatusSprite").css("background-image", "url(" + PROJECT_ROOT_PATH + entities[player0.heroEntityId].spritePath + ")");
    $("#player0StatusPseudo").text(player0.pseudo);
    $("#player0StatusPv").text("PV : " + entities[player0.heroEntityId].pv + " / " + entities[player0.heroEntityId].maxPv);
    $("#player0StatusGaugesFire").text(player0.gauges.fire);
    $("#player0StatusGaugesWater").text(player0.gauges.water);
    $("#player0StatusGaugesEarth").text(player0.gauges.earth);
    $("#player0StatusGaugesAir").text(player0.gauges.air);
    $("#player0StatusGaugesNeutral").text(player0.gauges.neutral);
    $("#player0StatusDescSprite").css("background-image", "url(" + PROJECT_ROOT_PATH + entities[player0.heroEntityId].descSpritePath + ")");

    $("#player1Status").css("border-color", player1.team);
    $("#player1StatusSprite").css("background-image", "url(" + PROJECT_ROOT_PATH + entities[player1.heroEntityId].spritePath + ")");
    $("#player1StatusPseudo").text(player1.pseudo);
    $("#player1StatusPv").text("PV : " + entities[player1.heroEntityId].pv + " / " + entities[player1.heroEntityId].maxPv);
    $("#player1StatusGaugesFire").text(player1.gauges.fire);
    $("#player1StatusGaugesWater").text(player1.gauges.water);
    $("#player1StatusGaugesEarth").text(player1.gauges.earth);
    $("#player1StatusGaugesAir").text(player1.gauges.air);
    $("#player1StatusGaugesNeutral").text(player1.gauges.neutral);
    $("#player1StatusDescSprite").css("background-image", "url(" + PROJECT_ROOT_PATH + entities[player1.heroEntityId].descSpritePath + ")");
}

function updateCompanion(companionIdx)
{
    if (player0.companionList[companionIdx].state === "alive")
    {
        $("#player0Companion_" + companionIdx).css("background-color", "#a155d4");
    }
    else if (player0.companionList[companionIdx].state === "dead")
    {
        $("#player0Companion_" + companionIdx).css("background-color", "#FF0000");
    }
    else
    {
        $("#player0Companion_" + companionIdx).css("background-color", "#FFFFFF");
    }
    $("#player0Companion_" + companionIdx + "_sprite").css("background-image", "url(" + PROJECT_ROOT_PATH + player0.companionList[companionIdx].descSpritePath + ")");

    if (player1.companionList[companionIdx].state === "alive")
    {
        $("#player1Companion_" + companionIdx).css("background-color", "#a155d4");
    }
    else if (player1.companionList[companionIdx].state === "dead")
    {
        $("#player1Companion_" + companionIdx).css("background-color", "#FF0000");
    }
    else
    {
        $("#player1Companion_" + companionIdx).css("background-color", "#FFFFFF");
    }
    $("#player1Companion_" + companionIdx + "_sprite").css("background-image", "url(" + PROJECT_ROOT_PATH + player0.companionList[companionIdx].descSpritePath + ")");
}

function updateHandBar()
{
    $("#player0Pa").text(player0.pa);
    $("#player0PaStock").text(player0.paStock);
    for (i = 0; i < HAND_SPELLS; i++)
    {
        $("#spell_player0_" + i).css("background-image", "");
        $("#spell_player0_" + i).css("background-color", "#FFFFFF");
        $("#spell_player0_" + i + "_cost").css("background-image", "");
        $("#spell_player0_" + i + "_cost").text("");
        $("#spell_player0_" + i).unbind();
    }
    for (j = 0; j < player0.handSpellList.length; j++)
    {
        $("#spell_player0_" + j).css("background-image", "url(" + PROJECT_ROOT_PATH + player0.handSpellList[j].spritePath + ")");
        $("#spell_player0_" + j + "_cost").css("background-image", "url(" + PROJECT_ROOT_PATH + "img/utils/pa.png)");
        $("#spell_player0_" + j + "_cost").text(player0.handSpellList[j].cost);
        $("#spell_player0_" + j).click(function() {spellClick($(this))});
        tooltipArray.push(new Tooltip(document.getElementById("spell_player0_" + j), PROJECT_ROOT_PATH + player0.handSpellList[j].descSpritePath, "img"));
    }

    $("#player1Pa").text(player1.pa);
    $("#player1PaStock").text(player1.paStock);
    for (i = 0; i < HAND_SPELLS; i++)
    {
        $("#spell_player1_" + i).css("background-image", "");
        $("#spell_player1_" + i).css("background-color", "#FFFFFF");
        $("#spell_player1_" + i + "_cost").css("background-image", "");
        $("#spell_player1_" + i + "_cost").text("");
        $("#spell_player0_" + i).unbind();
    }
    for (j = 0; j < player0.handSpellList.length; j++)
    {
        $("#spell_player1_" + j).css("background-image", "url(" + PROJECT_ROOT_PATH + player1.handSpellList[j].spritePath + ")");
        $("#spell_player1_" + j + "_cost").css("background-image", "url(" + PROJECT_ROOT_PATH + "img/utils/pa.png)");
        $("#spell_player1_" + j + "_cost").text(player0.handSpellList[j].cost);
        $("#spell_player1_" + j).click(function() {spellClick($(this))});
        tooltipArray.push(new Tooltip(document.getElementById("spell_player1_" + j), PROJECT_ROOT_PATH + player1.handSpellList[j].descSpritePath, "img"));
    }
}

function updateTurn()
{
    if (turn === "blue")
    {
        $("#stateBtn").css("background-color", "#0000FF");
        $("#stateBtn").text("Tour bleu");
    }
    else
    {
        $("#stateBtn").css("background-color", "#FF0000");
        $("#stateBtn").text("Tour rouge");
    }
}