import json

def main(self):
    def handler(message):
        if message["channel"] == "/service/player" and message.get("data") and message["data"].get("id") == 20:
            self._emit("TeamTalk",json.loads(message["data"]["content"]))
    self.handlers["teamTalk"] = handler
