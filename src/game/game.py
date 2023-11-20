import pygame


class Game:
  def __init__(self, w=640, h=480):
    self.w = w
    self.h = h
    self.screen = pygame.display.set_mode((self.w, self.h))
    pygame.display.set_caption("GAN Game")



  #TODO Complete other functions