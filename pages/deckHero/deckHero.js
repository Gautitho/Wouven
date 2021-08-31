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
}

function errorLog(message)
{
    $("#errorLog").text(message);
}

function heroClick()
{
    console.log("I have clicked");
}