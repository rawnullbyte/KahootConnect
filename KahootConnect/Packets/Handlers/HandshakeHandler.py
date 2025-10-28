import logging
from ...Packets.Messages.PacketFactory import PacketFactory
from ...Context import shared_context

class HandshakeHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def perform_handshake(self) -> str:
        """Perform WebSocket handshake and return client ID"""
        # Reset counters
        shared_context.message_counter = 1
        shared_context.ack_counter = 0
        
        # Send handshake
        await shared_context.websocket_client.send_packet(PacketFactory.create_handshake_request())
        handshake_response = await shared_context.websocket_client.receive_packet()
        
        if not handshake_response or not handshake_response.get('successful'):
            raise ConnectionError("Handshake failed")
            
        shared_context.client_id = handshake_response.get('clientId', '')
        if not shared_context.client_id:
            raise ConnectionError("Failed to receive client ID during handshake")
            
        self.logger.info(f"Received client ID: {shared_context.client_id}")

        # Send initial connect (ack: 0)
        await shared_context.websocket_client.send_packet(PacketFactory.create_initial_connect())
        connect_response = await shared_context.websocket_client.receive_packet()
        
        if not connect_response or not connect_response.get('successful'):
            raise ConnectionError("Initial connect failed")
            
        # Update ack counter based on response
        shared_context.ack_counter = connect_response.get('ext', {}).get('ack', 0) + 1
        
        # Send connect with ack: 1
        await shared_context.websocket_client.send_packet(
            PacketFactory.create_connect(shared_context.ack_counter)
        )
        
        # Send login request
        await shared_context.websocket_client.send_packet(PacketFactory.create_login_request())

        # Wait for login response with CID
        login_response = None
        for _ in range(10):
            response = await shared_context.websocket_client.receive_packet()
            if response and response.get('data', {}).get('cid'):
                login_response = response
                break
            elif response and response.get('channel') == '/meta/connect':
                # Update ack for connect messages
                ack_value = response.get('ext', {}).get('ack', 0)
                shared_context.ack_counter = ack_value + 1

        if not login_response or not login_response.get('data', {}).get('cid'):
            raise ConnectionError("Failed to receive CID during login")

        shared_context.cid = login_response['data']['cid']
        self.logger.info(f"Received CID: {shared_context.cid}")

        # Send client ready
        await shared_context.websocket_client.send_packet(PacketFactory.create_client_ready())

        for _ in range(5):
            response = await shared_context.websocket_client.receive_packet()
            if response and response.get('channel', {}) == '/service/controller': # ack after all messages
                await shared_context.websocket_client.send_packet(PacketFactory.create_acknowledgement())
                break

        for _ in range(5):
            response = await shared_context.websocket_client.receive_packet()
            if response and response.get('channel', {}) == '/service/status':
                if response.get('data', {}).get('status') != 'ACTIVE':
                    raise ConnectionError("Game status is not ACTIVE")
            elif response and response.get('channel') == '/meta/connect': # ack after all messages
                await shared_context.websocket_client.send_packet(PacketFactory.create_acknowledgement())
                break

        for _ in range(5):
            response = await shared_context.websocket_client.receive_packet()
            if response and response.get('channel', {}) == '/service/player':
                playerDataPacket = response
                self.logger.debug("Got player data!")
            elif response and response.get('channel') == '/meta/connect': # ack after all messages
                await shared_context.websocket_client.send_packet(PacketFactory.create_acknowledgement())
                break

        for _ in range(5):
            response = await shared_context.websocket_client.receive_packet()
            if response and response.get('channel', {}) == '/service/player':
                gameDataPacket = response
                self.logger.debug("Got game data!")
            elif response and response.get('channel') == '/meta/connect': # ack after all messages
                await shared_context.websocket_client.send_packet(PacketFactory.create_acknowledgement())
                break

        self.logger.info("Handshake completed successfully")
        return shared_context.client_id