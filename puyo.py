from constants import EMPTY

class Puyo:
    def __init__(self, color, state="normal", animation_timer=0):
        self.color = color
        self.state = state
        self.animation_timer = animation_timer
    