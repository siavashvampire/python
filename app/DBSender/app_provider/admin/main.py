import json
import threading
from datetime import datetime
from queue import Queue
from threading import Thread
from time import sleep
from typing import Any

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from tinydb import TinyDB, table
from tinydb.table import Table

import app.Logging.app_provider.admin.MersadLogging as Logging
from core.RH.ResponseHandler import send_data_rh
from core.app_provider.api.get import get_from_site_db, site_connection
from core.config.Config import main_get_check_url, log_db_path, main_default_log_url, send_timeout, check_timeout, \
    queue_sender_max_wait, sleep_time_1, sleep_time_2, sleep_time_3, sender_table_name, count_for_send_list, \
    boundary_for_payload, send_list_flag
from core.theme.pic import Pics


class DataArchive:
    update_queue: Queue[bool]
    state: bool
    should_stop: bool
    checkDBui: bool
    stop_check: bool
    DB: Table
    insertFlag: bool
    DBCheck: int
    ArchiveQ: Queue[Any]
    stop_thread: bool
    Force2Send: bool
    on: QPixmap
    off: QPixmap
    Thread: Thread
    check_label: QLabel
    thread_label: QLabel

    def __init__(self, check_label=None, thread_label=None):
        self.state = False
        self.should_stop = False
        self.thread_label = thread_label
        self.check_label = check_label
        self.checkDBui = False
        self.stop_check = False
        self.DB = TinyDB(log_db_path).table(sender_table_name)
        self.insertFlag = False
        self.DBCheck = 2
        self.ArchiveQ = Queue()
        self.stop_thread = False
        self.Force2Send = True
        self.on = Pics.checkMark
        self.off = Pics.deleteMark
        self.Thread = threading.Thread(target=self.saving_data, args=(lambda: self.stop_thread,))
        self.check_label.setPixmap(self.off)
        self.update_queue = Queue()

    def run_thread(self) -> None:
        self.Thread.start()

    def saving_data(self, stop_thread) -> None:
        now = datetime.now()
        sleep(1)
        while True:
            diff = datetime.now() - now
            sleep_time = 10
            if self.DBCheck == 2:
                sleep_time = sleep_time_3
            elif self.DBCheck == 1:
                sleep_time = sleep_time_2
            elif self.DBCheck == 0:
                sleep_time = sleep_time_1
            try:
                save_item = self.ArchiveQ.get(timeout=1)
                self.ArchiveQ.task_done()
                self.save_data(save_item)
                if queue_sender_max_wait:
                    if self.ArchiveQ.qsize() > queue_sender_max_wait:
                        now = datetime.now()
            except:
                if stop_thread():
                    break
            if diff.seconds > sleep_time or self.Force2Send:
                self.DBCheck = 0
                if self.local_db_len() or self.Force2Send:
                    if self.Force2Send:
                        self.Force2Send = False
                    self.DBCheck = 1
                    if self.check_db():
                        if not self.checkDBui:
                            self.checkDBui = True
                            self.check_label.setPixmap(self.on)
                        self.DBCheck = 2
                        while self.local_db_len() and not stop_thread():
                            if not self.import_db_check():
                                self.DBCheck = 1
                                break
                    else:
                        if self.checkDBui:
                            self.checkDBui = False
                            self.check_label.setPixmap(self.off)
                now = datetime.now()

    def save_data(self, item) -> None:
        good = False
        while not good:
            try:
                self.DB.insert(item)
                good = True
            except Exception as e:
                Logging.sender_log("insert data", str(e))
                good = False

    def get_save_data(self) -> list:
        if self.local_db_len():
            if send_list_flag:
                return self.DB.all()[0:count_for_send_list]
            else:
                return [self.DB.all()[0]]
        else:
            return []

    def delete_data(self, id_del: list[int]) -> None:
        self.DB.remove(doc_ids=id_del)

    def import_db_check(self) -> bool:
        s = self.get_save_data()
        if len(s):
            send_flag, should_update, s_doc_id = self.send_data(s)
            if send_flag:
                self.delete_data(s_doc_id)
            if should_update:
                self.update_queue.put(should_update)
            return send_flag
        else:
            return False

    def send_data(self, data: list[table.Document]) -> tuple[bool, bool, list[int]]:
        url = main_default_log_url
        good = False
        should_update = False
        index = []
        if self.check_db():
            payload = json.dumps(data)
            payload = "--" + boundary_for_payload + "\r\nContent-Disposition: form-data; name=\"DataArray\"\r\n\r\n" \
                      + payload + "\r\n--" + boundary_for_payload + "--"
            headers = {'cache-control': "no-cache",
                       'content-type': "multipart/form-data; boundary=" + boundary_for_payload}
            status, r = site_connection(url, send_timeout, data=payload, header=headers)
            good, index, error, should_update = send_data_rh(r, status)
            # self.insertFlag = RH(r, status)

        s_doc_id = [data[i].doc_id for i in index]
        return good, should_update, s_doc_id

    def local_db_len(self) -> int:
        len_db = len(self.DB)
        if not len_db:
            self.DB = TinyDB(log_db_path).table(sender_table_name)
        return len_db

    @staticmethod
    def check_db() -> bool:
        return get_from_site_db(main_get_check_url, check_timeout)[0]

    def restart_thread(self) -> None:
        if not (self.Thread.is_alive()):
            self.stop_thread = False
            self.Thread = threading.Thread(target=self.saving_data, args=(lambda: self.stop_thread,))
            self.Thread.start()

    def state_thread(self, state=False, program=False) -> None:
        if program is False:
            if self.state:
                self.should_stop = True
                self.stop_func()
                Logging.sender_log("sender", "stop")
            else:
                self.should_stop = False
                self.start_func()
                Logging.sender_log("sender", "start")
        else:
            if state is True:
                if not self.should_stop:
                    self.start_func()
            if state is False:
                self.stop_func()

    def stop_func(self) -> None:
        self.stop_thread = True
        self.Thread.join()
        self.stop_check = True
        self.state = False
        self.thread_label.setIcon(Pics.OFF)

    def start_func(self) -> None:
        self.stop_thread = False
        self.restart_thread()
        self.stop_check = False
        self.state = True
        self.DBCheck = 2
        self.thread_label.setIcon(Pics.ON)

    def check(self) -> None:
        if not (self.Thread.is_alive()):
            if self.state:
                self.thread_label.setIcon(Pics.OFF)
                self.state = False
            if not self.stop_check:
                self.stop_thread = False
                self.restart_thread()
        else:
            if not self.state:
                self.thread_label.setIcon(Pics.ON)
                self.state = True
        if not self.state:
            self.checkDBui = False
            self.check_label.setPixmap(Pics.MinusMark)

    def force_check_db(self) -> None:
        self.Force2Send = True
