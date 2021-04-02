import urllib
import time
import re
import base64
import math
import requests
import urllib
import asyncio
import json as JSON
from user_agent import generate_user_agent as UserAgent
from errors import *

loop = asyncio.get_event_loop()

async def requestChallenge(pin,client):
    options = {
        "headers": {
            "User-Agent": UserAgent(),
            "Origin": "kahoot.it",
            "Referer": "https://kahoot.it",
            "Accept-Language": "en-US,en;q=0.8",
            "Accept": "*/*"
        },
        "host": "kahoot.it",
        "protocol": "https:",
        "path": f"/rest/challenges/pin/{pin}"
    }
    url = (options.get("protocol") or "https:") + "//" + (options.get("host") or "kahoot.it") + (options.get("port") or "") + options.get("path")
    r = requests.request(options.get("method") or "GET",url,headers=options.get("headers"))
    try:
        data = r.json()
        out = {
            "data": {
                "isChallenge": True,
                "twoFactorAuth": False,
                "kahootData": data.get("kahoot"),
                "rawChallengeData": data["challenge"]
            }
        }
        out["data"].update(data["challenge"]["game_options"])
        return out
    except Exception as e:
        raise e

async def requestToken(pin,client):
    options = {
        "headers": {
            "User-Agent": UserAgent(),
            "Origin": "kahoot.it",
            "Referer": "https://kahoot.it",
            "Accept-Language": "en-US,en;q=0.8",
            "Accept": "*/*"
        },
        "host": "kahoot.it",
        "protocol": "https:",
        "path": f"/reserve/session/{pin}/?{int(time.time() * 1000)}"
    }
    url = (options.get("protocol") or "https:") + "//" + (options.get("host") or "kahoot.it") + (options.get("port") or "") + options.get("path")
    r = requests.request(options.get("method") or "GET",url,headers=options.get("headers"))
    if not r.headers.get("x-kahoot-session-token"):
        raise InvalidPINException("Invalid PIN")
    try:
        data = r.json()
        token = r.headers.get("x-kahoot-session-token")
        token = decodeBase64(token)
        return {
            "token": token,
            "data": data
        }
    except Exception as e:
        raise e

def solveChallenge(challenge):
    # src: https://github.com/msemple1111/kahoot-hack/blob/master/main.py
    s1 = challenge.find('this,') + 7
    s2 = challenge.find("');")
    message = challenge[s1:s2]
    s1 = challenge.find('var offset') + 13
    s2 = challenge.find('; if')
    offset = str("".join(challenge[s1:s2].split()))
    offset = eval(offset)
    def repl(char, position):
        return chr((((ord(char)*position) + offset)% 77)+ 48)
    res = ""
    for i in range(0,len(message)):
        res+=repl(message[i],i)
    return res

# Decode the token header
def decodeBase64(base):
    try:
        base += "=" * ((4 - len(base) % 4) % 4)
        return base64.b64decode(base).decode("utf-8")
    except Exception as e:
        return e
# complex stuff to get the actual token
def concatTokens(headerToken,challengeToken):
    token = ""
    for i in range(0,len(headerToken)):
        char = ord(headerToken[i])
        mod = ord(challengeToken[i % len(challengeToken)])
        decodedChar = char ^ mod
        token += chr(decodedChar)
    return token

async def resolve(pin,client):
    if math.isnan(int(pin)):
        raise InvalidPINException("Non-numberical PIN")
    if str(pin)[0] == "0":
        return requestChallenge(pin,client)
    data = await requestToken(pin,client)
    token2 = solveChallenge(data["data"]["challenge"])
    token = concatTokens(data["token"],token2)
    return {
        "token": token,
        "data": data["data"]
    }
