from datetime import datetime

from tinydb import TinyDB, Query

from core.config.Config import time_format, device_table_name, DeviceDBPath
from core.model.DataType import Device_new_log_app, Device_new_log_class, Device_new_log_method, \
    Device_new_log_data


class Device:
    doc_id: int

    def __init__(self, substation=0, substation_name=None, unit=None, name=None, device_type=None,
                 refresh_time=None, sender_queue=None):
        self.substation = substation
        self.substation_name = substation_name
        self.unit = unit
        self.name = name
        self.device_type = device_type
        self.refresh_time = refresh_time
        self.data_type = Device_new_log_data
        self.sender_queue = sender_queue

        if self.substation:
            self.update(self.substation)

    def send(self, values):
        self.sender_queue.put(
            {"app": Device_new_log_app,
             "class": Device_new_log_class,
             "method": Device_new_log_method,
             "data": self.get_data(values, datetime.now().strftime(time_format))})

    def update(self, substation=0, unit=0):
        Prop = Query()
        DB = TinyDB(DeviceDBPath).table(device_table_name)
        sea = DB.search((Prop.substation_id == substation) & (Prop.unitId == unit))
        sea = sea[0]
        self.substation_name = sea["substation_name"]
        self.name = sea["name"]
        self.device_type = int(sea["device_type"])
        self.refresh_time = int(sea["refresh_time"])
        self.doc_id = sea.doc_id