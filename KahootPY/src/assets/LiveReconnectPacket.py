from .LiveBaseMessage import LiveBaseMessage
import json

class LiveReconnectPacket(LiveBaseMessage):
    def __init__(self,client,pin,cid):
        super().__init__("/service/controller",{
            "gameid": str(pin),
            "host": "kahoot.it",
            "content": json.dumps({
                "device": {
                    "userAgent": client.userAgent,
                    "screen": {
                        "width": 1980,
                        "height": 1080
                    }
                }
            }),
            "cid": str(cid),
            "type": "relogin"
        })
