from datetime import datetime, timedelta
from queue import Queue
from threading import Thread
from time import sleep
from typing import Callable

from PyQt5.QtWidgets import QLabel
from persiantools.jdatetime import JalaliDateTime
from tinydb import TinyDB

import app.Logging.app_provider.admin.MersadLogging as Logging
from app.LineMonitoring.cronjob.cronjob import Cronjob
from app.LineMonitoring.model.CamSwitch import CamSwitch
from app.LineMonitoring.model.Sensor import Sensor
from app.LineMonitoring.render.render import RenderingDataThread
from core.app_provider.api.get import get_from_site_db
from core.config.Config import main_get_sensor_url, sensor_get_timeout, sensor_db_path, sensor_on_off_time, time_format, \
    sensor_table_name, switch_table_name
from core.config.Config import main_get_switch_url, switch_get_timeout, switch_db_path
from core.config.Config import time_delay_main_loop
from core.theme.pic import Pics


class LineMonitoring:
    state: bool
    stop_check: bool
    should_stop: bool
    thread_label: QLabel
    messenger_queue: Queue[list[str, int, int, int]]
    mergeData: Cronjob
    sensors: list[Sensor]
    switch: list[CamSwitch]
    stop_thread: bool
    Thread: Thread
    RDThread: RenderingDataThread

    def __init__(self, messenger_queue: Queue[list[str, int, int, int]], sender_queue, sender_state_func,
                 thread_label: QLabel, ui) -> None:
        self.ui = ui
        self.state = False
        self.stop_check = False
        self.should_stop = False
        self.thread_label = thread_label
        self.messenger_queue = messenger_queue

        self.mergeData = Cronjob(sender_state_func=sender_state_func)
        self.ArchiveQ = sender_queue
        self.sensors = []
        self.switch = []
        self.create_sensors()
        self.stop_thread = False
        self.Thread = Thread(target=self.line_monitoring,
                             args=(lambda: self.stop_thread,))
        self.Thread.start()
        self.RDThread = RenderingDataThread(sensor=self.sensors,
                                            switch=self.switch,
                                            messenger_queue=self.messenger_queue,
                                            ui=self.ui)

    def line_monitoring(self, stop_thread: Callable[[], bool]) -> None:
        now = datetime.now()
        while True:
            sleep(5)
            if (datetime.now() - now).seconds > sensor_on_off_time:
                now = datetime.now()
                for s in self.sensors:
                    if s.OffTime:
                        ll_temp = s.LastLog
                        if not ll_temp == None:
                            diff = (now + timedelta(seconds=time_delay_main_loop)) - ll_temp
                            now_te = JalaliDateTime.to_jalali(ll_temp)
                            if s.Active:
                                if diff.days or (diff.seconds > (s.OffTime * 60 + time_delay_main_loop)):
                                    s.send_activity(False, ll_temp.strftime(time_format))

                            if s.OffTime_Bale:
                                if s.Active_Bale:
                                    if diff.days or diff.seconds > s.OffTime_Bale * 60:
                                        s.Active_Bale = False
                                        if self.ui.Setting.baleONOFFSendFlag.isChecked():
                                            if self.ui.Setting.baleONOFFFlag.isChecked():
                                                print("off Sensor {} send".format(s.sensor_id))
                                            off_sensor_bale_text = str(s.label) + " فاز " + str(s.phaseLabel) + str(
                                                now_te.strftime(' در %y/%m/%d ساعت %H:%M:%S')) + " خاموش شده است"
                                            self.messenger_queue.put([off_sensor_bale_text, s.unit, s.phase, 1])
                            if s.OffTime_SMS:
                                if s.Active_SMS:
                                    if diff.days or diff.seconds > s.OffTime_SMS * 60:
                                        s.Active_SMS = False
                                        off_sensor_sms_text = str(s.label) + " فاز " + str(s.phaseLabel) + str(
                                            now_te.strftime(' در %y/%m/%d ساعت %H:%M:%S')) + " خاموش شده است"
                                        self.messenger_queue.put([off_sensor_sms_text, s.unit, s.phase, 2])

            if stop_thread():
                Logging.line_monitoring_log("Main Rendering Thread", "Stop")
                break

    def restart_thread(self) -> None:
        if not (self.Thread.is_alive()):
            self.stop_thread = False
            self.Thread = Thread(target=self.line_monitoring, args=(lambda: self.stop_thread,))
            self.Thread.start()
        #     TODO:bayad thread cronjob ham biad
        if not (self.RDThread.Thread.is_alive()):
            self.RDThread.stop_thread = False
            self.RDThread.restart_thread()

    def create_sensors(self) -> None:
        self.sensors.clear()
        self.switch.clear()
        sensor_db = TinyDB(sensor_db_path).table(sensor_table_name)
        switch_db = TinyDB(switch_db_path).table(switch_table_name)
        # TODO:check konim bebinim hatman age data base haw khali bashi chi mishe error mdie ya na

        sensors = sensor_db.all()
        switches = switch_db.all()
        # self.switch = [CamSwitch(switch_id=int(i["id"]), sender_queue=self.ArchiveQ) for i in switches]

        # self.sensors = [Sensor(sensor_id=int(i["id"]), ui=self.ui, sender_queue=self.ArchiveQ) for i in sensors]
        for i in sensors:
            self.sensors.append(Sensor(sensor_id=int(i["id"]), ui=self.ui, sender_queue=self.ArchiveQ))
        for i in switches:
            self.switch.append(CamSwitch(switch_id=int(i["id"]), sender_queue=self.ArchiveQ))

    def db_update_all(self) -> None:
        self.read_all_sensor_data()
        self.read_all_switch_data()

    @staticmethod
    def read_all_switch_data() -> None:
        get_from_site_db(main_get_switch_url, switch_get_timeout, switch_db_path, switch_table_name)

    @staticmethod
    def read_all_sensor_data() -> None:
        get_from_site_db(main_get_sensor_url, sensor_get_timeout, sensor_db_path, sensor_table_name)

    def check(self) -> None:
        if not (self.RDThread.Thread.is_alive()):
            if self.state:
                self.thread_label.setIcon(Pics.OFF)
                self.state = False
            if not self.stop_check:
                self.RDThread.stop_thread = False
                self.RDThread.restart_thread()
        else:
            if not self.state:
                self.thread_label.setIcon(Pics.ON)
                self.state = True
        if not (self.Thread.is_alive()):
            if self.state:
                self.thread_label.setIcon(Pics.OFF)
                self.state = False
            if not self.stop_check:
                self.restart_thread()
                self.stop_thread = False
        else:
            if not self.state:
                self.thread_label.setIcon(Pics.ON)
                self.state = True

    def state_thread(self, state: bool = False, program: bool = False) -> None:
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

    def stop_func(self) -> None:
        self.stop_thread = True
        self.Thread.join()
        self.RDThread.stop_thread = True
        self.RDThread.DataQ.put([0, 0])
        self.RDThread.Thread.join()
        self.stop_check = True
        self.state = False
        self.thread_label.setIcon(Pics.OFF)

    def start_func(self) -> None:
        self.stop_thread = False
        self.RDThread.stop_thread = False
        self.restart_thread()
        self.stop_check = False
        self.state = True
        self.thread_label.setIcon(Pics.ON)

    def update_system(self, where_should_update: tuple[str, str] = ("sensor_update", "switch_update")) -> None:
        if "sensor_update" in where_should_update:
            self.read_all_sensor_data()
        if "switch_update" in where_should_update:
            self.read_all_switch_data()

        self.create_sensors()
