import sys
import traceback

DISPLAYED_INFO_TYPE = ["MISC", "INFOB", "INFOG", "DEBUG", "WARNING"] #Not displayed : []

def exitOnError(msg):
    traceback.print_stack(file=sys.stdout)
    print('\033[31m' + "ERROR: " + str(msg) + '\033[0m')
    sys.exit(1)

def printInfo(msg, type="MISC"):
    if (type in DISPLAYED_INFO_TYPE):
        if (type == "WARNING"):
            print('\033[36m' + "WARNING: " + str(msg) + '\033[0m')
        elif (type == "INFOB"):
            print('\033[34m' + "INFO: " + str(msg) + '\033[0m')
        elif (type == "INFOG"):
            print('\033[32m' + "INFO: " + str(msg) + '\033[0m')
        else:
            print("INFO: " + str(msg))

def calcDist(xa, ya, xb, yb):
    return (abs(yb - ya) + abs(xb - xa))

def checkCondition(triggerError, condition, msg):
    if not(condition):
        if triggerError:
            exitOnError(msg)
        else:
            printInfo(msg, "WARNING")

def checkKeyPresence(triggerError, dic, dicName, key, default=""):
    if not(key in dic):
        if triggerError:
            exitOnError(f"Missing [{key}] in {dicName} !")
        else:
            printInfo(f"Missing [{key}] in {dicName} ! Set to the default value ({default}).", "WARNING")

