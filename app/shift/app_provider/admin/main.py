from app.shift.cronjob.cronjob import Cronjob


class Shift:
    def __init__(self, sender_state_func):
        self.state = False
        self.stop_check = False
        self.should_stop = False

        self.update_shift = Cronjob(sender_state_func=sender_state_func)

    def state_thread(self, state=False, program=False):
        if program is False:
            if self.state:
                self.should_stop = True
                self.stop_func()
            else:
                self.should_stop = False
                self.start_func()
        else:
            if state is True:
                if not self.should_stop:
                    self.start_func()
            if state is False:
                self.stop_func()

    def stop_func(self):
        self.update_shift.stop_thread = True
        self.stop_check = True
        self.state = False

    def start_func(self):
        self.update_shift.stop_thread = False
        self.update_shift.restart_thread()
        self.stop_check = False
        self.state = True
