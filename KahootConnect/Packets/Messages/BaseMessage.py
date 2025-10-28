import json
from typing import Dict, Any
from ...Context import shared_context

class BaseMessage:
    def __init__(self, client_id: str):
        self.client_id = client_id

    def build_base_packet(self, channel: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build base packet structure"""
        return {
            "id": str(shared_context.message_counter),
            "channel": channel,
            "clientId": self.client_id,
            "data": data,
            "ext": self._get_extensions()
        }

    def _get_extensions(self) -> Dict[str, Any]:
        """Get message extensions (timesync)"""
        return {
            "timesync": {
                "tc": self._get_timestamp(),
                "l": 0,
                "o": 0
            }
        }

    def _get_timestamp(self) -> int:
        """Get current timestamp in milliseconds"""
        import asyncio
        return int(asyncio.get_event_loop().time() * 1000)