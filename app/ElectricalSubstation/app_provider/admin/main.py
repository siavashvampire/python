from datetime import datetime, timedelta
from queue import Queue
from threading import Thread
from typing import List, Any

from persiantools.jdatetime import JalaliDateTime
from tinydb import TinyDB

import app.Logging.app_provider.admin.MersadLogging as Logging
from app.ElectricalSubstation.model.Device import Device
from app.ElectricalSubstation.render.render import RenderingDataThread
from core.app_provider.api.get import get_from_site_db
from core.config.Config import main_get_sensor_url, sensor_get_timeout, sensor_db_path, sensor_on_off_time, time_format, \
    sensor_table_name, switch_table_name
from core.config.Config import main_get_switch_url, switch_get_timeout, switch_db_path
from core.config.Config import time_delay_main_loop
from core.theme.pic import Pics


class ElectricalSubstation:

    def __init__(self, messenger_queue, sender_queue, sender_state_func, thread_label, ui):
        self.ui = ui
        self.state = False
        self.stop_check = False
        self.should_stop = False
        self.thread_label = thread_label
        self.DataQ = Queue()
        # self.messenger_queue = messenger_queue

        # self.mergeData = Cronjob(sender_state_func=sender_state_func)
        self.ArchiveQ = sender_queue
        self.create_devices()
        self.stop_thread = False
        self.Thread = Thread(target=self.electrical_substation,
                             args=(lambda: self.stop_thread,))
        self.Thread.start()
        self.RDThread = RenderingDataThread(device=self.devices,
                                            ui=self.ui)

    def electrical_substation(self, stop_thread):
        now = datetime.now()
        while True:
            try:
                data = self.DataQ.get(timeout=5)
                self.DataQ.task_done()

                if data:
                    self.RDThread.DataQ.put(data)
                else:
                    if stop_thread():
                        Logging.line_monitoring_log("Main Rendering Thread", "Stop")
                        break
            except:
                pass
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

    def restart_thread(self):
        if not (self.Thread.is_alive()):
            self.stop_thread = False
            self.Thread = Thread(target=self.electrical_substation, args=(lambda: self.stop_thread,))
            self.Thread.start()
        #     TODO:bayad thread cronjob ham biad
        if not (self.RDThread.Thread.is_alive()):
            self.RDThread.stop_thread = False
            self.RDThread.restart_thread()

    def create_devices(self):
        devices_db = TinyDB(sensor_db_path).table(sensor_table_name)
        # TODO:check konim bebinim hatman age data base haw khali bashi chi mishe error mdie ya na

        devices = devices_db.all()
        self.devices = [Device(switch_id=int(i["id"]), sender_queue=self.ArchiveQ) for i in devices]

    def db_update_all(self):
        self.read_all_device_data()

    @staticmethod
    def read_all_device_data():
        get_from_site_db(main_get_switch_url, switch_get_timeout, switch_db_path, switch_table_name)

    def check(self):
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
        self.stop_thread = True
        self.DataQ.put(0)
        self.Thread.join()
        self.RDThread.stop_thread = True
        self.RDThread.DataQ.put([0, None])
        self.RDThread.Thread.join()
        self.stop_check = True
        self.state = False
        self.thread_label.setIcon(Pics.OFF)

    def start_func(self):
        self.stop_thread = False
        self.RDThread.stop_thread = False
        self.restart_thread()
        self.stop_check = False
        self.state = True
        self.thread_label.setIcon(Pics.ON)

    def update_system(self, where_should_update):
        if "TileKindUpdate" in where_should_update:
            self.read_all_device_data()
            print("omad sensor")

        self.create_devices()
