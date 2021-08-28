// Available states : INIT, LOCKED, IDLE, MOVE, SPELL, COMPANION
var state = "INIT"; 
var turn = "blue";
var team = "blue";
var entitiesDataBase = {}
var spellsDataBase = {}
var companionsDataBase = {}
var heroesDataBase = {}
var selectedEntity      = -1;
var selectedSpell       = -1;
var selectedMyCompanion = -1;
var entities = {};
var myPlayer = {};
var opPlayer = {};
var boardTileList = [];
var tooltipArray = []

$.getJSON(PROJECT_ROOT_PATH + "data/entities.json", function(data) {entitiesDataBase = data});
$.getJSON(PROJECT_ROOT_PATH + "data/spells.json", function(data) {spellsDataBase = data});
$.getJSON(PROJECT_ROOT_PATH + "data/heroes.json", function(data) {heroesDataBase = data});
$.getJSON(PROJECT_ROOT_PATH + "data/companions.json", function(data) {companionsDataBase = data});

function removeTooltips()
{
    for(i = 0; i < tooltipArray.length; i++)
    {
        tooltipArray[i].destructor()
    }
    tooltipArray = [];
}

function updateState(newState)
{
    if (newState == "IDLE")
    {
        $("#stateBtn").css("background-color", "#00FF00");
        $("#stateBtn").text("Fin de tour");
    }
    else if (newState == "MOVE")
    {
        $("#stateBtn").css("background-color", "#0000FF");
        $("#stateBtn").text("Déplacement");
    }
    else if (newState == "SPELL")
    {
        $("#stateBtn").css("background-color", "#0000FF");
        $("#stateBtn").text("Lancement du sort");
    }
    else if (newState == "SUMMON")
    {
        $("#stateBtn").css("background-color", "#0000FF");
        $("#stateBtn").text("Invocation");
    }
    else
    {
        $("#stateBtn").css("background-color", "#FF0000");
        $("#stateBtn").text("Tour adverse");
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
        }
    }
    for (entityId in entities)
    {
        var imgStr = "";
        for (state in entities[entityId].states)
        {
            imgStr = imgStr + "url(" + PROJECT_ROOT_PATH + "img/" + entities[entityId].states[state].feature + ".png), ";
        }
        if (entities[entityId].elemState != "")
        {
            imgStr = imgStr + "url(" + PROJECT_ROOT_PATH + "img/states/" + entities[entityId].elemState + ".png), ";
        }
        imgStr = imgStr + "url(" + PROJECT_ROOT_PATH + eval("entitiesDataBase." + entities[entityId].descId + ".spritePath") + ")";
        $("#board_" + entities[entityId].x + "_" + entities[entityId].y).css("background-image", imgStr);
        $("#board_" + entities[entityId].x + "_" + entities[entityId].y).css("border-color", entities[entityId].team);
        tooltipArray.push(new Tooltip(document.getElementById("board_" + entities[entityId].x + "_" + entities[entityId].y),
                    "PV : " + entities[entityId].pv + " / " + eval("entitiesDataBase." + entities[entityId].descId + ".pv") + "\n" +
                    "ATK : " + entities[entityId].atk + " / " + eval("entitiesDataBase." + entities[entityId].descId + ".atk") + "\n" +
                    "PM : " + entities[entityId].pm + " / " + eval("entitiesDataBase." + entities[entityId].descId + ".pm"), "txt"));
    }
}

function updateMyStatus()
{
    $("#myStatus").css("border-color", myPlayer.team);
    $("#myStatusSprite").css("background-image", "url(" + PROJECT_ROOT_PATH + eval("entitiesDataBase." + eval("heroesDataBase." + myPlayer.heroDescId + ".entityDescId") + ".spritePath") + ")");
    $("#myStatusPv").text("PV : " + entities[myPlayer.heroEntityId].pv + " / " + eval("entitiesDataBase." + eval("heroesDataBase." + myPlayer.heroDescId + ".entityDescId") + ".pv"));
    $("#myStatusGaugesFire").text(myPlayer.gauges.fire);
    $("#myStatusGaugesWater").text(myPlayer.gauges.water);
    $("#myStatusGaugesEarth").text(myPlayer.gauges.earth);
    $("#myStatusGaugesAir").text(myPlayer.gauges.air);
    $("#myStatusGaugesNeutral").text(myPlayer.gauges.neutral);
    $("#myStatusDescSprite").css("background-image", "url(" + PROJECT_ROOT_PATH + eval("entitiesDataBase." + eval("heroesDataBase." + myPlayer.heroDescId + ".entityDescId") + ".descSpritePath") + ")");
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
    $("#myCompanion_" + companionIdx + "_sprite").css("background-image", "url(" + PROJECT_ROOT_PATH + eval("entitiesDataBase." + eval("companionsDataBase." + myPlayer.companions[companionIdx].descId + ".entityDescId") + ".descSpritePath") + ")");
}

function updateOpStatus()
{
    $("#opStatus").css("border-color", opPlayer.team);
    $("#opStatusSprite").css("background-image", "url(" + PROJECT_ROOT_PATH + eval("entitiesDataBase." + eval("heroesDataBase." + opPlayer.heroDescId + ".entityDescId") + ".spritePath") + ")");
    $("#opStatusPv").text("PV : " + entities[opPlayer.heroEntityId].pv + " / " + eval("entitiesDataBase." + eval("heroesDataBase." + opPlayer.heroDescId + ".entityDescId") + ".pv"));
    $("#opStatusGaugesFire").text(opPlayer.gauges.fire);
    $("#opStatusGaugesWater").text(opPlayer.gauges.water);
    $("#opStatusGaugesEarth").text(opPlayer.gauges.earth);
    $("#opStatusGaugesAir").text(opPlayer.gauges.air);
    $("#opStatusGaugesNeutral").text(opPlayer.gauges.neutral);
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
        $("#spell_" + j).css("background-image", "url(" + PROJECT_ROOT_PATH + eval("spellsDataBase." + myPlayer.handSpellDescIds[j] + ".spritePath") + ")");
        tooltipArray.push(new Tooltip(document.getElementById("spell_" + j), PROJECT_ROOT_PATH + eval("spellsDataBase." + myPlayer.handSpellDescIds[j] + ".descSpritePath"), "img"));
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
        for (entityId in entities)
        {
            if (entities[entityId].x == x && entities[entityId].y == y && entities[entityId].team == team)
            {
                updateState("MOVE");
                selectedEntity = entityId;
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