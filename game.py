from threading import Thread
import time

class Game(Thread):
    countdown = 5
    started = False
    players = []
    def __init__(self):
        Thread.__init__(self)

    def startGame(self, players):
        for p in players:
            p['play'] = -1
        self.players = players
        self.start()
    
    def send(self, msg):
        for p in self.players:
            p['connection'].send(bytes(msg, "utf-8"))
    
    def allPlayed(self):
        return len(self.players) == len(list(filter(lambda p: p['play'] >= 0, self.players)))

    def run(self):
        for i in reversed(range(1,1+self.countdown)):
            time.sleep(1)
            self.send("starting in %s seconds" % str(i))
        while not self.allPlayed():
            pass

        guesses  = set([p['play'] for p in self.players])
        if len(guesses) in [1,3]:
            self.send("You're all losers")
        else:
            [a,b] = guesses
            winner = a if ((a + 1) % 3 == b) else b
            winners = list(filter(lambda p: p['play'] == winner, self.players))
            winnerNames = [p['username'] for p in winners]
            if len(winners) == 1:
                self.send("Your winner is " % next(winnerNames))
            else:
                self.send("Your winners are %s" % ", ".join(winnerNames))
        self.send("Press Ready to play again")



        