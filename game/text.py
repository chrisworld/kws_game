"""
character class
"""

import pygame

from color_bag import ColorBag
from interactable import Interactable


class Text(Interactable):
  """
  character class
  """

  def __init__(self, screen, color_bag):

    # vars
    self.screen = screen
    self.color_bag = color_bag

    # init font
    pygame.font.init()

    # fonts
    self.big_font = pygame.font.SysFont('Courier', 40)
    self.small_font = pygame.font.SysFont('Courier', 20)

    # messages
    self.big_msg = None
    self.small_msg = None

    # positions
    self.big_pos = None
    self.small_pos = None


  def win_message(self, big_pos=(200, 100), small_pos=(200, 150)):
    """
    write winn message
    """

    self.big_msg = self.big_font.render('Win', True, self.color_bag.win)
    self.small_msg = self.small_font.render('press Enter', True, self.color_bag.win)
    self.big_pos = big_pos
    self.small_pos = small_pos


  def reset(self):
    """
    reset message
    """

    self.big_msg = None
    self.small_msg = None


  def update(self):
    """
    update texts on screen
    """

    if self.big_msg is not None:
      self.screen.blit(self.big_msg, self.big_pos)

    if self.small_msg is not None:
      self.screen.blit(self.small_msg, self.small_pos)


if __name__ == '__main__':
  """
  test character
  """

  from game_logic import GameLogic
  
  # size of display
  screen_size = width, height = 640, 480

  # collection of game colors
  color_bag = ColorBag()

  # init pygame
  pygame.init()

  # init display
  screen = pygame.display.set_mode(screen_size)

  # text module
  text = Text(screen, color_bag)
  text.win_message()
 

  # game logic
  game_logic = GameLogic()

  # add clock
  clock = pygame.time.Clock()

  # game loop
  while game_logic.run_loop:
    for event in pygame.event.get():

      # input handling
      game_logic.event_update(event)

    # frame update
    game_logic.update()

    # fill screen
    screen.fill(color_bag.background)

    # text update
    text.update()

    # update display
    pygame.display.flip()

    # reduce framerate
    clock.tick(60)


  # end pygame
  pygame.quit()




