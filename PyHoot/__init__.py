import time, asyncio, importlib, ssl, json, inspect
from pymitter import EventEmitter
from aiocometd import Client
from numbers import Number
from .src.util.token import resolve
from user_agent import generate_user_agent as UserAgent

class KahootClient(EventEmitter):
    def __init__(self):
        super().__init__()
        self.classes = {}
        self.connected = False
        self.data = {}
        self.gameid = None
        self.handlers = {}
        self.loggingMode = False
        self.name = None
        self.reconnectRecovery = None
        self.settings = {}
        self.socket = None
        self.twoFactorResetTime = None
        self.userAgent = UserAgent()
        self.quiz = {}
        for module in ("answer","backup","extraData","feedback","gameReset","main","nameAccept","podium","questionEnd","questionReady","questionStart","quizEnd","quizStart","teamAccept","teamTalk","timeOver"):
            f = getattr(importlib.import_module(f".src.modules.{module}","KahootPY"),"main")
            f(self)
    async def join(self,pin,name=None,team=["Player 1","Player 2","Player 3","Player 4"]):
        self.name = name
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        async def go():
            self.gameid = pin
            data = await resolve(self.gameid,self)
            self.settings.update(data["data"])
            token = data["token"]
            client = Client(f"wss://kahoot.it/cometd/{self.gameid}/{token}")
            self.socket = client
            await client.open()
            await client.subscribe("/service/controller")
            await client.subscribe("/service/status")
            await client.subscribe("/service/player")
            await self._send(self.classes["LiveJoinPacket"](self,name))
            async for message in client:
                # Handle messages
                self._message(message)
            await client.close()
        loop.create_task(go())
        return await future
    def _message(self,message):
        if self.loggingMode:
            d = json.dumps(message)
            print(f"RECV: {d}")
        for i in self.handlers:
            if inspect.iscoroutinefunction(self.handlers[i]):
                loop = asyncio.get_event_loop()
                loop.create_task(self.handlers[i](message))
            else:
                self.handlers[i](message)
    async def _send(self,message,callback=None):
        if self.loggingMode:
            d = json.dumps(message)
            print(f"SEND: {d}")
        if self.socket and not self.socket.closed:
            success = True
            try:
                c = message["channel"]
                m = message.get("data")
                await self.socket.publish(c,m)
            except Exception as e:
                success = False
            if not callable(callback):
                return
            if success:
                callback(True)
            else:
                callback(False)
    async def leave(self,safe=False):
        await self._send(self.classes["LiveLeavePacket"](self))
    def _emit(self,evt,payload=None):
        if not self.quiz:
            self.quiz = {}
        if payload and payload.get("quizQuestionAnswers"):
            self.quiz["quizQuestionAnswers"] = payload["quizQuestionAnswers"]
        if payload and not payload.get("questionIndex") is None:
            if not self.quiz.get("currentQuestion"):
                self.quiz["currentQuestion"] = {}
            self.quiz["currentQuestion"].update(payload)
        if not self.connected:
            self.lastEvent = (evt,payload)
        else:
            self.emit(evt,payload)
