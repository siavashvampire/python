from time import sleep
from threading import Thread
from typing import Callable

from PyQt5.QtWidgets import QLabel
from tinydb import TinyDB, Query

import app.Logging.app_provider.admin.MersadLogging as Logging
from app.ElectricalSubstation.model.Device import Device
from app.ElectricalSubstation.render.render import RenderingDataThread
from core.app_provider.api.get import get_from_site_db
from core.config.Config import device_db_path, device_table_name, main_get_device_url, device_get_timeout
from core.theme.pic import Pics


class ElectricalSubstation:
    state: bool
    stop_check: bool
    should_stop: bool
    thread_label: QLabel
    stop_thread: bool
    Thread: Thread
    RDThread: RenderingDataThread
    devices: list[Device]

    def __init__(self, messenger_queue, sender_queue, sender_state_func, thread_label, ui):
        self.ui = ui
        self.state = False
        self.stop_check = False
        self.should_stop = False
        self.thread_label = thread_label
        self.devices = []
        # self.messenger_queue = messenger_queue

        # self.mergeData = Cronjob(sender_state_func=sender_state_func)
        self.ArchiveQ = sender_queue
        self.create_devices()
        self.stop_thread = False
        self.Thread = Thread(target=self.electrical_substation,
                             args=(lambda: self.stop_thread,))
        self.Thread.start()
        self.RDThread = RenderingDataThread(devices=self.devices,
                                            ui=self.ui)

    def electrical_substation(self, stop_thread: Callable[[], bool]):
        while True:
            sleep(5)
            if stop_thread():
                Logging.line_monitoring_log("Main Rendering Thread", "Stop")
                break

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
        devices_db = TinyDB(device_db_path).table(device_table_name)
        # TODO:check konim bebinim hatman age data base haw khali bashi chi mishe error mdie ya na
        self.devices.clear()

        devices = devices_db.all()
        for i in devices:
            self.devices.append(
                Device(substation=int(i["substation_id"]), unit=int(i["unitId"]), sender_queue=self.ArchiveQ))

    def db_update_all(self):
        self.read_all_device_data()

    @staticmethod
    def read_all_device_data():
        get_from_site_db(main_get_device_url, device_get_timeout, device_db_path, device_table_name)

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
        self.RDThread.DataQ.put([(0, 0), {"substation_id": 0}])
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

    def update_system(self, where_should_update: tuple[str] = ()) -> None:
        self.read_all_device_data()
        self.create_devices()


def get_devices_by_substation_id(substation_id: int) -> list[Device]:
    devices_db = TinyDB(device_db_path).table(device_table_name)
    devices = devices_db.search(Query().substation_id == substation_id)

    devices_obj = [Device(substation=int(i["substation_id"]), unit=int(i["unitId"]))
                   for i in devices]
    return devices_obj
