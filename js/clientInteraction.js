// Available states : LOCKED, IDLE, MOVE, SPELL, COMPANION
var state = "LOCKED"; 
var turn = "blue";
var team = "blue";
var entitiesDataBase = {}
var spellsDataBase = {}
var companionsDataBase = {}
var heroesDataBase = {}
var selectedEntity  = -1;
var selectedSpell   = -1;
var entitiesList = [];
var myPlayer = {};
var opPlayer = {};
var boardTileList = [];

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
        $("#stateBtn").text("End move");
    }
    else if (newState == "SPELL")
    {
        $("#stateBtn").css("background-color", "#0000FF");
        $("#stateBtn").text("End spell cast");
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
        }
    }
    for (i = 0; i < entitiesList.length; i++)
    {
        $("#board_" + entitiesList[i].x + "_" + entitiesList[i].y).css("background-image", "url(" + eval("entitiesDataBase." + entitiesList[i].descId + ".spritePath") + ")");
    }
}

function updateMyStatus()
{
    $("#myStatusSprite").css("background-image", "url(" + eval("entitiesDataBase." + eval("heroesDataBase." + myPlayer.heroDescId + ".entityDescId") + ".spritePath") + ")");
    $("#myStatusPv").text("PV : " + entitiesList[myPlayer.heroEntityId].pv + " / " + eval("entitiesDataBase." + eval("heroesDataBase." + myPlayer.heroDescId + ".entityDescId") + ".pv"));
    $("#myStatusAtk").text("ATK : " + entitiesList[myPlayer.heroEntityId].atk + " / " + eval("entitiesDataBase." + eval("heroesDataBase." + myPlayer.heroDescId + ".entityDescId") + ".atk"));
    $("#myStatusPm").text("PM : " + entitiesList[myPlayer.heroEntityId].pm + " / " + eval("entitiesDataBase." + eval("heroesDataBase." + myPlayer.heroDescId + ".entityDescId") + ".pm"));
}

function updateOpStatus()
{
    $("#opStatusSprite").css("background-image", "url(" + eval("entitiesDataBase." + eval("heroesDataBase." + opPlayer.heroDescId + ".entityDescId") + ".spritePath") + ")");
    $("#opStatusPv").text("PV : " + entitiesList[opPlayer.heroEntityId].pv + " / " + eval("entitiesDataBase." + eval("heroesDataBase." + opPlayer.heroDescId + ".entityDescId") + ".pv"));
    $("#opStatusAtk").text("ATK : " + entitiesList[opPlayer.heroEntityId].atk + " / " + eval("entitiesDataBase." + eval("heroesDataBase." + opPlayer.heroDescId + ".entityDescId") + ".atk"));
    $("#opStatusPm").text("PM : " + entitiesList[opPlayer.heroEntityId].pm + " / " + eval("entitiesDataBase." + eval("heroesDataBase." + opPlayer.heroDescId + ".entityDescId") + ".pm"));
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

function errorLog(message)
{
    $("#errorLog").text(message);
}