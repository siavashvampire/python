from queue import Queue
from time import sleep
from datetime import datetime
from threading import Thread

import app.Logging.app_provider.admin.MersadLogging as Logging
from app.shift.model.Day import isDayUpdated, adminDayCounter
from core.app_provider.api.get import site_connection
from core.config.Config import main_cronjob_update_shift_url, cronjob_timeout, main_cronjob_update_day_url, \
    shift_check_time, adminUnit, choose_of_bale, choose_of_sms


class Cronjob:
    Thread: Thread
    stop_thread: bool
    last_check: datetime
    messenger_queue: Queue[list[str, int, int, int]]

    def __init__(self, messenger_queue: Queue[list[str, int, int, int]], sender_state_func) -> None:
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
                if (datetime.now() - self.last_check).seconds > shift_check_time:
                    self.sender_state_func(state=False, program=True)
                    self.update_shift()
                    self.update_day()

                    if isDayUpdated():
                        day_count = adminDayCounter()
                        self.messenger_queue.put([day_count, adminUnit, -4, choose_of_bale])
                        self.messenger_queue.put([day_count, adminUnit, -4, choose_of_sms])
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
        site_connection(main_cronjob_update_shift_url, cronjob_timeout)

    @staticmethod
    def update_day():
        site_connection(main_cronjob_update_day_url, cronjob_timeout)

    def restart_thread(self):
        if not (self.Thread.is_alive()):
            self.stop_thread = False
            self.Thread = Thread(target=self.update_shift_thread, args=(lambda: self.stop_thread,))
            self.Thread.start()
