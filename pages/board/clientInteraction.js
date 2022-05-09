// Available states : INIT, LOCKED, IDLE, MOVE, SPELL, COMPANION
var state = "INIT"; 
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

function updateMyStatus()
{
    $("#myStatus").css("border-color", myPlayer.team);
    $("#myStatusSprite").css("background-image", "url(" + PROJECT_ROOT_PATH + entities[myPlayer.heroEntityId].spritePath + ")");
    $("#myStatusPseudo").text(myPlayer.pseudo);
    $("#myStatusPv").text("PV : " + entities[myPlayer.heroEntityId].pv + " / " + entities[myPlayer.heroEntityId].maxPv);
    $("#myStatusGaugesFire").text(myPlayer.gauges.fire);
    $("#myStatusGaugesWater").text(myPlayer.gauges.water);
    $("#myStatusGaugesEarth").text(myPlayer.gauges.earth);
    $("#myStatusGaugesAir").text(myPlayer.gauges.air);
    $("#myStatusGaugesNeutral").text(myPlayer.gauges.neutral);
    $("#myStatusDescSprite").css("background-image", "url(" + PROJECT_ROOT_PATH + entities[myPlayer.heroEntityId].descSpritePath + ")");
}

function updateMyCompanion(companionIdx)
{
    if (myPlayer.companionList[companionIdx].state == "alive")
    {
        $("#myCompanion_" + companionIdx).css("background-color", "#a155d4");
    }
    else if (myPlayer.companionList[companionIdx].state == "dead")
    {
        $("#myCompanion_" + companionIdx).css("background-color", "#FF0000");
    }
    else
    {
        $("#myCompanion_" + companionIdx).css("background-color", "#FFFFFF");
    }
    $("#myCompanion_" + companionIdx + "_sprite").css("background-image", "url(" + PROJECT_ROOT_PATH + myPlayer.companionList[companionIdx].descSpritePath + ")");
}

function updateOpStatus()
{
    $("#opStatus").css("border-color", opPlayer.team);
    $("#opStatusSprite").css("background-image", "url(" + PROJECT_ROOT_PATH + entities[opPlayer.heroEntityId].spritePath + ")");
    $("#opStatusPseudo").text(opPlayer.pseudo);
    $("#opStatusPv").text("PV : " + entities[opPlayer.heroEntityId].pv + " / " + entities[opPlayer.heroEntityId].maxPv);
    $("#opStatusGaugesFire").text(opPlayer.gauges.fire);
    $("#opStatusGaugesWater").text(opPlayer.gauges.water);
    $("#opStatusGaugesEarth").text(opPlayer.gauges.earth);
    $("#opStatusGaugesAir").text(opPlayer.gauges.air);
    $("#opStatusGaugesNeutral").text(opPlayer.gauges.neutral);
    $("#opStatusPa").text(opPlayer.pa);
    $("#opStatusPaStock").text(opPlayer.paStock);
    $("#opStatusHandSize").text(opPlayer.handSize);
    $("#opStatusDescSprite").css("background-image", "url(" + PROJECT_ROOT_PATH + entities[opPlayer.heroEntityId].descSpritePath + ")");
}

function updateHandBar()
{
    $("#pa").text(myPlayer.pa);
    $("#paStock").text(myPlayer.paStock);
    for (i = 0; i < HAND_SPELLS; i++)
    {
        $("#spell_" + i).css("background-image", "");
        $("#spell_" + i).css("background-color", "#FFFFFF");
        $("#spell_" + i + "_cost").css("background-image", "");
        $("#spell_" + i + "_cost").text("");
        $("#spell_" + i).unbind();
    }
    for (j = 0; j < myPlayer.handSpellList.length; j++)
    {
        $("#spell_" + j).css("background-image", "url(" + PROJECT_ROOT_PATH + myPlayer.handSpellList[j].spritePath + ")");
        $("#spell_" + j + "_cost").css("background-image", "url(" + PROJECT_ROOT_PATH + "img/utils/pa.png)");
        $("#spell_" + j + "_cost").text(myPlayer.handSpellList[j].cost);
        $("#spell_" + j).click(function() {spellClick($(this))});
        tooltipArray.push(new Tooltip(document.getElementById("spell_" + j), PROJECT_ROOT_PATH + myPlayer.handSpellList[j].descSpritePath, "img"));
    }
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
        if (actionList[i].type == "move")
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
        else if (actionList[i].type == "spellCast")
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
        else if (actionList[i].type == "summon")
        {
            $("#historic0_" + i).css("background-image", "url(" + PROJECT_ROOT_PATH + actionList[i].source.spritePath + ")");
            $("#historic0_" + i).css("border-color", actionList[i].source.team);
            tooltipArray.push(new Tooltip(document.getElementById("historic0_" + i), PROJECT_ROOT_PATH + actionList[i].source.descSpritePath, "img"));
        }
        else if (actionList[i].type == "useReserve")
        {
            $("#historic0_" + i).css("background-image", "url(" + PROJECT_ROOT_PATH + "img/utils/paStock.png)");
            $("#historic0_" + i).css("border-color", actionList[i].source.team);
        }
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

function surrendBtnClick()
{
    surrend();
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
    var spellIdx = parseInt(spell.attr('id').split('_')[1]);

    if (turn != team)
    {
        errorLog("Not your turn, bro !");
    }
    else if (state == "IDLE")
    {
        updateState("SPELL");
        selectedSpell = spellIdx;
        $("#spell_" + spellIdx).css("background-color", "#6DB3F2");
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