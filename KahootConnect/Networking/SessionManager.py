from ..Context import shared_context
import httpx
import asyncio
import logging

class SessionManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def get_session(self) -> dict:
        """Retrieve session token and challenge from Kahoot server"""
        try:
            timestamp = int(asyncio.get_event_loop().time() * 1000)
            url = f"https://kahoot.it/reserve/session/{shared_context.game_pin}/?{timestamp}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    session_token = response.headers.get('x-kahoot-session-token')
                    challenge_data = response.json()
                    challenge = challenge_data.get('challenge', '')
                    
                    if session_token and challenge:
                        self.logger.info("Successfully retrieved session data")
                        return {
                            'session_token': session_token,
                            'challenge': challenge
                        }
                    else:
                        raise ValueError("Missing session token or challenge")
                else:
                    raise ConnectionError(f"HTTP error: {response.status_code}")
                    
        except Exception as e:
            self.logger.error(f"Session acquisition failed: {e}")
            raise