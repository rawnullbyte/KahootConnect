from .LiveBaseMessage import LiveBaseMessage
import time

class LiveLeavePacket(LiveBaseMessage):
    def __init__(self,client):
        super().__init__(client,"/meta/disconnect")
