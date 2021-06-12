class GameException(Exception):

    def __init__(self, msg):
        self._errorMsg = msg

    @property
    def errorMsg(self):
        return self._errorMsg