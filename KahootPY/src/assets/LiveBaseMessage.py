class LiveBaseMessage(dict):
    def __init__(self,channel,data=None):
        super().__init__()
        self["channel"] = channel
        if data:
            self["data"] = data
