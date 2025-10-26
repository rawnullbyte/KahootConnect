## Kahoot Protocol
Huge Shoutouts to msemple1111 and his protocol information [here](https://github.com/msemple1111/kahoot-hack/tree/master/kahoot-protocol) that supplied a lot of information for this

**Terms to Know**

__Epoch__: Unit of Time used by Unix - counts time from January 1st 1970 to current time in seconds [(converter)](https://www.epochconverter.com/ "Converter")
***
**Handshake**
Requests Returns Service Token
GET: `https://kahoot.it/reserve/session/*pin*/?*time`

| Parameter       | Purpose                  |
|-----------------|--------------------------|
| Pin             | Game Pin of Game         |
| Time            | Time of request in Epoch |

Proper Response: Empty JSON with Header `x-kahoot-session-token`
Bad Response: Response body String: `Not found`

Move on if you get a Proper Response
***
**Game Register Ping**
Kahoot and Browser websocket contact
GET: `https://kahoot.it/cometd/*pin*/*session-token*`

| Parameter       | Purpose                      |
|-----------------|------------------------------|
| Pin             | Game Pin of Game             |
| Session-Token   | Session Token from Handshake |

Proper Response: 400 Code with some HTML

Move on if you get a proper response
***
**Registration Process**
__Beginning Registration Process__
POST: `POST https://kahoot.it/cometd/*pin*/*session-token*/handshake`

| Parameter       | Purpose                      |
|-----------------|------------------------------|
| Pin             | Game Pin of Game             |
| Session-Token   | Session Token from Handshake |

__What to Post__
Example Post: 
```
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
```

__Breaking it Down__

* Advice

*Telling Kahoot when to drop the browser on non-responsiveness*

| Parameter       | Purpose                                |
|-----------------|----------------------------------------|
| Interval        | Intervals of Checks                    |
| Timeout         | Length of time before dropping browser |

* Channel
Channel Value tells what you want to do. All Possible Channels:
* _/meta/handshake_
  * Basic Handshake Channel
* _/meta/subscribe_
* _/meta/connect_
* _/meta/unsubscribe_

* Ext

*Used to sync time with Kahoot server and client*

| Parameter       | Purpose                                                             |
|-----------------|---------------------------------------------------------------------|
| l               | Network Lag - Client Calculated                                     |
| o               | Clock Offset that the client has calculated                         |
| tc              | Client Timestamp in ms since 1970 (epoch) when the message was sent |

* Id

*Connection value attempt to `/cometd` The First connection is 1, runs on increments of 1*

* Minimum Version

*Negotiates Protocol Version, can just leave as default*

***
[Example Login WebSocket Information](http://ryguy.us/share/44143a69.mp4)

**Later Information for Additions**

_*Services*_
* _/service/controller_
* _/service/player_
* _/service/status_
