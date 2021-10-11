from time import sleep
from datetime import datetime
from threading import Thread

import app.Logging.app_provider.admin.MersadLogging as Logging
from app.shift.model.Day import isDayUpdated, adminDayCounter
from core.app_provider.api.get import site_connection
from core.config.Config import MainCronShiftURL, CronJobTimeout, MainCronDayURL, ShiftCheckTime


class Cronjob:
    def __init__(self, messenger_queue, sender_state_func):
        self.messenger_queue = messenger_queue
        self.last_check = datetime.now()
        self.sender_state_func = sender_state_func
        self.stop_thread = False
        self.Thread = Thread(target=self.update_shift_thread, args=(lambda: self.stop_thread,))
        self.Thread.start()

    def update_shift_thread(self, stop_thread):
        while True:
            sleep(5)
            try:
                if (datetime.now() - self.last_check).seconds > ShiftCheckTime:
                    self.sender_state_func(state=False, program=True)
                    self.update_shift()
                    self.update_day()

                    if isDayUpdated():
                        day_count = adminDayCounter()
                        self.messenger_queue.TextQ.put([day_count, -3, 0, 1])
                        self.messenger_queue.TextQ.put([day_count, -3, 0, 2])
                    self.sender_state_func(state=True, program=True)
                    self.last_check = datetime.now()
            except Exception as e:
                Logging.main_log("Main_Try", str(e))
                pass

            if stop_thread():
                Logging.line_monitoring_log("Main Rendering Thread", "Stop")
                print("stop cronjob shift")
                break

    @staticmethod
    def update_shift():
        site_connection(MainCronShiftURL, CronJobTimeout)

    @staticmethod
    def update_day():
        site_connection(MainCronDayURL, CronJobTimeout)

    def restart_thread(self):
        if not (self.Thread.is_alive()):
            self.stop_thread = False
            self.Thread = Thread(target=self.update_shift_thread, args=(lambda: self.stop_thread,))
            self.Thread.start()
