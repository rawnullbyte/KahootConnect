from .LiveBaseMessage import LiveBaseMessage
import json

class LiveJoinPacket(LiveBaseMessage):
    def __init__(self,client,name):
        super().__init__("/service/controller",{
            "gameid": client.gameid,
            "host": "kahoot.it",
            "name": name or "Guido Rossum",
            "type": "login",
            "content": json.dumps({
                "userAgent": client.userAgent,
                "screen": {
                    "width": 1920,
                    "height": 1080
                }
            })
        })
