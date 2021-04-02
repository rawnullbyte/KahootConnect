from json import loads
from time import time

def main(self):
    def handler(message):
        if message["channel"] == "/service/player" and message.get("data") and message["data"].get("id") == 2:
            self.questionStartTime = int(time() * 1000)
            self._emit("QuestionStart",loads(message["data"]["content"]))
    self.handlers["questionStart"] = handler
