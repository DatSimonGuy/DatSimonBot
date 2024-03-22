import requests
from random import Random

request_url = ""

class ContextoGame:
    def __init__(self, url, game_num, guesses = {}, last_messages = []):
        self.url = url
        self.guesses = guesses or {}
        self.game_num = game_num
        self.last_messages = last_messages or []

    def __str__(self) -> str:
        guesses = "\n".join([f"{k}: {v[0]} {v[1]}" for k, v in list(self.guesses.items())[:15]])
        return f"ContextoGame(number={self.game_num})\nguesses:\n{guesses}"

    def initGame():
        random = Random()
        random_game = random.randint(1, 530)
        global request_url
        request_url = f"https://api.contexto.me/machado/en/game/{random_game}/"
        return ContextoGame(request_url, random_game)
    
    def evaluate(self, word, response):
        try:
            score = int(response.json()['distance'])
        except KeyError:
            raise Exception("Unfunny")
        if score <= 200:
            self.guesses[word] = (f"{score}", "🟢")
        elif score < 1500:
            self.guesses[word] = (f"{score}", "🟡")
        else:
            self.guesses[word] = (f"{score}", "🔴")
        
        return score
    
    def getScore(self, word):
        word = str(word).lower()
        response = requests.get(self.url + word)

        score = self.evaluate(word, response)
            
        self.guesses = dict(sorted(self.guesses.items(), key=lambda x: int(x[1][0])))
        
        if score == 0:
            raise Exception("WON")
        
        return score

    def getHint(self):
        if len(self.guesses) == 0:
            raise Exception("CANT")

        last = int(self.guesses[-1][0])

        if last == 1:
            raise Exception("CANT")

        response = requests.get(self.url + f"tip/{last + 1}")
        word = response.json()['word']

        self.evaluate(word, response)
        
        return word
        
        
        
        