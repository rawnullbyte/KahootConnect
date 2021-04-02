from json import loads

def main(self):
    def handler(message):
        if message["channel"] == "/service/player" and message.get("data") and message["data"].get("id") == 14:
            data = loads(message["data"]["content"])
            self.name = data["playerName"]
            self.emit("NameAccept")
    self.handlers["nameAccept"] = handler
