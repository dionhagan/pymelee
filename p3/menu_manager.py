import math
import time

import p3.pad

class MenuManager:
    def __init__(self):
        self.selected_falco = False

    def pick_falco(self, state, pad):
        if self.selected_falco:
            # Release buttons and lazilly rotate the c stick.
            pad.release_button(p3.pad.Button.A)
            pad.tilt_stick(p3.pad.Stick.MAIN, 0.5, 0.5)
            self.press_start_lots(state, pad)
            # angle = (state.frame % 240) / 240.0 * 2 * math.pi
            # pad.tilt_stick(p3.pad.Stick.C, 0.4 * math.cos(angle) + 0.5, 0.4 * math.sin(angle) + 0.5)
        else:
            # Go to falco and press A

            # Falco
            # target_x = -30.5
            # target_y = 11.5

            # Marth
            # target_x = 10.5
            # target_y = 4

            # Falcon
            target_x = 20.5
            target_y = 15.5

            dx = target_x - state.players[2].cursor_x
            dy = target_y - state.players[2].cursor_y
            mag = math.sqrt(dx * dx + dy * dy)
            if mag < 0.5:
                pad.press_button(p3.pad.Button.A)
                self.selected_falco = True
            else:
                pad.tilt_stick(p3.pad.Stick.MAIN, 0.5 * (dx / mag) + 0.5, 0.5 * (dy / mag) + 0.5)

    def pick_fd(self, state, pad):
        # Go to final destination and press A
        target_x = 75
        target_y = 75
        dx = target_x - state.players[2].cursor_x
        dy = target_y - state.players[2].cursor_y
        mag = math.sqrt(dx * dx + dy * dy)
        if mag < 0.3:
            pad.press_button(p3.pad.Button.A)

    def press_start_lots(self, state, pad):
        if state.frame % 500 == 0:
            pad.press_button(p3.pad.Button.START)
        else:
            pad.release_button(p3.pad.Button.START)
