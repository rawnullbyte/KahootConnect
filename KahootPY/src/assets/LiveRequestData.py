from .LiveBaseMessage import LiveBaseMessage

class LiveRequestData(LiveBaseMessage):
    def __init__(self,client):
        super().__init__("/service/controller",{
            "id": 16,
            "type": "message",
            "gameid": client.gameid,
            "host": "kahoot.it",
            "content": ""
        })
