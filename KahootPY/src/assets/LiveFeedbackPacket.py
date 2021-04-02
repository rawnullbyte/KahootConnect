from .LiveBaseMessage import LiveBaseMessage
import json as JSON

class LiveFeedbackPacket(LiveBaseMessage):
    def __init__(self,client,fun,learning,recommend,overall):
        super().__init__("/service/controller",{
            "id": 11,
            "type": "message",
            "gameid": client.gameid,
            "host": "kahoot.it",
            "content": JSON.dumps({
                "totalScore": (client.data and client.data["totalScore"]) or 0,
                "fun": fun,
                "learning": learning,
                "recommend": recommend,
                "overall": overall,
                "nickname": client.name
            })
        })
