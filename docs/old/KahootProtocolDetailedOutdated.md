This handshake is based on the long-polling method rather than WebSockets.

1. Handshake Request for Session Token

The first step is to request a session token:

GET https://kahoot.it/reserve/session/{pin}/?{time}

Parameters:

{pin}: The game pin

{time}: The current time in epoch format



Response:

If the game exists, the server responds with a session token in the header and an empty JSON body:

Header:

x-kahoot-session-token: 885ba1bd52520b9f3c3d7fdc41f55113cc1c8fcfe830a3a01e382b8252dd9dcdaec9b5fb3c2619cf582b22e8a49e4b90

Body:

{}


If the game pin does not exist, the response body contains:

Not found

2. Send a Ping to Register

Next, send a ping to register:

GET https://kahoot.it/cometd/{pin}/{session-token}

Parameters:

{pin}: The game pin

{session-token}: The session token from the first handshake request



Expected Response:

This request attempts to upgrade to WebSockets, and it should respond with:

HTTP/1.1 400 Bad Request

(The body will contain some HTML code.)

3. Start Registration Process

Now, initiate the registration process:

POST https://kahoot.it/cometd/{pin}/{session-token}/handshake

Parameters:

{pin}: The game pin

{session-token}: The session token from the first handshake request



Example Request Body:

[
  {
    "advice": {
      "interval": 0,
      "timeout": 60000
    },
    "channel": "/meta/handshake",
    "ext": {
      "ack": true,
      "timesync": {
        "l": 0,
        "o": 0,
        "tc": 1477400825756
      }
    },
    "id": "2",
    "minimumVersion": "1.0",
    "supportedConnectionTypes": [
      "long-polling"
    ],
    "version": "1.0"
  }
]

Breakdown of the Request:

"advice":

interval: 0

timeout: 60000


This informs Kahoot when to drop the connection if there’s no response. Keeping the default is advisable.

"channel":

Value: "/meta/handshake"


This indicates the purpose of the request, which is to perform a handshake.

"ext":

ack: true

timesync:

l: 0 (network lag)

o: 0 (clock offset)

tc: 1477400825756 (client timestamp in ms since 1970)



"id":

Value: "2" (incremental connection attempt)


"minimumVersion": "1.0"

"supportedConnectionTypes":

["long-polling"]

"version": "1.0"


These values ensure protocol version negotiation is handled appropriately.
