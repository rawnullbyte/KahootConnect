import json
from typing import Dict, Any, List
from ...Context import shared_context

class PacketFactory:
    @staticmethod
    def _get_timestamp() -> int:
        """Get current timestamp in milliseconds"""
        import time
        return int(time.time() * 1000)

    @staticmethod
    def create_handshake_request() -> Dict[str, Any]:
        """Create handshake packet"""
        packet = {
            "id": PacketFactory.get_message_id(),
            "version": "1.0", 
            "minimumVersion": "1.0",
            "channel": "/meta/handshake",
            "supportedConnectionTypes": ["websocket", "long-polling", "callback-polling"],
            "advice": {"timeout": 60000, "interval": 0},
            "ext": {
                "ack": True,
                "timesync": {"tc": PacketFactory._get_timestamp(), "l": 0, "o": 0}
            }
        }
        return packet

    @staticmethod
    def create_initial_connect() -> Dict[str, Any]:
        """Create initial connect packet"""
        packet = {
            "id": PacketFactory.get_message_id(),
            "channel": "/meta/connect",
            "connectionType": "websocket", 
            "advice": {"timeout": 0},
            "clientId": shared_context.client_id,
            "ext": {
                "ack": 0,
                "timesync": {"tc": PacketFactory._get_timestamp(), "l": 0, "o": 0}
            }
        }
        return packet

    @staticmethod
    def create_connect(ack_value: int) -> Dict[str, Any]:
        """Create connect packet with specific ack value"""
        packet = {
            "id": PacketFactory.get_message_id(),
            "channel": "/meta/connect",
            "connectionType": "websocket",
            "clientId": shared_context.client_id,
            "ext": {
                "ack": ack_value,
                "timesync": {"tc": PacketFactory._get_timestamp(), "l": 0, "o": 0}
            }
        }
        return packet

    @staticmethod
    def create_acknowledgement() -> Dict[str, Any]:
        """Create acknowledgement packet - uses current ack counter value"""
        packet = {
            "id": PacketFactory.get_message_id(),
            "channel": "/meta/connect",
            "connectionType": "websocket",
            "clientId": shared_context.client_id,
            "ext": {
                "ack": shared_context.ack_counter,  # Use current value, don't increment
                "timesync": {"tc": PacketFactory._get_timestamp(), "l": 0, "o": 0}
            }
        }
        return packet

    @staticmethod
    def create_login_request() -> Dict[str, Any]:
        """Create login request packet"""
        packet = {
            "id": PacketFactory.get_message_id(),
            "channel": "/service/controller",
            "data": {
                "type": "login",
                "gameid": shared_context.game_pin,
                "host": "kahoot.it",
                "name": shared_context.player_name,
                "content": "{}"
            },
            "clientId": shared_context.client_id,
            "ext": {}
        }
        return packet

    @staticmethod
    def create_client_ready() -> Dict[str, Any]:
        """Create client ready packet"""
        packet = {
            "id": PacketFactory.get_message_id(),
            "channel": "/service/controller", 
            "data": {
                "gameid": shared_context.game_pin,
                "type": "message",
                "host": "kahoot.it",
                "id": 16,
                "content": json.dumps({"usingNamerator": False})
            },
            "clientId": shared_context.client_id,
            "ext": {}
        }
        return packet

    # =============================
    #  ANSWER PACKETS
    # =============================

    @staticmethod
    def create_classic_answer(question_index: int, choice: int) -> Dict[str, Any]:
        """Create classic answer packet"""
        return PacketFactory._create_answer_base({
            "type": "quiz",
            "choice": choice,
            "questionIndex": question_index
        })

    @staticmethod
    def create_multiple_select_answer(question_index: int, choices: List[int]) -> Dict[str, Any]:
        """Create multiple select quiz answer packet"""
        return PacketFactory._create_answer_base({
            "type": "multiple_select_quiz", 
            "choice": choices,
            "questionIndex": question_index
        })

    @staticmethod
    def create_slider_answer(question_index: int, value: int) -> Dict[str, Any]:
        """Create slider answer packet"""
        return PacketFactory._create_answer_base({
            "type": "slider",
            "choice": value,
            "questionIndex": question_index
        })

    @staticmethod
    def create_open_ended_answer(question_index: int, text: str) -> Dict[str, Any]:
        """Create open-ended answer packet"""
        return PacketFactory._create_answer_base({
            "type": "open_ended",
            "text": text,
            "questionIndex": question_index
        })

    @staticmethod
    def create_jumble_answer(question_index: int, choice: dict) -> Dict[str, Any]:
        """Create jumble answer packet"""
        return PacketFactory._create_answer_base({
            "type": "jumble",
            "choice": choice,
            "questionIndex": question_index
        })

    # =============================
    #  INTERNAL HELPERS  
    # =============================

    @staticmethod
    def _create_answer_base(content: Dict[str, Any]) -> Dict[str, Any]:
        """Base packet structure for all answers"""
        packet = {
            "id": PacketFactory.get_message_id(),
            "channel": "/service/controller",
            "data": {
                "gameid": shared_context.game_pin,
                "type": "message",
                "host": "kahoot.it",
                "id": 45,
                "content": json.dumps(content)
            },
            "clientId": shared_context.client_id,
            "ext": {}
        }
        return packet

    # =============================
    #  GAME INTERACTION PACKETS
    # =============================

    @staticmethod
    def create_join_team(team_name: str) -> Dict[str, Any]:
        """Create join team packet"""
        return PacketFactory._create_answer_base({
            "type": "team_accept",
            "teamName": team_name
        })

    @staticmethod
    def create_leave_team() -> Dict[str, Any]:
        """Create leave team packet"""
        return PacketFactory._create_answer_base({
            "type": "team_leave"
        })

    @staticmethod
    def create_reaction(reaction_type: str) -> Dict[str, Any]:
        """Create reaction packet"""
        return PacketFactory._create_answer_base({
            "type": "reaction",
            "reaction": reaction_type
        })

    @staticmethod
    def create_nickname_change(new_name: str) -> Dict[str, Any]:
        """Create nickname change request packet"""
        packet = {
            "id": PacketFactory.get_message_id(),
            "channel": "/service/controller",
            "data": {
                "gameid": shared_context.game_pin,
                "type": "message",
                "host": "kahoot.it",
                "id": 16,
                "content": json.dumps({
                    "usingNamerator": True,
                    "newName": new_name
                })
            },
            "clientId": shared_context.client_id,
            "ext": {}
        }
        return packet

    # =============================
    #  HEARTBEAT/MAINTENANCE PACKETS
    # =============================

    @staticmethod
    def create_heartbeat() -> Dict[str, Any]:
        """Create heartbeat packet (same as acknowledgement)"""
        return PacketFactory.create_acknowledgement()

    @staticmethod
    def create_disconnect() -> Dict[str, Any]:
        """Create disconnect packet"""
        packet = {
            "id": PacketFactory.get_message_id(),
            "channel": "/meta/disconnect",
            "clientId": shared_context.client_id
        }
        return packet

    # =============================
    #  UTILITY METHODS
    # =============================

    @staticmethod
    def get_message_id() -> str:
        """Get current message ID"""
        return str(shared_context.message_counter)