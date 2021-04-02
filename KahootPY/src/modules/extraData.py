def main(self):
    self.data["totalScore"] = 0
    self.data["streak"] = 0
    self.data["rank"] = 1
    def GameResetHandler():
        self.data["totalScore"] = 0
        self.data["rank"] = 0
        self.data["streak"] = 0
        self.quiz = {}
    self.on("GameReset",GameResetHandler)
    def QuestionStartHandler(event):
        event.update({
            "type": event["type"],
            "index": event["questionIndex"]
        })
    self.on("QuestionStart",QuestionStartHandler)
    def QuizStartHandler(event):
        event.update({
            "questionCount": len(self.quiz["quizQuestionAnswers"])
        })
        try:
            self.quiz.update(event)
        except Exception:
            pass
    self.on("QuizStart",QuizStartHandler)
    def QuestionReadyHandler(event):
        event.update({
            "type": event["gameBlockType"],
            "index": event["questionIndex"]
        })
        try:
            self.quiz["currentQuestion"].update(event)
        except Exception:
            pass
    self.on("QuestionReady",QuestionReadyHandler)
    def QuestionEndHandler(event):
        self.data["totalScore"] = event["totalScore"]
        self.data["streak"] = event["pointsData"]["answerStreakPoints"]["streakLevel"]
        self.data["rank"] = event["rank"]
    self.on("QuestionEnd",QuestionEndHandler)
