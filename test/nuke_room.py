import websockets
import asyncio
import random
import base64
import httpx
import json
import time
import sys
import re

def join(game_pin):
    sessionRequest = httpx.get(f'https://kahoot.it/reserve/session/{game_pin}/?{int(time.time() * 1000)}')

    sessionToken = sessionRequest.headers['x-kahoot-session-token']
    sessionChallenge = sessionRequest.json()['challenge'].replace(' ', '').replace('    ', '').replace(' ', '')  # replace 0x2003 char with nothing

    def getMessage(input_string):
        message_match = re.search(r"decode\.call\(this,'(.*?)'", input_string)
        if message_match:
            message = message_match.group(1)
        else:
            raise ValueError("Message not found in input string")
        return message

    def getOffset(input_string):
        message_match = re.search(r"decode\.call\(this,'(.*?)'", input_string)
        if message_match:
            message = message_match.group(1)
        else:
            raise ValueError("Message not found in input string")

        offset_match = re.search(r'offset\s*=\s*(.*?);', input_string)
        if offset_match:
            offset_expr = offset_match.group(1)
        else:
            raise ValueError("Offset calculation not found in input string")

        try:
            offset = eval(offset_expr)
            logger.debug("Offset derived as: {}", offset)
        except Exception as e:
            raise ValueError(f"Failed to evaluate offset expression: {e}")

        return offset

    def xor_string(e, t):
        o = ""
        for r in range(len(e)):
            n = ord(e[r])
            s = ord(t[r % len(t)])
            a = n ^ s
            o += chr(a)
        return o

    def decode_session_token(e, message, offset_equation):
        r = ''.join(chr((ord(char) * position + eval(str(offset_equation))) % 77 + 48) for position, char in enumerate(getMessage(message)))
        n = base64.b64decode(e).decode('utf-8')
        return xor_string(n, r)

    connToken = decode_session_token(sessionToken, sessionChallenge, getOffset(sessionChallenge))
    logger.debug(f"Got connToken: {connToken}")

    try:
        # Connect to the WebSocket server
        async with websockets.connect(f"wss://kahoot.it/cometd/{game_pin}/{connToken}") as websocket:
            requestId = 1

            handshake_data = {
                "id": str(requestId),
                "version": "1.0",
                "minimumVersion": "1.0",
                "channel": "/meta/handshake",
                "supportedConnectionTypes": ["websocket"],
                "advice": {
                    "timeout": 60000,
                    "interval": 0
                },
                "ext": {
                    "ack": True,
                    "timesync": {
                        "tc": int(time.time() * 1000),
                        "l": 0,
                        "o": 0
                    }
                }
            }
            await websocket.send(json.dumps([handshake_data]))
            logger.debug("Handshake sent: {}", handshake_data)

            requestId += 1

            # Wait for a response from the server
            response = await websocket.recv()
            logger.debug("Received message from server: {}", response)
            clientId = json.loads(response)[0]['clientId']

            connect_data = {
                "id": str(requestId),
                "channel": "/meta/connect",
                "connectionType": "websocket",
                "advice": {"timeout": 0},
                "clientId": clientId,
                "ext": {
                    "ack": 0,
                    "timesync": {
                        "tc": int(time.time() * 1000),
                        "l": 0,
                        "o": 0
                    }
                }
            }
            await websocket.send(json.dumps([connect_data]))
            logger.debug("/meta/connect request sent: {}", connect_data)

            requestId += 1

            # Wait for a response from the server
            response = await websocket.recv()
            logger.debug("Received message from server: {}", response)

            device_info = {
                "device": {
                    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                    "screen": {
                        "width": 1920,
                        "height": 1080
                    }
                }
            }

            login_data = {
                "id": str(requestId),
                "channel": "/service/controller",
                "data": {
                    "type": "login",
                    "gameid": str(game_pin),
                    "host": "kahoot.it",
                    "name": f"PyBot{random.randint(1,1000000)}",
                    "content": json.dumps(device_info)
                },
                "clientId": clientId,
                "ext": {}
            }
            await websocket.send(json.dumps([login_data]))
            logger.debug("/service/controller request sent: {}", login_data)

            requestId += 1

            login_data = [
                {
                    "id": str(requestId),
                    "channel": "/meta/connect",
                    "connectionType": "websocket",
                    "clientId": clientId,
                    "ext": {
                        "ack": 1,
                        "timesync": {
                            "tc": int(time.time() * 1000),
                            "l": 0,
                            "o": 0
                        }
                    }
                }
            ]

            await websocket.send(json.dumps(login_data))
            logger.debug("/meta/connect request sent: {}", login_data)

            requestId += 1

            # Wait for a response from the server
            response = await websocket.recv()
            logger.debug("Received message from server: {}", response)

            message_data = {
                "id": str(requestId),
                "channel": "/service/controller",
                "data": {
                    "gameid": str(game_pin),
                    "type": "message",
                    "host": "kahoot.it",
                    "id": 16,
                    "content": json.dumps({"usingNamerator": False})
                },
                "clientId": clientId,
                "ext": {}
            }

            await websocket.send(json.dumps([message_data]))
            logger.debug("Message sent to server: {}", message_data)

            requestId += 1

            # Wait for a response from the server
            response = await websocket.recv()
            logger.debug("Received message from server: {}", response)

            connect_ack_data = {
                "id": str(requestId),
                "channel": "/meta/connect",
                "connectionType": "websocket",
                "clientId": clientId,
                "ext": {
                    "ack": 2,
                    "timesync": {
                        "tc": int(time.time() * 1000),
                        "l": 0,
                        "o": 0
                    }
                }
            }

            await websocket.send(json.dumps([connect_ack_data]))
            logger.debug("/meta/connect request sent: {}", connect_ack_data)

            requestId += 1

            connect_ack_data2 = {
                "id": str(requestId),
                "channel": "/service/controller",
                "data": {
                    "gameid": game_pin,
                    "type": "message",
                    "host": "kahoot.it",
                    "id": 61,
                    "content": "{\"points\":0}"
                },
                "clientId": clientId,
                "ext": {}
            }

            await websocket.send(json.dumps([connect_ack_data2]))
            logger.debug("/service/controller request sent: {}", connect_ack_data2)

            requestId += 1

            # Heartbeat function
            current_ack = 1  # Start with ack 1

            async def send_heartbeat():
                nonlocal current_ack  # Allow modification of current_ack
                while True:
                    heartbeat_data = {
                        "id": str(requestId),
                        "channel": "/meta/connect",
                        "connectionType": "websocket",
                        "clientId": clientId,
                        "ext": {
                            "ack": current_ack,  # Use the current acknowledgment
                            "timesync": {
                                "tc": int(time.time() * 1000),
                                "l": 0,
                                "o": 0
                            }
                        }
                    }
                    await websocket.send(json.dumps([heartbeat_data]))
                    logger.debug("Heartbeat sent: {}", heartbeat_data)
                    logger.warning("Heartbeat sent!")
                    current_ack += 1  # Increment ack for the next heartbeat
                    await asyncio.sleep(10)  # Wait for 10 seconds before sending the next heartbeat

            # Start the heartbeat task
            heartbeat_task = asyncio.create_task(send_heartbeat())

            while True:
                try:
                    response = await websocket.recv()
                    logger.debug("Received message from server: {}", response)

                except websockets.ConnectionClosed:
                    logger.warning("Connection closed by server.")
                    break
                except Exception as e:
                    logger.error("An error occurred while receiving messages: {}", e)
                    break

    except websockets.ConnectionClosedError as e:
        logger.error("Connection closed with error: {}", e)
    except Exception as e:
        logger.error("An error occurred: {}", e)

if __name__ == "__main__":
    # Configure the logger
    from loguru import logger
    logger.add("debug.log", level="DEBUG", rotation="1 MB", retention="10 days")
    logger.add(sys.stderr, level="INFO")  # Output to stderr for normal logs
    async def run_join_multiple_times(value, times=50):
        tasks = [join(value) for _ in range(times)]
        await asyncio.gather(*tasks)

    # Call the function
    asyncio.run(run_join_multiple_times(8144645))