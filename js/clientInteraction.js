// Available states : LOCKED, IDLE, MOVE, SPELL, COMPANION
var state = "LOCKED"; 
var turn = "blue";
var team = "blue";
var entitiesDataBase = {}
var spellsDataBase = {}
var companionsDataBase = {}
var heroesDataBase = {}
var selectedEntity      = -1;
var selectedSpell       = -1;
var selectedMyCompanion = -1;
var entitiesList = [];
var myPlayer = {};
var opPlayer = {};
var boardTileList = [];
var tooltipArray = []

$.getJSON("data/entities.json", function(data) {entitiesDataBase = data});
$.getJSON("data/spells.json", function(data) {spellsDataBase = data});
$.getJSON("data/heroes.json", function(data) {heroesDataBase = data});
$.getJSON("data/companions.json", function(data) {companionsDataBase = data});

function updateState(newState)
{
    if (newState == "IDLE")
    {
        $("#stateBtn").css("background-color", "#00FF00");
        $("#stateBtn").text("End turn");
    }
    else if (newState == "MOVE")
    {
        $("#stateBtn").css("background-color", "#0000FF");
        $("#stateBtn").text("Move");
    }
    else if (newState == "SPELL")
    {
        $("#stateBtn").css("background-color", "#0000FF");
        $("#stateBtn").text("Cast spell");
    }
    else if (newState == "SUMMON")
    {
        $("#stateBtn").css("background-color", "#0000FF");
        $("#stateBtn").text("Summon");
    }
    else
    {
        $("#stateBtn").css("background-color", "#FF0000");
        $("#stateBtn").text("Opponent turn");
    }
    state = newState;
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
            for(i = 0; i < tooltipArray.length; i++)
            {
                tooltipArray[i].destructor()
            }
            tooltipArray = [];
        }
    }
    for (i = 0; i < entitiesList.length; i++)
    {
        var imgStr = "";
        for (j = 0; j < entitiesList[i].states.length; j++)
        {
            imgStr = imgStr + "url(img/" + entitiesList[i].states[j].feature + ".png), ";
        }
        if (entitiesList[i].elemState != "")
        {
            imgStr = imgStr + "url(img/states/" + entitiesList[i].elemState + ".png), ";
        }
        imgStr = imgStr + "url(" + eval("entitiesDataBase." + entitiesList[i].descId + ".spritePath") + ")";
        $("#board_" + entitiesList[i].x + "_" + entitiesList[i].y).css("background-image", imgStr);
        $("#board_" + entitiesList[i].x + "_" + entitiesList[i].y).css("border-color", entitiesList[i].team);
        tooltipArray.push(new Tooltip(document.getElementById("board_" + entitiesList[i].x + "_" + entitiesList[i].y),
                    "PV : " + entitiesList[i].pv + " / " + eval("entitiesDataBase." + entitiesList[i].descId + ".pv") + "\n" +
                    "ATK : " + entitiesList[i].atk + " / " + eval("entitiesDataBase." + entitiesList[i].descId + ".atk") + "\n" +
                    "PM : " + entitiesList[i].pm + " / " + eval("entitiesDataBase." + entitiesList[i].descId + ".pm")));
    }
}

function updateMyStatus()
{
    $("#myStatus").css("border-color", myPlayer.team);
    $("#myStatusSprite").css("background-image", "url(" + eval("entitiesDataBase." + eval("heroesDataBase." + myPlayer.heroDescId + ".entityDescId") + ".spritePath") + ")");
    $("#myStatusPv").text("PV : " + entitiesList[myPlayer.heroEntityId].pv + " / " + eval("entitiesDataBase." + eval("heroesDataBase." + myPlayer.heroDescId + ".entityDescId") + ".pv"));
    $("#myStatusGauges").text("Gauges : " + myPlayer.gauges.fire + " / " + myPlayer.gauges.water + " / " + myPlayer.gauges.earth + " / " + myPlayer.gauges.air + " / " + myPlayer.gauges.neutral);
}

function updateMyCompanion(companionIdx)
{
    if (myPlayer.companions[companionIdx].state == "alive")
    {
        $("#myCompanion_" + companionIdx).css("background-color", "#a155d4");
    }
    else if (myPlayer.companions[companionIdx].state == "dead")
    {
        $("#myCompanion_" + companionIdx).css("background-color", "#FF0000");
    }
    else
    {
        $("#myCompanion_" + companionIdx).css("background-color", "#FFFFFF");
    }
    $("#myCompanion_" + companionIdx + "_sprite").css("background-image", "url(" + eval("entitiesDataBase." + eval("companionsDataBase." + myPlayer.companions[companionIdx].descId + ".entityDescId") + ".spritePath") + ")");
    $("#myCompanion_" + companionIdx + "_name").text(eval("entitiesDataBase." + eval("companionsDataBase." + myPlayer.companions[companionIdx].descId + ".entityDescId") + ".name"));

    let costStr = "Cost ";
    let gaugeCostArray = ["fire", "water", "earth", "air"];
    for (j = 0; j < gaugeCostArray.length; j++)
    {
        if ((typeof eval("companionsDataBase." + myPlayer.companions[companionIdx].descId + ".cost." + gaugeCostArray[j])) != "undefined")
        {
            costStr = costStr + " / " + eval("companionsDataBase." + myPlayer.companions[companionIdx].descId + ".cost." + gaugeCostArray[j]);
        }
        else
        {
            costStr = costStr + " / 0";
        }
    }
    $("#myCompanion_" + companionIdx + "_cost").text(costStr);
}

function updateOpStatus()
{
    $("#opStatus").css("border-color", opPlayer.team);
    $("#opStatusSprite").css("background-image", "url(" + eval("entitiesDataBase." + eval("heroesDataBase." + opPlayer.heroDescId + ".entityDescId") + ".spritePath") + ")");
    $("#opStatusPv").text("PV : " + entitiesList[opPlayer.heroEntityId].pv + " / " + eval("entitiesDataBase." + eval("heroesDataBase." + opPlayer.heroDescId + ".entityDescId") + ".pv"));
    $("#opStatusGauges").text("Gauges : " + opPlayer.gauges.fire + " / " + opPlayer.gauges.water + " / " + opPlayer.gauges.earth + " / " + opPlayer.gauges.air + " / " + opPlayer.gauges.neutral);
}

function updateHandBar()
{
    $("#pa").text(myPlayer.pa);
    $("#paStock").text(myPlayer.paStock);
    for (i = 0; i < HAND_SPELLS; i++)
    {
        $("#spell_" + i).css("background-image", "");
        $("#spell_" + i).css("background-color", "#FFFFFF");
    }
    for (j = 0; j < myPlayer.handSpellDescIds.length; j++)
    {
        $("#spell_" + j).css("background-image", "url(" + eval("spellsDataBase." + myPlayer.handSpellDescIds[j] + ".spritePath") + ")");
    }
}

function errorLog(message)
{
    $("#errorLog").text(message);
}

function stateBtnClick()
{
    if (state == "IDLE")
    {
        endTurn();
    }
    else if (state == "MOVE")
    {
        move();
        boardTileList = [];
        selectedEntity = -1;
        updateState("IDLE");
    }
    else if (state == "SPELL")
    {
        spell();
        boardTileList = [];
        selectedSpell = -1
        updateState("IDLE");
    }
    else if (state == "SUMMON")
    {
        summon();
        boardTileList = [];
        selectedMyCompanion = -1;
        updateState("IDLE");
    }
}

function cancelBtnClick()
{
    if (state == "MOVE")
    {
        boardTileList = [];
        selectedEntity = -1;
        updateState("IDLE");
        updateBoard();
    }
    else if (state == "SPELL")
    {
        boardTileList = [];
        selectedEntity = -1;
        updateState("IDLE");
        updateBoard();
        updateHandBar();
    }
    else if (state == "SUMMON")
    {
        updateMyCompanion(selectedMyCompanion);
        boardTileList = [];
        selectedMyCompanion = -1;
        updateState("IDLE");
        updateBoard();
    }
}

function paStockClick()
{
    usePaStock();
}

function boardTileClick(tile)
{
    var x = parseInt(tile.attr('id').split('_')[1]);
    var y = parseInt(tile.attr('id').split('_')[2]);

    if (turn != team)
    {
        errorLog("Not your turn, bro !");
    }
    else if (state == "IDLE")
    {
        for (i = 0; i < entitiesList.length; i++)
        {
            if (entitiesList[i].x == x && entitiesList[i].y == y && entitiesList[i].team == team)
            {
                updateState("MOVE");
                selectedEntity = i;
                boardTileList.push({"x" : x, "y" : y});
                $("#board_" + x + "_" + y).css("background-color", "#6DB3F2");
            } 
        }
    }
    else if (state == "MOVE")
    {
        if (boardTileList[boardTileList.length-1].x != x || boardTileList[boardTileList.length-1].y != y)
        {
            boardTileList.push({"x" : x, "y" : y});
            $("#board_" + x + "_" + y).css("background-color", "#6DB3F2");
        }
    }
    else if (state == "SPELL")
    {
        boardTileList.push({"x" : x, "y" : y});
        $("#board_" + x + "_" + y).css("background-color", "#6DB3F2");
    }
    else if (state == "SUMMON")
    {
        boardTileList.push({"x" : x, "y" : y});
        $("#board_" + x + "_" + y).css("background-color", "#6DB3F2");
    }
}

function spellClick(spell)
{
    var spellId = parseInt(spell.attr('id').split('_')[1]);

    if (turn != team)
    {
        errorLog("Not your turn, bro !");
    }
    else if (state == "IDLE")
    {
        updateState("SPELL");
        selectedSpell = spellId;
        $("#spell_" + spellId).css("background-color", "#6DB3F2");
    }
}

function myCompanionClick(myCompanion)
{
    var myCompanionId = parseInt(myCompanion.attr('id').split('_')[1]);

    if (turn != team)
    {
        errorLog("Not your turn, bro !");
    }
    else if (state == "IDLE")
    {
        updateState("SUMMON");
        selectedMyCompanion = myCompanionId;
        $("#myCompanion_" + myCompanionId).css("background-color", "#6DB3F2");
    }
}