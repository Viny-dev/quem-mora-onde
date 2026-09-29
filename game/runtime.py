from game.engine import GameEngine


# Instância única e compartilhada do jogo.
# API, NFC Manager e futuramente outros módulos
# utilizam exatamente este mesmo GameEngine.
game = GameEngine()