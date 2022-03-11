import sys
import traceback
from Database import *

DISPLAYED_INFO_TYPE = ["MISC", "INFOB", "INFOG", "INFO", "DEBUG", "WARNING"] # Not displayed : []
logDir = "logs/lastLogDir"

def exitOnError(msg):
    traceback.print_stack(file=sys.stdout)
    print('\033[31m' + "ERROR: " + str(msg) + '\033[0m')
    sys.exit(1)

def calcDist(xa, ya, xb, yb, offset=0):
    return (abs(yb - ya) + abs(xb - xa) + offset)

def checkCondition(triggerError, condition, msg):
    if not(condition):
        if triggerError:
            exitOnError(msg)
        else:
            printLog(msg, "WARNING")

def checkKeyPresence(triggerError, dic, dicName, key, default=""):
    if not(key in dic):
        if triggerError:
            exitOnError(f"Missing [{key}] in {dicName} !")
        else:
            printLog(f"Missing [{key}] in {dicName} ! Set to the default value ({default}).", "WARNING")

def toString(obj, separator=" "):
    if (type(obj) is list):
        s = ""
        for elem in obj:
            s += toString(elem) + separator
        s = s[:-len(separator)]
    elif (type(obj) is dict):
        s = ""
        for key in list(obj.keys()):
            s += str(key) + " : " + toString(obj[key]) + separator
        s = s[:-len(separator)]
    else:
        s = str(obj)
    return s

def printLog(msg, type="MISC", filePath=None, writeMode="a", format="LIGHT"):
    if (type in DISPLAYED_INFO_TYPE):
        if (type == "WARNING"):
            s = '\033[36m' + "WARNING: " + str(msg) + '\033[0m'
        elif (type == "INFOB"):
            s = '\033[34m' + "INFO: " + str(msg) + '\033[0m'
        elif (type == "INFOG"):
            s = '\033[32m' + "INFO: " + str(msg) + '\033[0m'
        elif (type == "INFO"):
            s = "INFO: " + str(msg)
        else:
            s = str(msg)

        if (filePath == None):
            print(s)
        else:
            if LOCAL_ENABLE:
                #print(filePath + " : " + s)
                #pass
                if (filePath == "server.log" or filePath == "client.log"):
                    print(s)
            else:
                fd = open(logDir + "/" + filePath, writeMode)
                fd.write(s + "\n")
                fd.close()