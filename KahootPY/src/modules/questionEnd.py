from json import loads

def main(self):
    def handler(message):
        if message["channel"] == "/service/player" and message.get("data") and message["data"].get("id") == 8:
            self._emit("QuestionEnd",loads(message["data"]["content"]))
    self.handlers["questionEnd"] = handler
