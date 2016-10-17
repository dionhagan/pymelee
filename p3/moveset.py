
"""
    FOX MOVESET
"""

# FUNDAMENTALS
def stop(self, pad):
    # self.action_list.append((0, pad.reset, []))
    self.action_list.append((1, None, []))

def pressA(self, pad, x=0.5, y=0.5):
    actions = []
    actions.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, x, y]))
    actions.append((0, pad.press_button, [p3.pad.Button.A]))
    actions.append((2, pad.release_button, [p3.pad.Button.A]))
    actions.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0.5]))
    return actions

def pressB(self, pad, x=0.5, y=0.5):
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, x, y]))
    self.action_list.append((0, pad.press_button, [p3.pad.Button.B]))
    self.action_list.append((2, pad.release_button, [p3.pad.Button.B]))
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0.5]))

def pressX(self, pad):
    self.action_list.append((0, pad.press_button, [p3.pad.Button.X]))
    self.action_list.append((2, pad.release_button, [p3.pad.Button.X]))

def shield(self, pad):
    self.action_list.append((0, pad.press_trigger, [p3.pad.Trigger.L, 1]))


# MOVEMENT
def jump(self, pad):
    self.action_list.append((0, pad.press_button, [p3.pad.Button.X]))
    self.action_list.append((3, pad.release_button, [p3.pad.Button.X]))

def shorthop(self, pad):
    self.action_list.append((0, pad.press_button, [p3.pad.Button.X]))
    self.action_list.append((2, pad.release_button, [p3.pad.Button.X]))

def double_jump(self, pad):
    self.jump()
    self.jump()

def dash(self, pad, x, dur):
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, x, 0.5]))
    self.action_list.append((dur, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0.5]))

# SPECIALS
def laser(self, pad):
    self.action_list.append((0, pad.press_button, [p3.pad.Button.B]))
    self.action_list.append((1, pad.release_button, [p3.pad.Button.B]))

def upB(self, pad, x=0.5, y=1.0): 
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, x, y]))
    self.action_list.append((0, pad.press_button, [p3.pad.Button.B]))
    self.action_list.append((3, pad.release_button, [p3.pad.Button.B]))

def sideB(self, pad):
    pass

def shine(self, pad):
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0.0]))
    self.action_list.append((0, pad.press_button, [p3.pad.Button.B]))
    self.action_list.append((1, pad.release_button, [p3.pad.Button.B]))
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0.5]))

# SMASH ATTACKS
def fsmash(self, pad, x):
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.C, x, 0.5]))
    self.action_list.append((1, pad.tilt_stick, [p3.pad.Stick.C, 0.5, 0.5]))

def up_smash(self, pad):
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.C, 0.5, 1]))
    self.action_list.append((1, pad.tilt_stick, [p3.pad.Stick.C, 0.5, 0.5]))

def down_smash(self, pad):
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.C, 0, 0.5]))
    self.action_list.append((1, pad.tilt_stick, [p3.pad.Stick.C, 0.5, 0.5]))

# AERIALS
def nair(self, pad):
    self.shorthop(pad)
    self.pressA(pad)
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0]))
    self.action_list.append((2, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0.5]))

def fair(self, pad, state):
    self.shorthop(pad)
    self.pressA(pad, x=state.players[2].facing)
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0]))
    self.action_list.append((2, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0.5]))

def dair(self, pad):
    pass

def bair(self, pad):
    pass


# TECH
def shinespam(self, pad):
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0.0]))
    self.action_list.append((0, pad.press_button, [p3.pad.Button.B]))
    self.action_list.append((1, pad.release_button, [p3.pad.Button.B]))
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0.5]))
    self.action_list.append((0, pad.press_button, [p3.pad.Button.X]))
    self.action_list.append((1, pad.release_button, [p3.pad.Button.X]))
    self.action_list.append((1, None, []))

def shorthop_laser(self, pad):
    self.action_list.append((0, pad.press_button, [p3.pad.Button.X]))
    self.action_list.append((2, pad.release_button, [p3.pad.Button.X]))
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0.5]))
    self.action_list.append((0, pad.press_button, [p3.pad.Button.B]))
    self.action_list.append((1, pad.release_button, [p3.pad.Button.B]))
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0]))
    self.action_list.append((1, None, []))

def wavedash(self, pad, state):
    self.action_list.append((0, pad.press_button, [p3.pad.Button.X]))
    self.action_list.append((1, pad.release_button, [p3.pad.Button.X]))
    self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, 0, 0]))
    self.action_list.append((2, pad.press_trigger, [p3.pad.Trigger.L, 1]))
    self.action_list.append((2, pad.reset, []))