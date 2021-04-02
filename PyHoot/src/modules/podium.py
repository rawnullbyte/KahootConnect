from json import loads

def main(self):
    def handler(message):
        if message["channel"] == "/service/player" and message.get("data") and message["data"].get("id") == 13:
            self._emit("Podium",loads(message["data"]["content"]))
        self.handlers["podium"] = handler
