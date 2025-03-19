from Game import Game


game = Game()
game.start()
while game.running:
    game.new()
    game.run()
    game.game_over()

game.quit()