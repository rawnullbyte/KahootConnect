This handshake is based upon the long-polling method rather than web
sockets  
  
  
1. A handshake request asks for a session token:  
\>\>\> GET https://kahoot.it/reserve/session/\*pin\*/?\*time  
where \*pin\* is the game pin and \*time\* is the time in epoch  
  
If the game exists, it responds with a session token in the header
called "x-kahoot-session-token"  
x-kahoot-session-token:
885ba1bd52520b9f3c3d7fdc41f55113cc1c8fcfe830a3a01e382b8252dd9dcdaec9b5fb3c2619cf582b22e8a49e4b90  
  
and in the body, an empty JSON response  
{}  
  
If the game pin entered does not exist, no cookie is sent and the
Response body contains a string:  
Not found  
  
  
  
2. Send a ping to kahoot saying we want to register:  
\>\>\> GET https://kahoot.it/cometd/\*pin\*/\*session-token\*  
Where \*pin\* is the game pin and \*session-token\* is the session token
from the first handshake request  
  
This request is kahoot/browser trying to upgrade to websockets.  
It should respond with code 400 and some html code. We can now move onto
the next request.  
  
  
  
3.  
\>\>\> POST
https://kahoot.it/cometd/\*pin\*/\*session-token\*/handshake  
Where \*pin\* is the game pin and \*session-token\* is the session token
from the first handshake request  
  
This is the start of the registration process. We are sending our time
in epoch, version and some more parameter.  
  
This is an example request.  
  
\[  
{  
\"advice\": {  
\"interval\": 0,  
\"timeout\": 60000  
},  
\"channel\": \"/meta/handshake\",  
\"ext\": {  
\"ack\": true,  
\"timesync\": {  
\"l\": 0,  
\"o\": 0,  
\"tc\": 1477400825756  
}  
},  
\"id\": \"2\",  
\"minimumVersion\": \"1.0\",  
\"supportedConnectionTypes\": \[  
\"long-polling\"  
\],  
\"version\": \"1.0\"  
}  
\]  
  
Breaking it down:  
  
  
\"advice\": {  
\"interval\": 0,  
\"timeout\": 60000  
}  
This is the browser telling kahoot when to drop the connection if the
browser does not respond. It is best just to keep this default.  
  
  
\"channel\": \"/meta/handshake\"  
This is a key part of the payload. The channel value is basically what
you want to do. So in this case we are only doing a handshake.  
  
  
\"ext\": {  
\"ack\": true,  
\"timesync\": {  
\"l\": 0,  
\"o\": 0,  
\"tc\": 1477400825756  
}  
}  
The ext dictionary is for time syncing the server and client. tc is the
client timestamp in ms since 1970 of when the message was sent. l is the
network lag that the client has calculated. o is the clock offset that
the client has calculated.  
  
  
\"id\": \"2\",  
The id value is connection attempt to /cometd/. The first connection
is 1. It is incremental.  
  
\"minimumVersion\": \"1.0\",  
\"supportedConnectionTypes\": \[  
\"long-polling\"  
\],  
\"version\": \"1.0\"  
Leave this the same. It is to do with protocol version negotiation. We
don't need to do anything with this really.  
  
  
  
  
  
  
  
