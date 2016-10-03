import p3.pad

class Fox:
    def __init__(self):
        self.action_list = []
        self.last_action = 0

    def advance(self, state, pad):
        while self.action_list:
            wait, func, args = self.action_list[0]
            if state.frame - self.last_action < wait:
                return
            self.action_list.pop(0)
            if func is not None:
                func(*args)
            self.last_action = state.frame
        else:
            # Eventually this will point at some decision-making thing.
            # pseudo: self.action_list = max(score(getSuccessors()))
            print (state.players)
            print ('\n')
            self.pressB(pad)
            self.shorthop_laser(pad)
            self.pressB(pad, 0.5, 1)

    """
        FOX MOVESET
    """

    # FUNDAMENTALS
    def stop(self):
        self.action_list.append((1, None, []))

    def pressA(self, pad, x=0.5, y=0.5):
        self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, x, y]))
        self.action_list.append((0, pad.press_button, [p3.pad.Button.A]))
        self.action_list.append((2, pad.release_button, [p3.pad.Button.A]))
        self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0.5]))

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
        self.action_list.append((1, pad.release_button, [p3.pad.Button.X]))

    def double_jump(self, pad):
        self.jump()
        self.jump()

    def dash(self, pad, x, dur):
        self.action_list.append((0, pad.tilt_stick, x, 0.5))
        self.action_list.append((dur, pad.tilt_stick, 0.5, 0.5))

    # SPECIALS
    def laser(self, pad):
        self.action_list.append((0, pad.press_button, [p3.pad.Button.B]))
        self.action_list.append((1, pad.release_button, [p3.pad.Button.B]))

    def upB(self, pad):
        pass

    def sideB(self, pad):
        pass

    def shine(self, pad):
        pass

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
    def shffl_nair(self, pad):
        self.shorthop(pad)
        self.pressA(pad)
        self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0]))
        self.action_list.append((1, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0.5]))

    def shffl_fair(self, pad):
        self.shorthop(pad)
        self.pressA(pad,)
        self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0]))
        self.action_list.append((1, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0.5]))

    def shffl_dair(self, pad):
        pass

    def shffl_bair(self, pad):
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

    def wavedash(self, pad, x):
        self.shorthop(pad)
        self.action_list.append((0, pad.tilt_stick, [p3.pad.Stick.MAIN, x, 0]))
        self.action_list.append((0, pad.press_trigger, [p3.pad.Trigger.L]))
        self.action_list.append((0, pad.release_trigger, [p3.pad.Trigger.L]))
        self.action_list.append((1, pad.tilt_stick, [p3.pad.Stick.MAIN, 0.5, 0.5]))
