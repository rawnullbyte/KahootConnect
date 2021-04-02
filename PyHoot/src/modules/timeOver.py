import json

def main(self):
    def handle(message):
        if message["channel"] == "/service/player" and message.get("data") and message["data"].get("id") == 4:
            self._emit("TimeOver",json.loads(message["data"]["content"]))
    self.handlers["timeOver"] = handle
