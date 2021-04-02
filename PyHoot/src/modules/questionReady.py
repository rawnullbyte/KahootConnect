from json import loads

def main(self):
    def handler(message):
        if message["channel"] == "/service/player" and message.get("data") and message["data"].get("id") == 1:
            self._emit("QuestionReady",loads(message["data"]["content"]))
    self.handlers["QuestionReady"] = handler
