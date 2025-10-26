# Kahoot Protocol Documentation
*Complete Reverse Engineering Guide*

## Table of Contents
1. [Session Acquisition](#session-acquisition)
2. [Token Decryption](#token-decryption)
3. [WebSocket Protocol](#websocket-protocol)
4. [Packet Structure](#packet-structure)
5. [Game Events](#game-events)
6. [Answer System](#answer-system)

---

## Session Acquisition

### HTTP Request
```http
GET https://kahoot.it/reserve/session/{GAME_PIN}/?{TIMESTAMP}
```

**Parameters:**
- `GAME_PIN`: 6-7 digit game code
- `TIMESTAMP`: Current Unix timestamp in milliseconds

### Response Headers
```http
HTTP/1.1 200 OK
x-kahoot-session-token: ENCRYPTED_TOKEN
x-kahoot-gameserver: https://play.kahoot.it
Content-Type: application/json
```

### Response Body
```json
{
  "challenge": "javascript code containing decode function"
}
```

**Example Challenge:**
```javascript
var offset = ((98*87)*73*(90+86*7));function decode(e){var t=offset;var o="";var r="V10tWQX5hk9F6MYjKlHH3qrwPGXksizp...";for(var n=0;n<e.length;n++){var a=e.charCodeAt(n);var i=r.charCodeAt(n%r.length);var s=a^i;o+=String.fromCharCode(s)}return o}decode.call(this,'ENCRYPTED_TOKEN');
```

---

## Token Decryption

### Step 1: Extract Components

#### Get Message String
```python
import re

def get_message(challenge):
    match = re.search(r"decode\.call\(this,'(.*?)'", challenge)
    if match:
        return match.group(1)
    raise ValueError("Message not found")
```

#### Get Offset Calculation
```python
def get_offset(challenge):
    # Remove invisible characters
    clean_challenge = challenge.replace(' ', '').replace('    ', '').replace(' ', '')
    
    match = re.search(r'offset\s*=\s*(.*?);', clean_challenge)
    if match:
        offset_expr = match.group(1)
        return eval(offset_expr)
    raise ValueError("Offset not found")
```

**Common Offset Patterns:**
- `((84*33)*28)+28*61` = 79324
- `(98*87)*73*(90+86*7)` = 430699416
- `((76*13)*19)+19*47` = 20615

### Step 2: Generate XOR Key
```python
def generate_key(message, offset):
    key = ""
    for position, char in enumerate(message):
        key_char = chr((ord(char) * position + offset) % 77 + 48)
        key += key_char
    return key
```

### Step 3: XOR Decryption
```python
import base64

def xor_decrypt(encrypted_token, key):
    # Decode base64 token
    decoded_token = base64.b64decode(encrypted_token).decode('utf-8')
    
    # XOR decrypt
    result = ""
    for i in range(len(decoded_token)):
        char_code = ord(decoded_token[i])
        key_code = ord(key[i % len(key)])
        result += chr(char_code ^ key_code)
    
    return result
```

### Complete Decryption Function
```python
def decrypt_session_token(encrypted_token, challenge):
    message = get_message(challenge)
    offset = get_offset(challenge)
    key = generate_key(message, offset)
    return xor_decrypt(encrypted_token, key)
```

**Example Output:**
```
8a4c9a11330b463dda795501017c31f8af02b86f28b046909ae5146b92455fccd0902228168581785563d6cb690638a7
```

---

## WebSocket Protocol

### Connection URL
```
wss://kahoot.it/cometd/{GAME_PIN}/{DECRYPTED_TOKEN}
```

### Bayeux Protocol
Kahoot uses the Bayeux protocol over WebSocket with the following channels:

#### Core Channels:
- `/meta/handshake` - Initial connection
- `/meta/connect` - Heartbeats and acknowledgments
- `/meta/subscribe` - Channel subscriptions
- `/meta/unsubscribe` - Channel unsubscriptions

#### Service Channels:
- `/service/controller` - Game control messages
- `/service/player` - Player-specific events
- `/service/status` - Game status updates

---

## Packet Structure

### Base Packet Format
```json
{
  "id": "1",
  "channel": "/channel/name",
  "data": {},
  "clientId": "CLIENT_ID",
  "ext": {}
}
```

### Handshake Sequence

#### Step 1: Client Handshake
```json
[{
  "id": "1",
  "version": "1.0",
  "minimumVersion": "1.0",
  "channel": "/meta/handshake",
  "supportedConnectionTypes": ["websocket"],
  "advice": {
    "timeout": 60000,
    "interval": 0
  },
  "ext": {
    "ack": true,
    "timesync": {
      "tc": 1761479379758,
      "l": 0,
      "o": 0
    }
  }
}]
```

#### Step 2: Server Response
```json
[{
  "ext": {
    "timesync": {
      "p": 1,
      "a": -35,
      "tc": 1761479379758,
      "ts": 1761479379793
    },
    "ack": true
  },
  "minimumVersion": "1.0",
  "clientId": "flvzz5qggsxzvsnlq1u152pg17fdkz",
  "supportedConnectionTypes": ["websocket", "long-polling", "callback-polling"],
  "advice": {
    "interval": 0,
    "timeout": 30000,
    "reconnect": "retry"
  },
  "channel": "/meta/handshake",
  "id": "1",
  "version": "1.0",
  "successful": true
}]
```

#### Step 3: Client Connect
```json
[{
  "id": "2",
  "channel": "/meta/connect",
  "connectionType": "websocket",
  "advice": {"timeout": 0},
  "clientId": "flvzz5qggsxzvsnlq1u152pg17fdkz",
  "ext": {
    "ack": 0,
    "timesync": {
      "tc": 1761479379795,
      "l": 0,
      "o": 0
    }
  }
}]
```

### Login Sequence

#### Step 1: Login Request
```json
[{
  "id": "3",
  "channel": "/service/controller",
  "data": {
    "type": "login",
    "gameid": "4810301",
    "host": "kahoot.it",
    "name": "PlayerName",
    "content": "{\"device\": {\"userAgent\": \"Mozilla/5.0...\", \"screen\": {\"width\": 1920, \"height\": 1080}}}"
  },
  "clientId": "flvzz5qggsxzvsnlq1u152pg17fdkz",
  "ext": {}
}]
```

#### Step 2: Connect with ACK 1
```json
[{
  "id": "4",
  "channel": "/meta/connect",
  "connectionType": "websocket",
  "advice": {"timeout": 0},
  "clientId": "flvzz5qggsxzvsnlq1u152pg17fdkz",
  "ext": {
    "ack": 1,
    "timesync": {
      "tc": 1761479379832,
      "l": 0,
      "o": 0
    }
  }
}]
```

#### Step 3: Message (usingNamerator)
```json
[{
  "id": "5",
  "channel": "/service/controller",
  "data": {
    "gameid": "4810301",
    "type": "message",
    "host": "kahoot.it",
    "id": 16,
    "content": "{\"usingNamerator\": false}"
  },
  "clientId": "flvzz5qggsxzvsnlq1u152pg17fdkz",
  "ext": {}
}]
```

#### Step 4: Connect with ACK 2
```json
[{
  "id": "6",
  "channel": "/meta/connect",
  "connectionType": "websocket",
  "advice": {"timeout": 0},
  "clientId": "flvzz5qggsxzvsnlq1u152pg17fdkz",
  "ext": {
    "ack": 2,
    "timesync": {
      "tc": 1761479379872,
      "l": 0,
      "o": 0
    }
  }
}]
```

#### Step 5: Points Initialization
```json
[{
  "id": "7",
  "channel": "/service/controller",
  "data": {
    "gameid": "4810301",
    "type": "message",
    "host": "kahoot.it",
    "id": 61,
    "content": "{\"points\": 0}"
  },
  "clientId": "flvzz5qggsxzvsnlq1u152pg17fdkz",
  "ext": {}
}]
```

---

## Game Events

### Event Detection
All game events come through `/service/player` channel:

```json
{
  "ext": {"timetrack": 1761480438594},
  "data": {
    "gameid": "4810301",
    "id": 2,
    "type": "message",
    "content": "JSON_STRING",
    "cid": "452901403"
  },
  "channel": "/service/player"
}
```

### Question Types

#### Multiple Select Quiz
```json
{
  "gameBlockIndex": 4,
  "totalGameBlockCount": 11,
  "extensiveMode": false,
  "type": "multiple_select_quiz",
  "timeRemaining": 44996,
  "timeAvailable": 45000,
  "numberOfAnswersAllowed": 1,
  "currentQuestionAnswerCount": 0,
  "numberOfChoices": 6
}
```

#### True/False Question
```json
{
  "gameBlockIndex": 6,
  "totalGameBlockCount": 11,
  "layout": "TRUE_FALSE",
  "extensiveMode": false,
  "type": "quiz",
  "timeRemaining": 29997,
  "timeAvailable": 30000,
  "numberOfAnswersAllowed": 1,
  "currentQuestionAnswerCount": 0,
  "numberOfChoices": 2
}
```

#### Regular Quiz
```json
{
  "gameBlockIndex": 1,
  "totalGameBlockCount": 11,
  "extensiveMode": false,
  "type": "quiz",
  "timeRemaining": 19998,
  "timeAvailable": 20000,
  "numberOfAnswersAllowed": 1,
  "currentQuestionAnswerCount": 0,
  "numberOfChoices": 4
}
```

#### Content Slide
```json
{
  "gameBlockIndex": 2,
  "totalGameBlockCount": 11,
  "type": "content",
  "timeRemaining": 14999,
  "timeAvailable": 15000
}
```

### Game Start Event
```json
{
  "type": "startQuiz",
  "quizName": "Science Quiz",
  "numberOfQuestions": 10,
  "quizType": "quiz",
  "gameMode": "classic"
}
```

### Leaderboard Event
```json
{
  "type": "leaderboard",
  "leaderboard": [
    {"name": "Player1", "score": 1000, "isHost": false},
    {"name": "Player2", "score": 800, "isHost": false}
  ]
}
```

---

## Answer System

### Answer Packet Structure

#### Single Answer (Quiz/TrueFalse)
```json
[{
  "id": "8",
  "channel": "/service/controller",
  "data": {
    "gameid": "4810301",
    "type": "message",
    "host": "kahoot.it",
    "id": 45,
    "content": "{\"choice\": 2, \"questionIndex\": 4}"
  },
  "clientId": "flvzz5qggsxzvsnlq1u152pg17fdkz",
  "ext": {}
}]
```

#### Multiple Select Answer
```json
[{
  "id": "8",
  "channel": "/service/controller",
  "data": {
    "gameid": "4810301",
    "type": "message",
    "host": "kahoot.it",
    "id": 6,
    "content": "{\"type\": \"multiple_select_quiz\", \"choice\": [0, 2], \"questionIndex\": 4}"
  },
  "clientId": "flvzz5qggsxzvsnlq1u152pg17fdkz",
  "ext": {}
}]
```

### Answer Parameters

#### Single Choice
- `choice`: Integer from 0 to (numberOfChoices - 1)
- `questionIndex`: Current question index (0-based)

#### Multiple Choice
- `choice`: Array of integers (e.g., [0, 2, 4])
- `type`: Always "multiple_select_quiz"
- `questionIndex`: Current question index (0-based)

### Message IDs
- `16`: usingNamerator false
- `45`: Regular answer submission
- `61`: Points initialization
- `6`: Multiple select answer

---

## Heartbeat System

### Heartbeat Packet
```json
[{
  "id": "9",
  "channel": "/meta/connect",
  "connectionType": "websocket",
  "clientId": "flvzz5qggsxzvsnlq1u152pg17fdkz",
  "ext": {
    "ack": 3,
    "timesync": {
      "tc": 1761479379875,
      "l": 0,
      "o": 0
    }
  }
}]
```

### Heartbeat Interval
- Send every 10 seconds
- Increment `ack` value by 1 each time
- Server responds with acknowledgment

---

## Error Handling

### Common Errors

#### Duplicate Name
```json
{
  "description": "Duplicate name",
  "type": "loginResponse", 
  "error": "USER_INPUT"
}
```

#### Game Not Found
```json
{
  "error": "NotFoundError",
  "message": "Game not found"
}
```

#### Game Full
```json
{
  "error": "GameFullError",
  "message": "Game is full"
}
```

---

## Complete Flow Example

### 1. Get Session
```python
import httpx
import time

game_pin = "4810301"
url = f"https://kahoot.it/reserve/session/{game_pin}/?{int(time.time() * 1000)}"
response = httpx.get(url)

session_token = response.headers['x-kahoot-session-token']
challenge = response.json()['challenge']
```

### 2. Decrypt Token
```python
decrypted_token = decrypt_session_token(session_token, challenge)
```

### 3. Connect WebSocket
```python
import websockets
import json

ws_url = f"wss://kahoot.it/cometd/{game_pin}/{decrypted_token}"
async with websockets.connect(ws_url) as websocket:
    # Handshake and login sequence...
```

### 4. Handle Game Events
```python
while True:
    message = await websocket.recv()
    packet = json.loads(message)
    
    if packet[0]['channel'] == '/service/player':
        data = packet[0]['data']
        content = json.loads(data['content'])
        
        if content.get('type') == 'multiple_select_quiz':
            # Handle multiple select question
            await send_multiple_select_answer(websocket, [0, 2], content['gameBlockIndex'])
        
        elif content.get('type') == 'quiz':
            if content.get('layout') == 'TRUE_FALSE':
                # Handle true/false question
                await send_single_answer(websocket, 0, content['gameBlockIndex'])
            else:
                # Handle regular question
                await send_single_answer(websocket, 1, content['gameBlockIndex'])
```