from time import sleep
from datetime import datetime
from threading import Thread

import app.Logging.app_provider.admin.MersadLogging as Logging
from core.app_provider.api.get import site_connection
from core.config.Config import MainCronMergeURL, CronJobTimeout, MergeTime, mergeCheckTime


class Cronjob:
    def __init__(self, sender_state_func, merge_time=MergeTime):
        self.LastMerge = datetime.now()
        self.last_check = datetime.now()
        self.MergeTime = merge_time
        self.sender_state_func = sender_state_func
        self.stop_thread = False
        self.Thread = Thread(target=self.merge_data_thread, args=(lambda: self.stop_thread,))
        self.Thread.start()

    def merge_data(self):
        status, r = site_connection(MainCronMergeURL, CronJobTimeout)
        if status:
            if str(r) == "done.":
                self.LastMerge = datetime.now()

        return status

    def merge_data_thread(self, stop_thread):
        while True:
            sleep(5)
            if (datetime.now() - self.last_check).seconds > mergeCheckTime * 60:
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
