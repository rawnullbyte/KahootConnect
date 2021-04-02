from .LiveBaseMessage import LiveBaseMessage
import json

class LiveTwoStepAnswer(LiveBaseMessage):
    def __init__(self,client,sequence):
        super().__init__("/service/controller",{
            "id": 50,
            "type": "message",
            "gameid": client.gameid,
            "host": "kahoot.it",
            "content": json.dumps({
                "sequence": "".join(sequence)
            })
        })
