from datetime import datetime, timedelta
from threading import Thread
from time import sleep

from persiantools.jdatetime import JalaliDateTime
from tinydb import TinyDB

import app.Logging.app_provider.admin.MersadLogging as Logging
from app.LineMonitoring.cronjob.cronjob import Cronjob
from app.LineMonitoring.model.CamSwitch import CamSwitch
from app.LineMonitoring.model.Sensor import Sensor
from app.LineMonitoring.render.render import RenderingDataThread
from core.app_provider.api.get import get_from_site_db
from core.config.Config import MainGetSensorURL, SensorGetTimeout, SensorDBPath, SensorONOFFTime, time_format, \
    sensor_table_name, switch_table_name
from core.config.Config import MainGetSwitchURL, SwitchGetTimeout, SwitchDBPath
from core.config.Config import TimeDelayMainLoop
from core.theme.pic import Pics


class LineMonitoring:
    def __init__(self, messenger_queue, sender_queue, sender_state_func, thread_label, ui):
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

    def line_monitoring(self, stop_thread):
        now = datetime.now()
        while True:
            sleep(5)
            if (datetime.now() - now).seconds > SensorONOFFTime:
                now = datetime.now()
                for s in self.sensors:
                    if s.OffTime:
                        ll_temp = s.LastLog
                        if not ll_temp == None:
                            diff = (now + timedelta(seconds=TimeDelayMainLoop)) - ll_temp
                            now_te = JalaliDateTime.to_jalali(ll_temp)
                            if s.Active:
                                if diff.days or (diff.seconds > (s.OffTime * 60 + TimeDelayMainLoop)):
                                    s.send_activity(False, ll_temp.strftime(time_format))

                            if s.OffTime_Bale:
                                if s.Active_Bale:
                                    if diff.days or diff.seconds > s.OffTime_Bale * 60:
                                        s.Active_Bale = False
                                        if self.ui.Setting.baleONOFFSendFlag.isChecked():
                                            if self.ui.Setting.baleONOFFFlag.isChecked():
                                                print("off Sensor {} send".format(s.sensor_id))
                                            off_sensor_bale_text = str(s.Name) + " فاز " + str(s.Phase) + str(
                                                now_te.strftime(' در %y/%m/%d ساعت %H:%M:%S')) + " خاموش شده است"
                                            self.messenger_queue.put([off_sensor_bale_text, s.unitId, s.Phase, 1])
                            if s.OffTime_SMS:
                                if s.Active_SMS:
                                    if diff.days or diff.seconds > s.OffTime_SMS * 60:
                                        s.Active_SMS = False
                                        off_sensor_sms_text = str(s.Name) + " فاز " + str(s.Phase) + str(
                                            now_te.strftime(' در %y/%m/%d ساعت %H:%M:%S')) + " خاموش شده است"
                                        self.messenger_queue.put([off_sensor_sms_text, s.unitId, s.Phase, 2])

            if stop_thread():
                Logging.line_monitoring_log("Main Rendering Thread", "Stop")
                break

    def restart_thread(self):
        if not (self.Thread.is_alive()):
            self.stop_thread = False
            self.Thread = Thread(target=self.line_monitoring, args=(lambda: self.stop_thread,))
            self.Thread.start()
        #     TODO:bayad thread cronjob ham biad
        if not (self.RDThread.Thread.is_alive()):
            self.RDThread.stop_thread = False
            self.RDThread.restart_thread()

    def create_sensors(self):
        sensor_db = TinyDB(SensorDBPath).table(sensor_table_name)
        switch_db = TinyDB(SwitchDBPath).table(switch_table_name)
        # TODO:check konim bebinim hatman age data base haw khali bashi chi mishe error mdie ya na

        r = sensor_db.all()
        switches = switch_db.all()
        self.switch = [CamSwitch(switch_id=int(i["id"]), sender_queue=self.ArchiveQ) for i in switches]

        self.sensors = [Sensor(sensor_id=int(i["id"]), ui=self.ui, sender_queue=self.ArchiveQ) for i in r]

    def db_update_all(self):
        self.read_all_sensor_data()
        self.read_all_switch_data()

    @staticmethod
    def read_all_switch_data():
        get_from_site_db(MainGetSwitchURL, SwitchGetTimeout, SwitchDBPath, switch_table_name)

    @staticmethod
    def read_all_sensor_data():
        get_from_site_db(MainGetSensorURL, SensorGetTimeout, SensorDBPath, sensor_table_name)

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
            self.read_all_switch_data()
            print("omad sensor")
        if "SwitchKindUpdate" in where_should_update:
            self.read_all_sensor_data()
            print("omad switch")

        self.create_sensors()
