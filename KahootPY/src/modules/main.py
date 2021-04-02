from ..assets.LiveJoinPacket import LiveJoinPacket
from ..assets.LiveJoinTeamPacket import LiveJoinTeamPacket
from ..assets.LiveTwoStepAnswer import LiveTwoStepAnswer
from ..assets.LiveLeavePacket import LiveLeavePacket
import asyncio
import time
import math
import json

def main(self):
    self.classes["LiveTwoStepAnswer"] = LiveTwoStepAnswer
    self.classes["LiveJoinPacket"] = LiveJoinPacket
    self.classes["LiveJoinTeamPacket"] = LiveJoinTeamPacket
    self.classes["LiveLeavePacket"] = LiveLeavePacket
    def TwoFactor(message):
        if message["channel"] == "/service/player" and message.get("data") and not self.connected:
            if message["data"].get("id") == 53:
                self.twoFactorResetTime = int(time.time() * 1000)
                self.emit("TwoFactorReset")
            elif message["data"].get("id") == 51:
                self.emit("TwoFactorWrong")
            elif message["data"].get("id") == 52:
                self.connected = True
                self.emit("TwoFactorCorrect")
                if self.lastEvent:
                    self.emit(self.lastEvent[0],self.lastEvent[1])
                self.lastEvent = None
                self.twoFactorResetTime = None
    self.handlers["TwoFactor"] = TwoFactor

    async def Join(message):
        if message["channel"] == "/service/status":
            self.emit("status",message["data"])
            if message["data"]["status"] == "LOCKED":
                self.disconnectReason = "Game Locked"
                await self.leave(True)
                return
            self.disconnectReason = message.get("description")
            await self.leave(True)
        elif message["channel"] == "/service/controller" and message.get("data") and message["data"].get("type") == "loginResponse":
            if message["data"].get("error"):
                if str(message["data"].get("description")).lower() != "duplicate name":
                    self.disconnectReason = message.get("description")
                    await self.leave(True)
            else:
                self.cid = message["data"]["cid"]
                if self.settings.get("gameMode") == "team":
                    await asyncio.sleep(1)
                    if team != False:
                        try:
                            await self.joinTeam(team,True)
                        except Exception:
                            pass
                        self.emit("Joined")
                        if not self.settings["twoFactorAuth"]:
                            self.connected = True
                        else:
                            self.emit("TwoFactorReset")
                    else:
                        self.emit("Joined")
                        if self.settings["twoFactorAuth"]:
                            self.emit("TwoFactorReset")
                else:
                    self.emit("Joined")
                    if not self.settings["twoFactorAuth"]:
                        self.connected = True
                    else:
                        self.emit("TwoFactorReset")
    self.handlers["Join"] = Join

    def Disconnect(message):
        if message["channel"] == "/service/player" and message.get("data") and message["data"].get("id") == 10:
            content = json.loads(message["data"]["content"])
            if content.get("kickCode"):
                self.disconnectReason = "Kicked"
            else:
                self.disconnectReason = "Session Ended"
            loop = asyncio.get_event_loop()
            loop.create_task(self.leave(True))
    self.handlers["Disconnect"] = Disconnect
