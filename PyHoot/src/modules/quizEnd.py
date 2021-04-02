from json import loads

def main(self):
    def handler(message):
        if message["channel"] == "/service/player" and message.get("data") and message["data"].get("id") == 3:
            self._emit("QuizEnd",loads(message["data"]["content"]))
    self.handlers["quizEnd"] = handler
