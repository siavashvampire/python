from datetime import datetime

from tinydb import TinyDB, Query

import app.LineMonitoring.app_provider.api.LastLog as LastLog
from core.config.Config import SensorDBPath, time_format, sensor_table_name
from core.model.DataType import sensor_new_log_app_name, sensor_new_log_data, sensor_activity_app_name, \
    sensor_activity_data


def find_sensor_choose(choose, sensors):
    for sen in sensors:
        if sen.PLC_id == choose:
            return sen
    return False


class Sensor:
    Active_Bale: object
    Active_SMS: object
    PLC_id: int
    doc_id: int

    def __init__(self, sensor_id=0, name="", unit_id=None, phase=None, counter=1, off_time=5, off_time_bale=5,
                 off_time_sms=5, tile_kind=None, motor_speed=None, active=False, sender_queue=None, ui=None):
        self.Name = name
        self.SenderQ = sender_queue
        self.sensor_id = sensor_id
        self.counter = counter
        self.Tile_Kind = tile_kind
        self.Motor_Speed = motor_speed
        self.Active = active
        self.LastLog = LastLog
        self.OffTime = off_time
        self.OffTime_Bale = off_time_bale
        self.OffTime_SMS = off_time_sms
        self.Phase = phase
        self.unitId = unit_id
        self.data_type = sensor_new_log_data
        self.data_activity_type = sensor_activity_data

        if self.sensor_id:
            self.update(self.sensor_id)

        if self.doc_id < 9 and ui is not None:
            from core.theme.pic import Pics
            self.lbl_Data_Name = ui.lbl_Data_Name[self.doc_id - 1]
            self.lbl_Data = ui.lbl_Data[self.doc_id - 1]
            self.lbl_Data_Status = ui.lbl_Data_Status[self.doc_id - 1]
            self.lbl_Data_Name.setText(str(self.Name))

            if self.Active:
                self.lbl_Data_Status.setPixmap(Pics.checkMark)
            else:
                self.lbl_Data_Status.setPixmap(Pics.deleteMark)

            if self.OffTime == 0:
                self.lbl_Data_Status.setPixmap(Pics.MinusMark)
        else:
            self.lbl_Data_Name = ""
            self.lbl_Data = ""
            self.lbl_Status = ""

    def send(self, value):
        BaleReportFlag = False
        SMSReportFlag = False
        now = datetime.now().strftime(time_format)

        self.SenderQ.put(
            {"app": sensor_new_log_app_name,
             "data": self.get_data(value, datetime.now().strftime(time_format))})

        if self.OffTime:
            self.LastLog = datetime.now()
            LastLog.update(self.sensor_id)
        if not self.Active:
            self.send_activity(True, now)
        if not self.Active_Bale:
            self.Active_Bale = True
            BaleReportFlag = True
        if not self.Active_SMS:
            self.Active_SMS = True
            SMSReportFlag = True
        if not self.lbl_Data_Name == "":
            self.lbl_Data.setText(str(value))
        return BaleReportFlag, SMSReportFlag

    def update(self, sensor_id=0):
        if sensor_id == 0:
            sensor_id = self.sensor_id
        SensorProp = Query()
        SensorDB = TinyDB(SensorDBPath).table(sensor_table_name)
        sea = SensorDB.search(SensorProp.id == sensor_id)
        sea = sea[0]
        self.PLC_id = int(sea["PLC_id"])
        self.counter = sea["tile_Count"]
        self.Tile_Kind = sea["tile_id"]
        self.Name = sea["Name"]
        self.OffTime = sea["OffTime"]
        self.OffTime_Bale = sea["OffTime_Bale"]
        self.OffTime_SMS = sea["OffTime_SMS"]
        self.Motor_Speed = 100
        self.Active = sea["Active"]
        self.Active_Bale = self.Active
        self.Active_SMS = self.Active
        self.Phase = sea["Phase"]
        self.unitId = sea["unitId"]
        self.doc_id = sea.doc_id
        LTime = LastLog.get(self.sensor_id)
        if LTime is not None:
            self.LastLog = datetime.strptime(LTime, time_format)
        else:
            self.LastLog = None

    def send_activity(self, value, time=None):
        self.SenderQ.put(
            {"app": sensor_activity_app_name,
             "data": self.get_data_activity(value, time)})
        self.Active = value
        if not self.lbl_Data_Name == "":
            if not self.OffTime == 0:
                from core.theme.pic import Pics

                if self.Active:
                    self.lbl_Data_Status.setPixmap(Pics.checkMark)
                else:
                    self.lbl_Data_Status.setPixmap(Pics.deleteMark)

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

    def get_data_activity(self, value, time):
        data_temp_activity = dict(self.data_activity_type)
        key = sorted(list(data_temp_activity.keys()), key=self.key_order_activity)

        data_temp_activity[key[0]] = self.sensor_id  # for switch id
        data_temp_activity[key[1]] = value  # for active
        data_temp_activity[key[2]] = self.Tile_Kind  # for Tile_Kind
        data_temp_activity[key[3]] = time  # for time
        return data_temp_activity

    @staticmethod
    def key_order_activity(key):
        import difflib
        app_order = ["Sensor_id", "active", "Tile_Kind", "time"]

        key = difflib.get_close_matches(key, app_order)

        if len(key) != 0:
            if key[0] == "Sensor_id":
                return 1
            elif key[0] == "active":
                return 2
            elif key[0] == "Tile_Kind":
                return 3
            elif key[0] == "time":
                return 4
            else:
                return 0
        else:
            return 0
