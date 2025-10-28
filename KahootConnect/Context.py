class Context:
    def __init__(self):
        self.game_pin = ""
        self.client_id = ""
        self.message_counter = 1
        self.websocket_client = None
        self.player_name = ""
        self.game_event_handler = None
        self.ack_counter = 2
        self.cid = 0
        self.score = 0
        self.rank = 0

# singleton instance
shared_context = Context()