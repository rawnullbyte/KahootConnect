from json import loads

def main(self):
    def handler(message):
        if message["channel"] == "/service/player" and message.get("data") and message["data"].get("id") == 9:
            self._emit("QuizStart",loads(message["data"]["content"]))
    self.handlers["quizStart"] = handler
