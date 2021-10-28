from datetime import datetime
from threading import Thread
from time import sleep

import app.Logging.app_provider.admin.MersadLogging as Logging
from core.app_provider.api.get import site_connection
from core.config.Config import main_cronjob_merge_url, cronjob_timeout, merge_time, merge_check_time


class Cronjob:
    def __init__(self, sender_state_func, merge_time=merge_time):
        self.LastMerge = datetime.now()
        self.last_check = datetime.now()
        self.MergeTime = merge_time
        self.sender_state_func = sender_state_func
        self.stop_thread = False
        self.Thread = Thread(target=self.merge_data_thread, args=(lambda: self.stop_thread,))
        self.Thread.start()

    def merge_data(self):
        status, r = site_connection(main_cronjob_merge_url, cronjob_timeout)
        if status:
            if str(r) == "done.":
                self.LastMerge = datetime.now()

        return status

    def merge_data_thread(self, stop_thread):
        while True:
            sleep(5)
            if (datetime.now() - self.last_check).seconds > merge_check_time * 60:
                diff = datetime.now() - self.LastMerge
                hours = diff.seconds // 3600 + diff.days * 24
                if hours >= int(self.MergeTime):
                    self.sender_state_func(state=False, program=True)
                    # TODO:check konim bebinim vai mise ya na
                    self.merge_data()
                    self.sender_state_func(state=True, program=True)
                    self.last_check = datetime.now()
            if stop_thread():
                Logging.line_monitoring_log("Main Rendering Thread", "Stop")
                print("stop cronjob")
                break
