from datetime import datetime

from tinydb import TinyDB, Query

from core.config.Config import switch_db_path, off_cam_switch_value, on_cam_switch_value, time_format, switch_table_name
from core.model.DataType import switch_activity_data, switch_activity_app, switch_activity_class, switch_activity_method


class CamSwitch:
    PLC_id: int
    doc_id: int

    def __init__(self, switch_id=0, name="", unit_id=None, phase=None, active=False, sender_queue=None):
        self.label = name
        self.Switch_id = switch_id
        self.doc_id = 0
        self.Active = active
        self.SenderQ = sender_queue
        self.phase = phase
        self.phaseLabel = phase
        self.unit = unit_id
        self.data_type = switch_activity_data
        if self.Switch_id:
            self.update()

    def send(self, value):
        bale_report_flag = False
        sms_report_flag = False
        if value == off_cam_switch_value:
            value = 0
        if value == on_cam_switch_value:
            value = 1

        self.SenderQ.put(
            {"app": switch_activity_app,
             "class": switch_activity_class,
             "method": switch_activity_method,
             "data": self.get_data(value, datetime.now().strftime(time_format))})
        self.Active = value
        return bale_report_flag, sms_report_flag

    def update(self):
        switch_id = self.Switch_id
        prop = Query()
        switch_db = TinyDB(switch_db_path).table(switch_table_name)
        sea = switch_db.search(prop.id == switch_id)
        if sea:
            sea = sea[0]
            self.PLC_id = int(sea["PLC_id"])
            self.label = sea["label"]
            self.Active = sea["Active"]
            self.phase = sea["phase"]
            self.phaseLabel = sea["phaseLabel"]
            self.unit = sea["unit"]
            self.doc_id = sea.doc_id

    def get_data(self, value, time):
        data_temp = dict(self.data_type)
        key = sorted(list(data_temp.keys()), key=self.key_order)

        data_temp[key[0]] = self.Switch_id  # for switch id
        data_temp[key[1]] = value  # for active
        if value:
            data_temp[key[1]] = 1  # for active
        else:
            data_temp[key[1]] = 0  # for active
        data_temp[key[2]] = time  # for time
        return data_temp

    @staticmethod
    def key_order(key):
        import difflib
        app_order = ["Switch_id", "active", "time"]

        key = difflib.get_close_matches(key, app_order)

        if len(key) != 0:
            if key[0] == "Switch_id":
                return 1
            elif key[0] == "active":
                return 2
            elif key[0] == "time":
                return 3
            else:
                return 0
        else:
            return 0


def find_switch_choose(choose: int, switches: list[CamSwitch]) -> CamSwitch:
    for sw in switches:
        if sw.PLC_id == choose:
            return sw
    return CamSwitch()
