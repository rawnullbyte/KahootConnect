from json import loads
from json import dumps

def main(self):
    def handler(message):
        if message["channel"] == "/service/player" and message.get("data") and message["data"].get("id") == 19:
            data = loads(message["data"]["content"])
            self.emit("teamAccept",data)
            del self.handlers["teamAccept"]
            if self.handlers.get("recovery"):
                self.handlers["recovery"]({
                    "channel": "/service/player",
                    "data": {
                        "id": 17,
                        "content": dumps(data["recoveryData"])
                    }
                })
    self.handlers["teamAccept"] = handler
