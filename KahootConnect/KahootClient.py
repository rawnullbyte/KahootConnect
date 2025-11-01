# KahootConnect/KahootClient.py
import asyncio
import logging
import json
from typing import Dict, Any, Callable

from .Crypto.TokenDecryptor import TokenDecryptor
from .Networking.SessionManager import SessionManager
from .Networking.WebSocketClient import WebSocketClient
from .Packets.Handlers.HandshakeHandler import HandshakeHandler
from .Packets.Handlers.GameEventHandler import GameEventHandler
from .Context import shared_context

class KahootClient:
    def __init__(self, game_pin: str, player_name: str, debug: bool = False):
        shared_context.debug = debug
        shared_context.game_pin = game_pin
        self.player_name = player_name
        shared_context.player_name = player_name
        
        # Initialize components
        self.token_decryptor = TokenDecryptor()
        self.session_manager = SessionManager()
        self.websocket_client = WebSocketClient()
        shared_context.websocket_client = self.websocket_client
        
        # Initialize handlers - pass websocket_client to GameEventHandler
        self.handshake_handler = HandshakeHandler()
        self.game_event_handler = GameEventHandler()
        shared_context.game_event_handler = self.game_event_handler
        
        self.is_connected = False
        self.logger = logging.getLogger(__name__)

    async def connect(self) -> bool:
        """Connect to Kahoot game"""
        try:
            # Get session data
            session_data = await self.session_manager.get_session()
            
            # Decrypt token
            decrypted_token = self.token_decryptor.decrypt(
                session_data['session_token'],
                session_data['challenge']
            )
            
            # Connect to WebSocket
            ws_url = f"wss://kahoot.it/cometd/{shared_context.game_pin}/{decrypted_token}"
            if not await self.websocket_client.connect(ws_url):
                return False
            
            # Perform handshake
            await self.handshake_handler.perform_handshake()
            
            self.is_connected = True
            self.logger.info("Successfully connected to Kahoot game")
            return True
            
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False

    async def listen(self) -> None:
        """Listen for incoming messages with responsive timing"""
        self.logger.info("Starting to listen for packets...")
        packet_count = 0
        
        while self.is_connected and self.websocket_client.is_connected:
            try:
                self.logger.info("Waiting for next packet...")
                packet = await self.websocket_client.receive_packet()
                self.logger.info("Packet received.")
                packet_count += 1
                
                # Handle timeout case (no data received)
                if packet is None:
                    continue
                    
                # Handle empty dict case
                if packet == {}:
                    continue
                
                # Debug
                channel = packet.get('channel', '')
                self.logger.debug(f"📦 Packet #{packet_count} on channel: {channel}")
                
                # CRITICAL: Process heartbeat packets immediately
                if channel == '/meta/connect':
                    self.logger.debug("💓 Heartbeat packet received - processing immediately")
                    await self.game_event_handler.handle_packet(packet)
                    continue
                    
                if channel == '/service/player':
                    data = packet.get('data', {})
                    content_str = data.get('content', '{}')
                    
                    if content_str is None or content_str == 'null':
                        self.logger.info("🎯 SERVICE/PLAYER PACKET: No content (null)")
                        # Still pass the packet to the handler, it might handle null content
                        await self.game_event_handler.handle_packet(packet)
                        continue

                    # Log the raw content to see what's actually there
                    self.logger.info(f"🎯 SERVICE/PLAYER PACKET: {content_str[:200]}...")
                    
                    try:
                        content = json.loads(content_str)
                        event_type = content.get('type')
                        game_block = content.get('gameBlockIndex')
                        
                        self.logger.info(f"🔍 Parsed: type={event_type}n, block={game_block}")
                        
                    except Exception as e:
                        self.logger.warning(f"❌ Failed to parse content: {e}")
                        self.logger.debug(f"Raw content: {content_str}")
                        
                else:
                    self.logger.debug(f"📡 Other channel: {channel}")
                        
                await self.game_event_handler.handle_packet(packet)
                
            except Exception as e:
                self.logger.error(f"Error in listen loop: {e}")
                self.logger.debug("Full error:", exc_info=True)
                break

        self.logger.info(f"Listen loop ended after {packet_count} packets")
        self.is_connected = False

    async def disconnect(self) -> None:
        """Disconnect from game"""
        self.is_connected = False
        await self.websocket_client.disconnect()
        self.logger.info("Disconnected from Kahoot game")

    # Event handler proxy methods
    def on_gameBlockUpdate(self, handler: Callable):
        self.game_event_handler.on_gameBlockUpdate(handler)

    def on_leaderboard(self, handler: Callable):
        self.game_event_handler.on_leaderboard(handler)

    def on_gameOver(self, handler: Callable):
        self.game_event_handler.on_gameOver(handler)