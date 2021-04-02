from .LiveBaseMessage import LiveBaseMessage
import json

class LiveJoinTeamPacket(LiveBaseMessage):
    def __init__(self,client,team):
        super().__init__("/service/controller",{
            "gameid": client.gameid,
            "host": "kahoot.it",
            "content": json.dumps(team),
            "id": 18,
            "type": "message"
        })
