from .LiveBaseMessage import LiveBaseMessage
import math
import json

class LiveQuestionAnswer(LiveBaseMessage):
    def __init__(self,client,choice):
        question = (client.quiz and client.quiz["currentQuestion"]) or {}
        type = question["gameBlockType"] or "quiz"
        text = None
        if type == "multiple_select_poll" or type == "multiple_select_quiz" or type == "jumble":
            if not isinstance(choice,list):
                if math.isnan(choice):
                    choice = [0,1,2,3]
                else:
                    choice = [int(choice)]
                if type == "jumble" and len(choice) != 4:
                    choice = [0,1,2,3]
        elif type == "word_cloud" or type == "open_ended":
            text = str(choice)
        else:
            if math.isnan(choice):
                choice = 0
            choice = int(choice)
        content = {
            "gameid": client.gameid,
            "host": "kahoot.it",
            "id": 45,
            "type": "message"
        }
        if text:
            content["content"] = json.dumps({
                "text": text,
                "questionIndex": question.get("questionIndex") or 0,
                "meta": {
                    "lag": client._timesync.get("l") or 30
                },
                "type": type
            })
        else:
            content["content"] = json.dumps({
                "choice": choice,
                "questionIndex": question.get("questionIndex") or 0,
                "meta": {
                    "lag": client._timesync.get("l") or 30
                },
                "type": type
            })
        super().__init__("/service/controller",content)
