from kahoot import client
pin = 473403
bot = client()
# bot.loggingMode = True
bot.join(pin,"KahootPY",["a","b","c"])
def joined():
    print("joined")
bot.on("ready",joined)
def badname():
    print("invalid name")
    bot.leave()
bot.on("invalidName",badname)
def answer(q):
    print("Question started. Answering '0'")
    q.answer(0)
bot.on("questionStart",answer)
def qs(q):
    print("Quiz Started: " + q.name)
bot.on("quiz",qs)
def question(q):
    print("Question of type " + q.type + " got!")
bot.on("question",question)
def rank(qe):
    print("Question Ended. In rank " + qe.rank + " with " + qe.total + " points.")
bot.on("questionEnd",rank)
def end():
    print("disconnected")
bot.on("disconnect",end)
def sub():
    print("answer submitted")
bot.on("questionSubmit",sub)
def finishtext(fin):
    print("finished with " + fin.metal + " medal")
bot.on("finishText",finishtext)
def done(dat):
    print("quiz finished")
    print(dat)
bot.on("finish",done)
