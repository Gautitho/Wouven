////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Main
////////////////////////////////////////////////////////////////////////////////////////////////////////////

const PROJECT_ROOT_PATH = "../../"
const HERO_RACE_LIST = ['iop', 'cra', 'sacrieur', 'eniripsa', 'xelor']
const HERO_CLASSES = 5
const ELEMS = ['fire', 'water', 'earth', 'air', 'neutral']
const SPELLS_BY_ELEM = 10
const COMPANION_ROWS_BY_ELEM = 9
const COMPANION_COLS_BY_ELEM = 2
const COMPANION_COLS_FOR_NEUTRAL = 1
const DECK_SPELLS = 9
const DECK_COMPANIONS = 4

// Available choiceDisplayed : HERO, SPELL, COMPANION
var choiceDisplayed         = "HERO"
var heroesDataBase          = {}
var entitiesDataBase        = {}
var spellsDataBase          = {}
var companionsDataBase      = {}
var selectedHero            = "hi0"
var selectedSpellList       = ["shi0"]
var selectedCompanionList   = []
var tooltipArray            = []

var deckBuildingCode        = localStorage.getItem('deckCode');
if (!!deckBuildingCode && deckBuildingCode.split("&").length === 14)
{
    selectedHero            = deckBuildingCode.split("&")[0];
    selectedSpellList       = deckBuildingCode.split("&").slice(1, 10)
    selectedCompanionList   = deckBuildingCode.split("&").slice(10, 14);
}

$.when(getHeroesDataBase(), getEntitiesDataBase(), getSpellsDataBase(), getCompanionsDataBase()).then(loadPage)

////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////////////////////////////////////////

function getHeroesDataBase()
{
    $.getJSON(PROJECT_ROOT_PATH + "data/heroes/iop.json", function(data) {heroesDataBase = {...heroesDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/heroes/xelor.json", function(data) {heroesDataBase = {...heroesDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/heroes/cra.json", function(data) {heroesDataBase = {...heroesDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/heroes/eniripsa.json", function(data) {heroesDataBase = {...heroesDataBase, ...data}});
    return $.getJSON(PROJECT_ROOT_PATH + "data/heroes/sacrieur.json", function(data) {heroesDataBase = {...heroesDataBase, ...data}});
}

function getEntitiesDataBase()
{
    $.getJSON(PROJECT_ROOT_PATH + "data/entities/air.json", function(data) {entitiesDataBase = {...entitiesDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/entities/water.json", function(data) {entitiesDataBase = {...entitiesDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/entities/fire.json", function(data) {entitiesDataBase = {...entitiesDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/entities/earth.json", function(data) {entitiesDataBase = {...entitiesDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/entities/multi.json", function(data) {entitiesDataBase = {...entitiesDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/entities/iop.json", function(data) {entitiesDataBase = {...entitiesDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/entities/xelor.json", function(data) {entitiesDataBase = {...entitiesDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/entities/cra.json", function(data) {entitiesDataBase = {...entitiesDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/entities/eniripsa.json", function(data) {entitiesDataBase = {...entitiesDataBase, ...data}});
    return $.getJSON(PROJECT_ROOT_PATH + "data/entities/sacrieur.json", function(data) {entitiesDataBase = {...entitiesDataBase, ...data}})
}

function getSpellsDataBase()
{
    $.getJSON(PROJECT_ROOT_PATH + "data/spells/air.json", function(data) {spellsDataBase = {...spellsDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/spells/water.json", function(data) {spellsDataBase = {...spellsDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/spells/fire.json", function(data) {spellsDataBase = {...spellsDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/spells/earth.json", function(data) {spellsDataBase = {...spellsDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/spells/iop.json", function(data) {spellsDataBase = {...spellsDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/spells/xelor.json", function(data) {spellsDataBase = {...spellsDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/spells/cra.json", function(data) {spellsDataBase = {...spellsDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/spells/sacrieur.json", function(data) {spellsDataBase = {...spellsDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/spells/eniripsa.json", function(data) {spellsDataBase = {...spellsDataBase, ...data}});
    return $.getJSON(PROJECT_ROOT_PATH + "data/spells/misc.json", function(data) {spellsDataBase = {...spellsDataBase, ...data}})
}

function getCompanionsDataBase()
{
    $.getJSON(PROJECT_ROOT_PATH + "data/companions/air.json", function(data) {companionsDataBase = {...companionsDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/companions/water.json", function(data) {companionsDataBase = {...companionsDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/companions/fire.json", function(data) {companionsDataBase = {...companionsDataBase, ...data}});
    $.getJSON(PROJECT_ROOT_PATH + "data/companions/earth.json", function(data) {companionsDataBase = {...companionsDataBase, ...data}});
    return $.getJSON(PROJECT_ROOT_PATH + "data/companions/multi.json", function(data) {companionsDataBase = {...companionsDataBase, ...data}});
}

function removeTooltips()
{
    for(i = 0; i < tooltipArray.length; i++)
    {
        tooltipArray[i].destructor()
    }
    tooltipArray = [];
}

function loadPage()
{
    cleanPage();
    removeTooltips();
    if (choiceDisplayed === "HERO")
    {
        $("#heroBtn").css("background-color", "#FF0000");
        $("#spellBtn").css("background-color", "#0000FF");
        $("#companionBtn").css("background-color", "#0000FF");
        heroChoice();
    }
    else if (choiceDisplayed === "SPELL")
    {
        $("#heroBtn").css("background-color", "#0000FF");
        $("#spellBtn").css("background-color", "#FF0000");
        $("#companionBtn").css("background-color", "#0000FF");
        spellChoice();
    }
    else if (choiceDisplayed === "COMPANION")
    {
        $("#heroBtn").css("background-color", "#0000FF");
        $("#spellBtn").css("background-color", "#0000FF");
        $("#companionBtn").css("background-color", "#FF0000");
        companionChoice();
    }
    heroBarDisplay();
    spellBarDisplay();
    companionBarDisplay();
    validateBtnDisplay();
}

function cleanPage()
{
    document.getElementById("choiceLayout").removeChild(document.getElementById("choiceGrid"));
    document.getElementById("spellBarLayout").removeChild(document.getElementById("spellBar"));
    document.getElementById("companionBarLayout").removeChild(document.getElementById("companionBar"));
}

function heroChoice()
{
    document.getElementById("choiceLayout").insertAdjacentHTML('beforeend',`<div id="choiceGrid" class="h-full"></div>`);
    $("#choiceGrid").addClass("flex-grow grid grid-cols-" + String(HERO_RACE_LIST.length) + " grid-rows-" + String(HERO_CLASSES))

    for (y = 0; y < HERO_CLASSES; y++)
    {
        for (x = 0; x < HERO_RACE_LIST.length; x++)
        {
            document.getElementById("choiceGrid").insertAdjacentHTML('beforeend',`<div id="choiceGrid_${x}_${y}" class="border-2 border-light-blue-500 border-opacity-25 relative bg-center bg-contain bg-no-repeat"></div>`);
            $("#choiceGrid_" + x + "_" + y).click(function() {heroChoiceClick($(this))});
            $("#choiceGrid_" + x + "_" + y).css("background-color", "#FFFFFF");
        } 
    }

    for (x = 0; x < HERO_RACE_LIST.length; x++)
    {
        var y = 0;
        for (h in heroesDataBase)
        {
            if (heroesDataBase[h]["race"] === HERO_RACE_LIST[x])
            {
                $("#choiceGrid_" + x + "_" + y).css("background-image", "url(" + PROJECT_ROOT_PATH + eval("entitiesDataBase." + eval("heroesDataBase." + h + ".entityDescId") + ".descSpritePath") + ")");
                $("#choiceGrid_" + x + "_" + y).data("heroDescId", h);
                tooltipArray.push(new Tooltip(document.getElementById("choiceGrid_" + x + "_" + y), PROJECT_ROOT_PATH + eval("spellsDataBase." + eval("heroesDataBase." + h + ".spellDescId") + ".descSpritePath"), "img"));
                y = y + 1;
            }
        }
    }
}

function spellChoice()
{
    document.getElementById("choiceLayout").insertAdjacentHTML('beforeend',`<div id="choiceGrid" class="h-full"></div>`);
    $("#choiceGrid").addClass("flex-grow grid grid-cols-" + String(ELEMS.length) + " grid-rows-" + String(SPELLS_BY_ELEM))
    for (y = 0; y < SPELLS_BY_ELEM; y++)
    {
        for (x = 0; x < ELEMS.length; x++)
        {
            document.getElementById("choiceGrid").insertAdjacentHTML('beforeend',`<div id="choiceGrid_${x}_${y}" class="border-2 border-light-blue-500 border-opacity-25 relative bg-center bg-contain bg-no-repeat"></div>`);
            $("#choiceGrid_" + x + "_" + y).click(function() {spellChoiceClick($(this))});
            $("#choiceGrid_" + x + "_" + y).css("background-color", "#FFFFFF");
        } 
    }

    for (x = 0; x <ELEMS.length; x++)
    {
        var y = 0;
        for (s in spellsDataBase)
        {
            if (spellsDataBase[s]["race"] === eval("heroesDataBase." + selectedHero + ".race") && spellsDataBase[s]["elem"] === ELEMS[x])
            {
                if (!(spellsDataBase[s].hasOwnProperty('typeList') && (spellsDataBase[s]["typeList"].includes("destructible"))))
                {
                    $("#choiceGrid_" + x + "_" + y).css("background-image", "url(" + PROJECT_ROOT_PATH + eval("spellsDataBase." + s + ".descSpritePath") + ")");
                    $("#choiceGrid_" + x + "_" + y).data("spellDescId", s);
                    y = y + 1;
                }
            }
        }
    }
}

function companionChoice()
{
    document.getElementById("choiceLayout").insertAdjacentHTML('beforeend',`<div id="choiceGrid" class="h-full"></div>`);
    $("#choiceGrid").addClass("flex-grow grid grid-cols-" + String((ELEMS.length-1)*COMPANION_COLS_BY_ELEM + COMPANION_COLS_FOR_NEUTRAL) + " grid-rows-" + String(COMPANION_ROWS_BY_ELEM))
    for (y = 0; y < COMPANION_ROWS_BY_ELEM; y++)
    {
        for (x0 = 0; x0 < ELEMS.length; x0++)
        {
            if (ELEMS[x0] === 'neutral')
            {
                for (x1 = 0; x1 < COMPANION_COLS_FOR_NEUTRAL; x1++)
                {
                    document.getElementById("choiceGrid").insertAdjacentHTML('beforeend',`<div id="choiceGrid_${x0}_${x1*COMPANION_ROWS_BY_ELEM + y}" class="border-2 border-light-blue-500 border-opacity-25 relative bg-center bg-contain bg-no-repeat"></div>`);
                    $("#choiceGrid_" + x0 + "_" + (x1*COMPANION_ROWS_BY_ELEM + y)).click(function() {companionChoiceClick($(this))});
                    $("#choiceGrid_" + x0 + "_" + (x1*COMPANION_ROWS_BY_ELEM + y)).css("background-color", "#FFFFFF");
                }
            }
            else
            {
                for (x1 = 0; x1 < COMPANION_COLS_BY_ELEM; x1++)
                {
                    document.getElementById("choiceGrid").insertAdjacentHTML('beforeend',`<div id="choiceGrid_${x0}_${x1*COMPANION_ROWS_BY_ELEM + y}" class="border-2 border-light-blue-500 border-opacity-25 relative bg-center bg-contain bg-no-repeat"></div>`);
                    $("#choiceGrid_" + x0 + "_" + (x1*COMPANION_ROWS_BY_ELEM + y)).click(function() {companionChoiceClick($(this))});
                    $("#choiceGrid_" + x0 + "_" + (x1*COMPANION_ROWS_BY_ELEM + y)).css("background-color", "#FFFFFF");
                }
            }
        } 
    }

    for (x = 0; x <ELEMS.length; x++)
    {
        var y = 0;
        for (c in companionsDataBase)
        {
            if (Object.keys(companionsDataBase[c]["cost"]).length === 1 && Object.keys(companionsDataBase[c]["cost"])[0] === ELEMS[x])
            {
                $("#choiceGrid_" + x + "_" + y).css("background-image", "url(" + PROJECT_ROOT_PATH + eval("entitiesDataBase." + eval("companionsDataBase." + c + ".entityDescId") + ".descSpritePath") + ")");
                $("#choiceGrid_" + x + "_" + y).data("companionDescId", c);
                if (eval("companionsDataBase." + c + ".spellDescId"))
                {
                    tooltipArray.push(new Tooltip(document.getElementById("choiceGrid_" + x + "_" + y), PROJECT_ROOT_PATH + eval("spellsDataBase." + eval("companionsDataBase." + c + ".spellDescId") + ".descSpritePath"), "img"));
                }
                y = y + 1;
            }
            else if (Object.keys(companionsDataBase[c]["cost"]).length > 1 && ELEMS[x] === 'neutral')
            {
                $("#choiceGrid_" + x + "_" + y).css("background-image", "url(" + PROJECT_ROOT_PATH + eval("entitiesDataBase." + eval("companionsDataBase." + c + ".entityDescId") + ".descSpritePath") + ")");
                $("#choiceGrid_" + x + "_" + y).data("companionDescId", c);
                if (eval("companionsDataBase." + c + ".spellDescId"))
                {
                    tooltipArray.push(new Tooltip(document.getElementById("choiceGrid_" + x + "_" + y), PROJECT_ROOT_PATH + eval("spellsDataBase." + eval("companionsDataBase." + c + ".spellDescId") + ".descSpritePath"), "img"));
                }
                y = y + 1;
            }
        }
    }
}

function heroBarDisplay()
{
    $("#heroBar").css("background-image", "url(" + PROJECT_ROOT_PATH + eval("entitiesDataBase." + eval("heroesDataBase." + selectedHero + ".entityDescId") + ".spritePath") + ")")
}

function spellBarDisplay()
{
    document.getElementById("spellBarLayout").insertAdjacentHTML('beforeend',`<div id="spellBar" class="grid grid-cols-9 grid-rows-1 w-max mx-4"></div>`);
    for (i = 0; i < DECK_SPELLS; i++)
    {
        document.getElementById("spellBar").insertAdjacentHTML('beforeend',`<div id="spell_${i}" class="h-20 w-20 border-2 border-light-blue-500 border-opacity-25 relative bg-center bg-contain bg-no-repeat"></div>`);
        if (i < selectedSpellList.length)
        {
            $("#spell_" + i).css("background-image", "url(" + PROJECT_ROOT_PATH + eval("spellsDataBase." + selectedSpellList[i] + ".spritePath") + ")");
            $("#spell_" + i).data("spellDescId", selectedSpellList[i]);
            $("#spell_" + i).click(function() {spellBarClick($(this))});
            tooltipArray.push(new Tooltip(document.getElementById("spell_" + i), PROJECT_ROOT_PATH + eval("spellsDataBase." + selectedSpellList[i] + ".descSpritePath"), "img"));
        }
    }
}

function companionBarDisplay()
{
    document.getElementById("companionBarLayout").insertAdjacentHTML('beforeend',`<div id="companionBar" class="grid grid-cols-4 grid-rows-1 w-max mx-4"></div>`);
    for (i = 0; i < DECK_COMPANIONS; i++)
    {
        document.getElementById("companionBar").insertAdjacentHTML('beforeend',`<div id="companion_${i}" class="h-20 w-20 border-2 border-light-blue-500 border-opacity-25 relative bg-center bg-contain bg-no-repeat"></div>`);
        if (i < selectedCompanionList.length)
        {
            $("#companion_" + i).css("background-image", "url(" + PROJECT_ROOT_PATH + eval("entitiesDataBase." + eval("companionsDataBase." + selectedCompanionList[i] + ".entityDescId") + ".spritePath") + ")");
            $("#companion_" + i).data("companionDescId", selectedCompanionList[i]);
            $("#companion_" + i).click(function() {companionBarClick($(this))});
            tooltipArray.push(new Tooltip(document.getElementById("companion_" + i), PROJECT_ROOT_PATH + eval("entitiesDataBase." + eval("companionsDataBase." + selectedCompanionList[i] + ".entityDescId") + ".descSpritePath"), "img"));
        }
    }
}

function validateBtnDisplay()
{
    if (selectedSpellList.length === DECK_SPELLS && selectedCompanionList.length === DECK_COMPANIONS)
    {
        $("#validateBtn").css("background-color", "#00FF00");
        $("#validateBtn").text("Valider");
    }
    else
    {
        $("#validateBtn").css("background-color", "#FF0000");
        $("#validateBtn").text("Deck non rempli");
    }
}

function heroChoiceBtnClick()
{
    choiceDisplayed = "HERO";
    loadPage();
}

function spellChoiceBtnClick()
{
    choiceDisplayed = "SPELL";
    loadPage();
}

function companionChoiceBtnClick()
{
    choiceDisplayed = "COMPANION";
    loadPage();
}

function validateBtnClick()
{
    if (selectedSpellList.length === DECK_SPELLS && selectedCompanionList.length === DECK_COMPANIONS)
    {
        var newDeckCode = selectedHero + "&" + selectedSpellList.join("&") + "&" + selectedCompanionList.join("&");
        localStorage.setItem('deckCode', newDeckCode);
        window.location = PROJECT_ROOT_PATH + "index.html";
    }
}

function heroChoiceClick(div)
{
    if ($("#" + div.attr('id')).data("heroDescId"))
    { 
        selectedHero = $("#" + div.attr('id')).data("heroDescId");
        selectedSpellList = [];
        selectedSpellList.push(heroesDataBase[selectedHero]["spellDescId"]);
        loadPage();
        $("#" + div.attr('id')).css("background-color", "#6DB3F2");
    }
}

function spellChoiceClick(div)
{
    if ($("#" + div.attr('id')).data("spellDescId") && selectedSpellList.length < DECK_SPELLS && !selectedSpellList.includes($("#" + div.attr('id')).data("spellDescId")))
    {
        selectedSpellList.push($("#" + div.attr('id')).data("spellDescId"));
        loadPage();
        $("#" + div.attr('id')).css("background-color", "#6DB3F2");
    }
}

function companionChoiceClick(div)
{
    if ($("#" + div.attr('id')).data("companionDescId") && selectedCompanionList.length < DECK_COMPANIONS && !selectedCompanionList.includes($("#" + div.attr('id')).data("companionDescId")))
    {
        selectedCompanionList.push($("#" + div.attr('id')).data("companionDescId"));
        loadPage();
        $("#" + div.attr('id')).css("background-color", "#6DB3F2");
    }
}

function spellBarClick(div)
{
    if ($("#" + div.attr('id')).data("spellDescId"))
    {
        index = selectedSpellList.indexOf($("#" + div.attr('id')).data("spellDescId"));
        if (index != 0)
        {
            selectedSpellList.splice(index, 1);
            loadPage();
        }
    }
}

function companionBarClick(div)
{
    if ($("#" + div.attr('id')).data("companionDescId"))
    {
        selectedCompanionList.splice(selectedCompanionList.indexOf($("#" + div.attr('id')).data("companionDescId")), 1);
        loadPage();
    }
}
