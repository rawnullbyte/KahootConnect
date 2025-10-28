import json
import asyncio
import logging
from typing import Dict, Any, Callable, Optional
from ...Context import shared_context
from .BlockContext import BlockContext
from ...Packets.Messages.PacketFactory import PacketFactory

class GameEventHandler:
    def __init__(self):
        self.event_handlers = {
            'onGameBlockUpdate': None,
            'onLeaderboard': None,
            'onGameOver': None
        }
        self.logger = logging.getLogger(__name__)
        self.gameBlocks = {}
        self.lastBlockIndex = 0

    def on_gameBlockUpdate(self, handler: Callable):
        self.event_handlers['onGameBlockUpdate'] = handler

    def on_leaderboard(self, handler: Callable):
        self.event_handlers['onLeaderboard'] = handler

    def on_gameOver(self, handler: Callable):
        self.event_handlers['onGameOver'] = handler

    async def handle_packet(self, packet: Optional[Dict[str, Any]]) -> None:
        """Handle incoming game packet - handles None case"""
        if packet is None:
            return
            
        if not isinstance(packet, dict):
            self.logger.error(f"Received non-dict packet: {type(packet)} - {packet}")
            return
            
        try:
            if packet == None:
                return
            channel = packet.get('channel', '')
            
            # DEBUG: Log all packets to see what we're receiving
            self.logger.debug(f"Handling packet on channel: {channel}")
            
            if channel == '/service/player':
                await self._handle_game_event(packet)
            elif channel == '/meta/connect':
                await self._handle_heartbeat(packet)
            elif channel == '/service/controller':
                self.logger.debug(f"Controller packet: {packet.get('id', 'unknown')}")
            elif channel == '/service/status':
                self.logger.debug(f"Status packet: {packet.get('data', {})}")
            else:
                self.logger.debug(f"Ignoring packet on channel: {channel}")

        except Exception as e:
            self.logger.error(f"Error handling packet: {e} | Packet: {packet}")

    def _call_event_handler(self, event_name, *args, **kwargs):
        handler = self.event_handlers.get(event_name)
        if handler:
            # NON-BLOCKING: Create task instead of awaiting
            asyncio.create_task(handler(*args, **kwargs))
        else:
            self.logger.warning(f"No {event_name} handler registered!")

    async def _handle_game_event(self, packet: Dict[str, Any]) -> None:
        """Handle game event from /service/player channel"""
        data = packet.get('data', {})
        if not data:
            return
            
        content_str = data.get('content', '{}')

        try:
            content = json.loads(content_str)
            gameBlockIndex = content.get('gameBlockIndex')
            if gameBlockIndex is None:
                self.logger.debug("Game event missing gameBlockIndex")
                gameBlockIndex = self.lastBlockIndex
            else:
                self.lastBlockIndex = gameBlockIndex
            
            # Initialize game block if not exists
            if gameBlockIndex not in self.gameBlocks:
                self.gameBlocks[gameBlockIndex] = {
                    "status": "unknown",
                    "content": {},
                    "start_time": 0
                }
                
            gameBlock = self.gameBlocks[gameBlockIndex]

            if data["id"] == 1:  # prefetch
                gameBlock["status"] = "awaiting"
                gameBlock["content"] = content
                gameBlock["start_time"] = packet["ext"]["timetrack"]  # 1761568243975

                self.logger.info(f"🕒 [Block {gameBlockIndex}] Prefetch received at {packet['ext']['timetrack']}")
                self.logger.info(f"❓ Question detected: {content.get('type')} | Title: {content.get('title', 'N/A')}")
                self.logger.debug(f"[Block {gameBlockIndex}] Full content data: {content}")

            elif data["id"] == 2:  # start
                gameBlock["status"] = "started"
                self.logger.info(f"🚀 [Block {gameBlockIndex}] Question started.")
                self.logger.debug(f"[Block {gameBlockIndex}] Current block data: {gameBlock}")

            elif data["id"] == 8:  # end + result
                gameBlock["status"] = "ended"

                if "results" not in gameBlock:
                    gameBlock["results"] = {}
                    self.logger.debug(f"[Block {gameBlockIndex}] Created empty results dict.")

                gameBlock["results"]["content"] = content

                # Merge all info from content into results
                gameBlock["results"].update({
                    "pointsData": content.get("pointsData"),
                    "hasAnswer": content.get("hasAnswer"),
                    "skip": content.get("skip"),
                    "points": content.get("points"),
                    "isCorrect": content.get("isCorrect"),
                })

                self.logger.debug(f"gameBlock DATA:\n{gameBlock}\n\n\n\n\n")

                shared_context.rank = content.get("rank", shared_context.rank)
                shared_context.score = content.get("totalScore", shared_context.score)

                self.logger.info(f"🏁 [Block {gameBlockIndex}] Question ended. "
                                f"Score: {shared_context.score}, Rank: {shared_context.rank}")
                self.logger.debug(f"[Block {gameBlockIndex}] Raw result content: {content}")

                gameBlockType = (gameBlock.get("content") or {}).get("type", "unknown")

                if gameBlockType in ['quiz', 'multiple_select_quiz', 'jumble']:
                    gameBlock["results"]["correctAnswers"] = (
                        gameBlock.get('results', {}).get('content', {}).get('correctChoices', [])
                    )

                    gameBlock["results"]["answers"] = (
                        gameBlock.get('results', {}).get('content', {}).get('choice', [])
                    )
                    
                    self.logger.info(f"✅ [Block {gameBlockIndex}] Correct answers (quiz): "
                                    f"{gameBlock['results']['correctAnswers']}")
                elif gameBlockType == 'open_ended':
                    gameBlock["results"]["correctAnswers"] = (
                        gameBlock.get('results', {}).get('content', {}).get('correctTexts', 'N/A')
                    )

                    gameBlock["results"]["answers"] = (
                        gameBlock.get('results', {}).get('content', {}).get('text', [])
                    )

                    self.logger.info(f"🗒️ [Block {gameBlockIndex}] Correct answers (open-ended): "
                                    f"{gameBlock['results']['correctAnswers']}")
                else:
                    gameBlock["results"]["correctAnswers"] = 'N/A'
                    self.logger.warning(f"⚠️ [Block {gameBlockIndex}] Unknown question type: {gameBlockType}")

                self.logger.debug(f"[Block {gameBlockIndex}] Final gameBlock data: {gameBlock}")

            ctx = BlockContext(gameBlockIndex, gameBlock)
            self.logger.debug(f"📡 Dispatching event 'onGameBlockUpdate' for block {gameBlockIndex}.")
            self._call_event_handler('onGameBlockUpdate', ctx)


        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse game event content: {e}")

    async def _handle_heartbeat(self, packet: Dict[str, Any]) -> None:
        """Handle heartbeat packet - CRITICAL: This must respond to keep connection alive"""
        self.logger.debug(f"💓 Received heartbeat with ack: {packet.get('ext', {}).get('ack')}")
        
        # Send acknowledgement back to server
        ack_packet = PacketFactory.create_acknowledgement()
        await shared_context.websocket_client.send_packet(ack_packet)
        self.logger.debug(f"💓 Sent heartbeat ack: {ack_packet['ext']['ack']}")