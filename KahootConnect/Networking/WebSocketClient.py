import websockets
import json
import asyncio
import logging
from typing import Dict, Any, Callable, Optional
from ..Context import shared_context
from ..Packets.Messages.PacketFactory import PacketFactory

class WebSocketClient:
    def __init__(self):
        self.websocket = None
        self.client_id = None
        self.is_connected = False
        self.ack_counter = 0
        self.logger = logging.getLogger(__name__)
        self.heartbeat_task = None
        self.receive_timeout = 1.0  # 1 second timeout for receiving

    async def connect(self, url: str) -> bool:
        """Connect to WebSocket URL"""
        try:
            self.websocket = await websockets.connect(url)
            self.is_connected = True
            self.logger.info(f"Connected to WebSocket: {url}")
            
            # Start heartbeat task
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            return True
        except Exception as e:
            self.logger.error(f"WebSocket connection failed: {e}")
            return False

    async def _heartbeat_loop(self):
        """Maintain heartbeat with server"""
        while self.is_connected and self.websocket:
            try:
                # Send heartbeat every 10 seconds
                await asyncio.sleep(10)
                if self.is_connected and self.client_id:
                    await self.send_heartbeat()
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
                break

    async def send_heartbeat(self):
        """Send heartbeat packet"""
        if not self.is_connected or not self.websocket:
            return
            
        heartbeat_packet = {
            "id": str(shared_context.message_counter),
            "channel": "/meta/connect",
            "connectionType": "websocket",
            "clientId": self.client_id,
            "ext": {
                "ack": self.ack_counter,
                "timesync": {
                    "tc": self._get_timestamp(),
                    "l": 0,
                    "o": 0
                }
            }
        }
        
        await self.send_packet(heartbeat_packet)
        self.logger.debug(f"Sent heartbeat with ack: {self.ack_counter}")

    def _get_timestamp(self) -> int:
        """Get current timestamp in milliseconds"""
        return int(asyncio.get_event_loop().time() * 1000)

    async def send_packet(self, packet: Dict[str, Any]) -> None:
        """Send packet to WebSocket"""
        if not self.is_connected or not self.websocket:
            raise ConnectionError("WebSocket not connected")
        
        await self.websocket.send(json.dumps([packet]))
        file1 = open("packet_log.txt", "a")
        file1.write(f"Sent: {packet}\n") ##################################################################################################
        file1.close()
        self.logger.debug(f"Sent packet: {packet}")
        shared_context.message_counter += 1

    async def receive_packet(self) -> Optional[Dict[str, Any]]:
        """Receive packet from WebSocket with timeout"""
        if not self.is_connected or not self.websocket:
            self.logger.debug("WebSocket not connected, returning None")
            return None
        
        try:
            message = await asyncio.wait_for(
                self.websocket.recv(), 
                timeout=self.receive_timeout
            )
            
            if not message:
                return None
                
            self.logger.debug(f"Raw message received: {message}")

            packets = json.loads(message)
            
            if not packets:
                return {}
                
            packet = packets[0] if packets else {}


            file1 = open("packet_log.txt", "a")
            file1.write(f"Received: {packet}\n") ##################################################################################################
            file1.close()
            
            # CRITICAL FIX: Only update ack counter for connect messages with ack field
            if (packet.get('channel') == '/meta/connect' and 
                packet.get('ext') and 
                'ack' in packet['ext']):
                
                received_ack = packet['ext']['ack']
                # The next ack we send should be received_ack + 1
                shared_context.ack_counter = received_ack + 1
                self.logger.debug(f"Updated ack counter to: {shared_context.ack_counter}")
                    
            self.logger.debug(f"Processed packet: {packet.get('channel', 'unknown')}")
            return packet
            
        except asyncio.TimeoutError:
            return None
        except websockets.exceptions.ConnectionClosed as e:
            self.logger.info(f"WebSocket connection closed: {e}")
            self.is_connected = False
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error receiving packet: {e}")
            return None

    async def disconnect(self) -> None:
        """Disconnect from WebSocket"""
        self.is_connected = False
        
        # Cancel heartbeat task
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        if self.websocket:
            await self.websocket.close()
        self.logger.info("WebSocket disconnected")