import pygame
import numpy as np
# import movement as mv
import src.utils.levelHelper as lh

class Game:
  def __init__(self):
    # Initialize constants
    self.w = 500
    self.h = 500
    self.playerW = 25
    self.playerH = 25
    self.playerVelocity = 0.2

    # Set up pygame stuff
    self.screen = pygame.display.set_mode((self.w, self.h))
    pygame.display.set_caption("GAN Game")
    self.clock = pygame.time.Clock()

    #TODO Add a configurable level loader
    # Loads map from save file
    self.tileList = np.loadtxt("src\\game\\levels\\testLevel.txt", dtype=int)
    for (row_idx, col_idx), tile in np.ndenumerate(self.tileList):
      if(tile == lh.tileType.START):
        self.playerX = col_idx*25
        self.playerY = row_idx*25
    
    # Marks game as running
    self.is_running = True

  def handle_events(self):
    # Checks for new events
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        self.is_running = False

    self.keys = pygame.key.get_pressed()

    # Sets the FPS
    self.clock.tick(60)

  def update(self):
    # (self.playerX, self.playerY) = mv.update_position(self.playerX, self.playerY, self.keys)

    if(self.keys[pygame.K_w]):
      self.playerY -= 25.0 * self.playerVelocity
      # Very basic boundary check
      if(self.playerY < 0):
        self.playerY = 0

    if(self.keys[pygame.K_s]):
      self.playerY += 25.0 * self.playerVelocity
      # Very basic boundary check
      if(self.playerY > (self.h - self.playerH)):
        self.playerY = (self.h - self.playerH)

    if(self.keys[pygame.K_d]):
      self.playerX += 25.0 * self.playerVelocity
      # Very basic boundary check
      if(self.playerX > (self.w - self.playerW)):
        self.playerX = (self.w - self.playerW)

    if(self.keys[pygame.K_a]):
      self.playerX -= 25.0 * self.playerVelocity
      # Very basic boundary check
      if(self.playerX < 0):
        self.playerX = 0

  def render(self):
    # Draws all of the map tiles
    for (row_idx, col_idx), tile in np.ndenumerate(self.tileList):
      pygame.draw.rect(self.screen, lh.getTileColor(tile), (col_idx*25, row_idx*25, 25, 25))

    # Draws the player
    pygame.draw.rect(self.screen, "pink", (self.playerX, self.playerY, self.playerW, self.playerH))

    #actually renders the updates to the screen
    pygame.display.update()