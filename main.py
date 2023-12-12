import sys
import pygame
from src.game.game import Game
# from src.gan.generate import generate_levels

if __name__ == "__main__":
  # Uncomment the following lines when you are ready to use the GAN-generated levels
  # print("Generating levels with GAN...")
  # generate_levels()
  # print("Levels generated successfully.")

  print("Running the game...")
  
  # Initialize Pygame
  pygame.init()

  # Get runtime type (0 for human, 1 for agent)
  run_type = sys.argv[1]

  # Set up the game
  game = Game(run_type)
  # game.initialize()

  # Run the game loop
  while game.is_running:
    game.handle_events()
    game.update()
    game.render()

  # Clean up Pygame
  pygame.quit()
  # print("Final score: " + str(int(game.score)))