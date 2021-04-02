# All of these are the same, just different names

class GameLockedError(Exception):
    def __init__(self,data):
        super().__init__(data)

class JoinFailError(Exception):
    def __init__(self,data):
        super().__init__(data)

class TeamJoinError(Exception):
    def __init__(self,data):
        super().__init__(data)

class SendFailException(Exception):
    def __init__(self,data):
        super().__init__(data)

class AnswerFailException(Exception):
    def __init__(self,data):
        super().__init__(data)

class InvalidPINException(Exception):
    pass
