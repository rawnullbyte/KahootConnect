import asyncio
import json
from ..assets.LiveRequestData import LiveRequestData

loop = asyncio.get_event_loop()

def main(self):
    async def requestRecoveryData():
        await asyncio.sleep(0.5)
        promise = loop.create_future()
        def waiter(r):
            promise.set_result(None)
        await self._send(LiveRequestData(self),waiter)
    self.requestRecoveryData = requestRecoveryData
    def handler(message):
        if message["channel"] == "/service/player" and message.get("data") and message["data"].get("id") == 17:
            recover = json.loads(message["data"]["content"])
            self.emit("RecoveryData",recover)
            if not len(self.quiz):
                def questionCount(self):
                    return (self.get("quizQuestionAnswers") and len(self["quizQuestionAnswers"])) or 10
                self.quiz = {
                    "questionCount": property(questionCount)
                }
                self.quiz["quizQuestionAnswers"] = recover["defaultQuizData"]["quizQuestionAnswers"]
                data = recover["data"]
                state = recover["state"]
                if state == 0:
                    pass
                elif state == 1:
                    self._emit("QuizStart",data)
                elif state == 2:
                    self._emit("QuestionReady",data["getReady"])
                elif state == 3:
                    self._emit("QuestionStart",data)
                elif state == 4 or state == 5:
                    self._emit("TimeUp",data)
                elif state == 6:
                    self._emit("QuizEnd",data)
                elif state == 7:
                    self._emit("Feedback")
    self.handlers["recovery"] = handler
    def handler():
        if self.reconnectRecovery:
            loop.create_task(self.requestRecoveryData())
    self.on("Joined",handler)
    def rrd():
        loop.create_task(self.requestRecoveryData())
    self.once("NameAccept",rrd)
