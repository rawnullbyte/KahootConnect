import asyncio
import json
import time
import math
from ..assets.LiveQuestionAnswer import LiveQuestionAnswer
from ..util.errors import AnswerFailException

loop = asyncio.get_event_loop()

def main(self):
    async def answer(choice):
        wait = int(time.time() * 1000) - self.questionStartTime
        if math.isnan(wait):
            wait = 0
        if wait < 250:
            await asyncio.sleep((250 - wait) / 1000)
        promise = loop.create_future()
        def waiter(result):
            if not result or not result.get("successful"):
                promise.set_exception(AnswerFailException(result))
            else:
                promise.set_result(result)
        await self._send(LiveQuestionAnswer(self,choice),waiter)
        return promise
