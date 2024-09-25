# Kahoot WebSocket API Documentation

## Overview

This guide details how to connect to the Kahoot WebSocket server, including how to send requests, receive responses, calculate essential parameters like `connToken`, and send messages during gameplay.

## Table of Contents
1. [Session Reservation](#1-session-reservation)
2. [Calculate `connToken`](#2-calculate-conntoken)
3. [Connect to the WebSocket Server](#3-connect-to-the-websocket-server)
4. [Send Handshake Request](#4-send-handshake-request)
5. [Handle Handshake Response](#5-handle-handshake-response)
6. [Login to the Game](#6-login-to-the-game)
7. [Send Login Data](#7-send-login-data)
8. [Maintain Connection with Heartbeat](#8-maintain-connection-with-heartbeat)

---

## 1. Session Reservation

### Step 1: Reserve a Session

To join a Kahoot game, you need to reserve a session using an HTTP GET request.

- **Request:**
  - **Method:** GET
  - **URL:** `https://kahoot.it/reserve/session/{game_pin}/?{timestamp}`
    - **Parameters:**
      - `{game_pin}`: The actual game PIN (e.g., `123456`).
      - `{timestamp}`: Current time in milliseconds since the Unix epoch.

- **Example Request:**
  ```
  GET https://kahoot.it/reserve/session/123456/?1695632636000
  ```

### Step 2: Parse the Response

You will receive a response containing crucial data.

- **Response Structure:**
  - **Headers:**
    - `x-kahoot-session-token`: Your session token.
  - **Body (JSON):**
    - `challenge`: A string used to calculate the `connToken`.

- **Example Response:**
  ```
  {
      "challenge": "decode.call(this,'example_encoded_string')"
  }
  ```

### Step 3: Extract Information

From the response:
- **Session Token:** Extract from the response headers.
- **Session Challenge:** Extract from the JSON body.

---

## 2. Calculate `connToken`

To establish a connection to the WebSocket server, you need to calculate `connToken` using the session token and the session challenge.

### Step 1: Decode the Session Challenge

1. **Extract Message and Offset:**
   - Use regular expressions to extract the encoded message and the offset calculation from the session challenge string.

   **Example Session Challenge:**
   ```
   decode.call(this,'example_encoded_string')
   offset = (some_value);
   ```

   - **Extracted Message:** `example_encoded_string`
   - **Extracted Offset:** The offset calculation in a format that can be evaluated (e.g., `2 * 5 + 3`).

### Step 2: Perform Calculations

1. **Calculate Offset Value:**
   - Evaluate the offset expression to get a numerical value. For example, if the offset is `2 * 5 + 3`, the result is `13`.

   ```
   offset_value = eval("2 * 5 + 3")  # Result is 13
   ```

2. **XOR Calculation:**
   - Use a method to perform an XOR operation between two strings.
   - The `example_encoded_string` will be decoded from Base64.

   **Example Steps:**
   - **Base64 Decode the Session Token:**
     ```
     import base64
     session_token = "<base64_encoded_token>"
     decoded_token = base64.b64decode(session_token).decode('utf-8')
     ```

   - **Perform XOR Operation:**
     Create an XOR function:
     ```
     def xor_string(string1, string2):
         return ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(string1, string2))
     ```

   - **Calculate `connToken`:**
     ```
     connToken = xor_string(decoded_token, generated_string)
     ```

3. **Example of XOR Calculation:**
   - If `decoded_token` is "token" and the generated string from the previous steps is "key":
   ```
   connToken = xor_string("token", "key")
   # Perform the XOR operation character by character.
   ```

### Step 3: Resulting `connToken`

After performing the calculations, you will get your `connToken`, which will be used for the WebSocket connection.

---

## 3. Connect to the WebSocket Server

### Step 1: Establish Connection

Once you have your `connToken`, you can connect to the Kahoot WebSocket server.

- **WebSocket URL:**
  ```
  wss://kahoot.it/cometd/{game_pin}/{connToken}
  ```

- **Example Connection:**
  ```
  wss://kahoot.it/cometd/123456/your_calculated_connToken
  ```

---

## 4. Send Handshake Request

Upon establishing a connection, send a handshake message to the server.

- **Message Structure:**
  ```
  {
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
              "tc": <current_timestamp>,
              "l": 0,
              "o": 0
          }
      }
  }
  ```

---

## 5. Handle Handshake Response

After sending the handshake message, the server will respond with a confirmation.

- **Response Structure:**
  - Contains a `clientId`, which is necessary for subsequent requests.

- **Example Response:**
  ```
  [
      {
          "successful": true,
          "clientId": "<your_client_id>",
          "channel": "/meta/handshake"
      }
  ]
  ```

---

## 6. Login to the Game

Now that you are connected, you need to log in to the game.

- **Login Message Structure:**
  ```
  {
      "id": "3",
      "channel": "/service/controller",
      "data": {
          "type": "login",
          "gameid": "<game_pin>",
          "host": "kahoot.it",
          "name": "<your_nickname>",
          "content": {
              "device": {
                  "userAgent": "User-Agent String Here",
                  "screen": {
                      "width": 1920,
                      "height": 1080
                  }
              }
          }
      },
      "clientId": "<your_client_id>",
      "ext": {}
  }
  ```

### Step 7: Send Login Data

The following message is part of the login process and should be sent right after sending the login message to provide additional context about your connection.

- **Content Structure:**
  ```
  {
      "id": "4",
      "channel": "/service/controller",
      "data": {
          "type": "message",
          "gameid": "<game_pin>",
          "host": "kahoot.it",
          "content": "{\"points\":0}"
      },
      "clientId": "<your_client_id>",
      "ext": {}
  }
  ```

---

## 8. Maintain Connection with Heartbeat

To keep the connection alive, periodically send heartbeat messages.

### Step 1: Send Heartbeat Message

- **Heartbeat Message Structure:**
  ```
  {
      "id": "<incremented_id>",
      "channel": "/meta/connect",
      "connectionType": "websocket",
      "clientId": "<your_client_id>",
      "ext": {
          "ack": <ack_number>,
          "timesync": {
              "tc": <current_timestamp>,
              "l": 0,
              "o": 0
          }
      }
  }
  ```

### Step 2: Sending Frequency

- Send the heartbeat message every 10 seconds to maintain the connection.

---

## Conclusion

This documentation provides a detailed guide on how to connect to the Kahoot WebSocket server, calculate `connToken`, and manage your connection effectively. Follow each step carefully to ensure successful interaction with the Kahoot platform.
