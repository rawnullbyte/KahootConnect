def main(self):
    def handler(message):
        if message["channel"] == "/service/player" and message.get("data") and message["data"].get("id") == 5:
            self._emit("GameReset")
    self.handlers["gameReset"] = handler
