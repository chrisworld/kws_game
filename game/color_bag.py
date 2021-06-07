"""
color bag class
"""

class ColorBag():
  """
  Input Handler class
  """

  def __init__(self):

    # background
    self.background = (255, 255, 255)

    # ordinary walls
    self.wall = (10, 200, 200)

    # moving walls
    self.active_move_wall = (200, 100, 100)
    self.default_move_wall = (10, 100, 100)

    # text color
    self.text_win = (50, 100, 100)
    self.text_menu = (50, 100, 100)
    self.text_menu_active = (100, 50, 75)

    # mic bar
    self.mic_bar_meter = (210, 100, 20)

    # canvas
    self.canvas_background = (230, 210, 200)
    self.canvas_win_backgound = (230, 210, 200, 128)
    self.canvas_device_background = (255, 255, 255)



