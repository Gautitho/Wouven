import sys
import traceback

DISPLAYED_INFO_TYPE = ["MISC", "WARNING", "DEBUG"]

def exitOnError(msg):
    traceback.print_stack(file=sys.stdout)
    print('\033[31m' + "ERROR: " + str(msg) + '\033[0m')
    sys.exit(1)

def printInfo(msg, type="MISC"):
    if (type in DISPLAYED_INFO_TYPE):
        print('\033[36m' + "INFO: " + str(msg) + '\033[0m')

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

