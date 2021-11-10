from datetime import datetime

from tinydb import TinyDB, Query

from core.config.Config import time_format, device_table_name, device_db_path
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

        if self.substation and self.unit:
            self.update(self.substation, self.unit)

    def send(self, values):
        self.sender_queue.put(
            {"app": Device_new_log_app,
             "class": Device_new_log_class,
             "method": Device_new_log_method,
             "data": self.get_data(values, datetime.now().strftime(time_format))})

    def update(self, substation=0, unit=0):
        Prop = Query()
        DB = TinyDB(device_db_path).table(device_table_name)
        sea = DB.search((Prop.substation_id == substation) & (Prop.unitId == unit))
        if sea:
            sea = sea[0]
            self.substation_name = sea["substation_name"]
            self.name = sea["Name"]
            self.device_type = int(sea["deviceType"])
            self.refresh_time = int(sea["refreshTime"])
            self.doc_id = sea.doc_id
        else:
            # TODO: Ejade log baraye else
            pass


def find_device(substation_id: int, unitId: int, devices: list[Device]) -> Device:
    for this_device in devices:
        if this_device.substation == substation_id:
            if this_device.unit == unitId:
                print(this_device.substation_name)
                return Device()
