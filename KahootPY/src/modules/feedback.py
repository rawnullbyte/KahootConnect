import asyncio
import time
import json
from ..assets.LiveFeedbackPacket import LiveFeedbackPacket
from ..util.errors import SendFailException

loop = asyncio.get_event_loop()

def main(self):
    def handler(message):
        if message["channel"] == "/service/player" and message.get("data") and message["data"].get("id") == 12:
            self.feedbackTime = int(time.time() * 1000)
            self._emit("Feedback",json.loads(message["data"]["content"]))
    self.handlers["feedback"] = handler
    async def sendFeedback(fun,learn,recommend,overall):
        if str(self.gameid)[0] == "0":
            raise "Cannot send feedback in Challenges"
        wait = int(time.time() * 1000) - self.feedbackTime
        if wait < 500:
            await asyncio.sleep((500 - wait) / 1000)
        promise = loop.create_future()
        def waiter(result):
            if not result or not result.get("successful"):
                promise.set_exception(SendFailException(result))
            else:
                promise.set_result(result)
        await self._send(LiveFeedbackPacket(self,fun,learn,recommend,overall),waiter)
        return promise
    self.sendFeedback = sendFeedback
