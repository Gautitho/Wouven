////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Main
////////////////////////////////////////////////////////////////////////////////////////////////////////////

const PROJECT_ROOT_PATH = "../../"
const HERO_CLASSES = 5
const HERO_RACE_LIST = ['iop', 'xelor', 'cra']

// Available states : HERO, SPELLS, COMPANIONS
var state = "HERO"
var heroesDataBase      = {}
var entitiesDataBase    = {}
var spellsDataBase      = {}
var companionsDataBase  = {}

$.when(getHeroesDataBase(), getEntitiesDataBase()).then(loadPage)

////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////////////////////////////////////////

function getHeroesDataBase()
{
    return $.getJSON(PROJECT_ROOT_PATH + "data/heroes.json", function(data) {heroesDataBase = data});
}

function getEntitiesDataBase()
{
    return $.getJSON(PROJECT_ROOT_PATH + "data/entities.json", function(data) {entitiesDataBase = data});
}

function getSpellsDataBase()
{
    return $.getJSON(PROJECT_ROOT_PATH + "data/spells.json", function(data) {spellsDataBase = data});
}

function getCompanionsDataBase()
{
    return $.getJSON(PROJECT_ROOT_PATH + "data/companions.json", function(data) {companionsDataBase = data});
}

function loadPage()
{
    cleanPage()
    if (state == "HERO")
    {
        $("#heroBtn").css("background-color", "#FF0000");
        $("#spellsBtn").css("background-color", "#0000FF");
        $("#companionsBtn").css("background-color", "#0000FF");
        heroChoice();
    }
    else if (state == "SPELLS")
    {
        $("#heroBtn").css("background-color", "#0000FF");
        $("#spellsBtn").css("background-color", "#FF0000");
        $("#companionsBtn").css("background-color", "#0000FF");
        spellsChoice();
    }
    else if (state == "COMPANIONS")
    {
        $("#heroBtn").css("background-color", "#0000FF");
        $("#spellsBtn").css("background-color", "#0000FF");
        $("#companionsBtn").css("background-color", "#FF0000");
        companionsChoice();
    }
}

function cleanPage()
{
    document.getElementById("choiceLayout").removeChild(document.getElementById("choiceGrid"));
}

function heroChoice()
{
    document.getElementById("choiceLayout").insertAdjacentHTML('beforeend',`<div id="choiceGrid"></div>`);
    $("#choiceGrid").addClass("flex-grow grid grid-cols-" + String(HERO_RACE_LIST.length) + " grid-rows-" + String(1 + HERO_CLASSES))

    for (y = 0; y < 1 + HERO_CLASSES; y++)
    {
        for (x = 0; x < HERO_RACE_LIST.length; x++)
        {
            if (y == 0)
            {
                document.getElementById("choiceGrid").insertAdjacentHTML('beforeend',`<div id="choiceGrid_${x}"></div>`);
                $("#choiceGrid_" + x).text(HERO_RACE_LIST[x]);
            }
            else
            {
                document.getElementById("choiceGrid").insertAdjacentHTML('beforeend',`<div id="choiceGrid_${x}_${y}" class="border-2 border-light-blue-500 border-opacity-25 relative bg-center bg-contain bg-no-repeat"></div>`);
                $("#choiceGrid_" + x + "_" + y).click(function() {heroClick($(this))});
            }
        } 
    }

    for (x = 0; x < HERO_RACE_LIST.length; x++)
    {
        var y = 1;
        for (h in heroesDataBase)
        {
            if (heroesDataBase[h]["race"] == HERO_RACE_LIST[x])
            {
                $("#choiceGrid_" + x + "_" + y).css("background-image", "url(" + PROJECT_ROOT_PATH + eval("entitiesDataBase." + eval("heroesDataBase." + h + ".entityDescId") + ".descSpritePath") + ")");
                y = y + 1;
            }
        }
    }
}

function spellsChoice()
{
    document.getElementById("choiceLayout").insertAdjacentHTML('beforeend',`<div id="choiceGrid"></div>`);
    $("#choiceGrid").addClass("flex-grow grid grid-cols-" + String(HERO_RACE_LIST.length) + " grid-rows-" + String(1 + HERO_CLASSES))

    for (y = 0; y < 1 + HERO_CLASSES; y++)
    {
        for (x = 0; x < HERO_RACE_LIST.length; x++)
        {
            if (y == 0)
            {
                document.getElementById("choiceGrid").insertAdjacentHTML('beforeend',`<div id="choiceGrid_${x}"></div>`);
                $("#choiceGrid_" + x).text(HERO_RACE_LIST[x]);
            }
            else
            {
                document.getElementById("choiceGrid").insertAdjacentHTML('beforeend',`<div id="choiceGrid_${x}_${y}" class="border-2 border-light-blue-500 border-opacity-25 relative bg-center bg-contain bg-no-repeat"></div>`);
                $("#choiceGrid_" + x + "_" + y).click(function() {heroClick($(this))});
            }
        } 
    }

    for (x = 0; x < HERO_RACE_LIST.length; x++)
    {
        var y = 1;
        for (h in heroesDataBase)
        {
            if (heroesDataBase[h]["race"] == HERO_RACE_LIST[x])
            {
                $("#choiceGrid_" + x + "_" + y).css("background-image", "url(" + PROJECT_ROOT_PATH + eval("entitiesDataBase." + eval("heroesDataBase." + h + ".entityDescId") + ".descSpritePath") + ")");
                y = y + 1;
            }
        }
    }
}

function companionsChoice()
{
    document.getElementById("choiceLayout").insertAdjacentHTML('beforeend',`<div id="choiceGrid"></div>`);
    $("#choiceGrid").addClass("flex-grow grid grid-cols-" + String(HERO_RACE_LIST.length) + " grid-rows-" + String(1 + HERO_CLASSES))

    for (y = 0; y < 1 + HERO_CLASSES; y++)
    {
        for (x = 0; x < HERO_RACE_LIST.length; x++)
        {
            if (y == 0)
            {
                document.getElementById("choiceGrid").insertAdjacentHTML('beforeend',`<div id="choiceGrid_${x}"></div>`);
                $("#choiceGrid_" + x).text(HERO_RACE_LIST[x]);
            }
            else
            {
                document.getElementById("choiceGrid").insertAdjacentHTML('beforeend',`<div id="choiceGrid_${x}_${y}" class="border-2 border-light-blue-500 border-opacity-25 relative bg-center bg-contain bg-no-repeat"></div>`);
                $("#choiceGrid_" + x + "_" + y).click(function() {heroClick($(this))});
            }
        } 
    }

    for (x = 0; x < HERO_RACE_LIST.length; x++)
    {
        var y = 1;
        for (h in heroesDataBase)
        {
            if (heroesDataBase[h]["race"] == HERO_RACE_LIST[x])
            {
                $("#choiceGrid_" + x + "_" + y).css("background-image", "url(" + PROJECT_ROOT_PATH + eval("entitiesDataBase." + eval("heroesDataBase." + h + ".entityDescId") + ".descSpritePath") + ")");
                y = y + 1;
            }
        }
    }
}

function heroChoiceBtnClick()
{
    state = "HERO";
    loadPage();
}

function spellsChoiceBtnBtnClick()
{
    state = "SPELLS";
    loadPage();
}

function companionsChoiceBtnClick()
{
    state = "COMPANIONS";
    loadPage();
}

function heroClick()
{
    console.log("I have clicked");
}