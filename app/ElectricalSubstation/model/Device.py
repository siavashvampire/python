from datetime import datetime

from tinydb import TinyDB, Query

from core.config.Config import time_format, device_table_name, DeviceDBPath
from core.model.DataType import Device_new_log_app, Device_new_log_class, Device_new_log_method, \
    Device_new_log_data


def find_sensor_choose(choose, sensors):
    for sen in sensors:
        if sen.PLC_id == choose:
            return sen
    return False


class Device:
    doc_id: int

    def __init__(self, substation=0, substation_name=None, unit=None, name=None, device_type=None,
                 refresh_time=None, SenderQ=None):
        self.substation = substation
        self.substation_name = substation_name
        self.unit = unit
        self.name = name
        self.device_type = device_type
        self.refresh_time = refresh_time
        self.data_type = Device_new_log_data
        self.SenderQ = SenderQ

        if self.substation:
            self.update(self.substation)

    def send(self, values):
        self.SenderQ.put(
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

    def get_data(self, value, time):
        data_temp = dict(self.data_type)
        key = sorted(list(data_temp.keys()), key=self.key_order)

        data_temp[key[0]] = self.sensor_id  # for switch id
        data_temp[key[1]] = value  # for on value
        data_temp[key[2]] = self.counter  # for counter
        data_temp[key[3]] = self.Tile_Kind  # for Tile_Kind
        data_temp[key[4]] = self.Motor_Speed  # for Motor_Speed
        data_temp[key[5]] = time  # for time
        return data_temp

    @staticmethod
    def key_order(key):
        import difflib
        app_order = ["Sensor_id", "AbsTime", "counter", "Tile_Kind", "Motor_Speed", "start_time"]

        key = difflib.get_close_matches(key, app_order)

        if len(key) != 0:
            if key[0] == "Sensor_id":
                return 1
            elif key[0] == "AbsTime":
                return 2
            elif key[0] == "counter":
                return 3
            elif key[0] == "Tile_Kind":
                return 4
            elif key[0] == "Motor_Speed":
                return 5
            elif key[0] == "start_time":
                return 6
            else:
                return 0
        else:
            return 0
