from datetime import datetime
from typing import Union

from tinydb import TinyDB, Query

from core.config.Config import time_format, device_table_name, device_db_path
from core.model.DataType import Device_new_log_app, Device_new_log_class, Device_new_log_method, \
    Device_new_log_data


# TODO:inja bayad y done device dashte bashim k beshe class parent baraye ina

class Device:
    substation: int
    unit: int
    data_type: dict[str, Union[int, str]]
    last_read_time_from_device: datetime
    substation_name: str
    name: str
    device_type: int
    refresh_time: int
    doc_id: int

    def __init__(self, substation: int = 0, substation_name: str = None, unit: int = 0, name: str = None,
                 device_type: int = None,
                 refresh_time: int = None,
                 sender_queue=None) -> None:
        self.substation = substation
        self.substation_name = substation_name
        self.unit = unit
        self.name = name
        self.device_type = device_type
        self.refresh_time = refresh_time
        self.data_type = Device_new_log_data
        self.sender_queue = sender_queue
        self.last_read_time_from_device = datetime.now()

        if self.substation and self.unit:
            self.update()

    def send(self, values: dict[str, Union[int, float]]) -> None:
        # print("ta send omad")
        if self.sender_queue is not None:
            self.sender_queue.put(
                {"app": Device_new_log_app,
                 "class": Device_new_log_class,
                 "method": Device_new_log_method,
                 "data": self.get_data(values, datetime.now().strftime(time_format))})

    def update(self) -> None:
        substation: int = self.substation
        unit: int = self.unit
        prop = Query()
        db = TinyDB(device_db_path).table(device_table_name)
        sea = db.search((prop.substation_id == substation) & (prop.unitId == unit))
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

    def get_data(self, value: dict[str, Union[int, float]], time: str) -> dict[str, Union[int, float]]:

        data_temp = dict(self.data_type)
        key = sorted(list(data_temp.keys()), key=self.key_order)

        data_temp[key[0]] = value['substation_id']
        data_temp[key[1]] = value['unitId']
        data_temp[key[2]] = time

        data_temp[key[3]] = value['Current_A']
        data_temp[key[4]] = value['Current_B']
        data_temp[key[5]] = value['Current_C']
        data_temp[key[6]] = value['Current_N']
        data_temp[key[7]] = value['Current_G']
        data_temp[key[8]] = value['Current_Avg']

        data_temp[key[9]] = value['Voltage_A_B']
        data_temp[key[10]] = value['Voltage_B_C']
        data_temp[key[11]] = value['Voltage_C_A']
        data_temp[key[12]] = value['Voltage_L_L_Avg']
        data_temp[key[13]] = value['Voltage_A_N']
        data_temp[key[14]] = value['Voltage_B_N']
        data_temp[key[15]] = value['Voltage_C_N']
        data_temp[key[16]] = value['Voltage_L_N_Avg']

        data_temp[key[17]] = value['Active_Power_A']
        data_temp[key[18]] = value['Active_Power_B']
        data_temp[key[19]] = value['Active_Power_C']
        data_temp[key[20]] = value['Active_Power_Total']
        data_temp[key[21]] = value['Reactive_Power_A']
        data_temp[key[22]] = value['Reactive_Power_B']
        data_temp[key[23]] = value['Reactive_Power_C']
        data_temp[key[24]] = value['Reactive_Power_Total']
        data_temp[key[25]] = value['Apparent_Power_A']
        data_temp[key[26]] = value['Apparent_Power_B']
        data_temp[key[27]] = value['Apparent_Power_C']
        data_temp[key[28]] = value['Apparent_Power_Total']

        data_temp[key[29]] = value['Power_Factor_A']
        data_temp[key[30]] = value['Power_Factor_B']
        data_temp[key[31]] = value['Power_Factor_C']
        data_temp[key[32]] = value['Power_Factor_Total']
        data_temp[key[33]] = value['Displacement_Power_Factor_A']
        data_temp[key[34]] = value['Displacement_Power_Factor_B']
        data_temp[key[35]] = value['Displacement_Power_Factor_C']
        data_temp[key[36]] = value['Displacement_Power_Factor_Total']

        data_temp[key[37]] = value['Frequency']

        data_temp[key[38]] = value['Active_Energy_Delivered']
        data_temp[key[39]] = value['Active_Energy_Received']
        data_temp[key[40]] = value['Active_Energy_Delivered_Pos_Received']
        data_temp[key[41]] = value['Active_Energy_Delivered_Neg_Received']
        data_temp[key[42]] = value['Reactive_Energy_Delivered']
        data_temp[key[43]] = value['Reactive_Energy_Received']
        data_temp[key[44]] = value['Reactive_Energy_Delivered_Pos_Received']
        data_temp[key[45]] = value['Reactive_Energy_Delivered_Neg_Received']
        data_temp[key[46]] = value['Apparent_Energy_Delivered']
        data_temp[key[47]] = value['Apparent_Energy_Received']
        data_temp[key[48]] = value['Apparent_Energy_Delivered_Pos_Received']
        data_temp[key[49]] = value['Apparent_Energy_Delivered_Neg_Received']

        data_temp[key[50]] = value['Active_Power_Last_Demand']
        data_temp[key[51]] = value['Reactive_Power_Last_Demand']
        data_temp[key[52]] = value['Apparent_Power_Last_Demand']

        data_temp[key[53]] = value['Current_Avg_Last_Demand']
        data_temp[key[54]] = value['Current_Avg_Present_Demand']
        data_temp[key[55]] = value['Current_Avg_Predicted_Demand']
        data_temp[key[56]] = value['Current_Avg_Peak_Demand']
        data_temp[key[57]] = value['Current_Avg_PK_DT_Demand']

        data_temp[key[58]] = value['Active_Power_Present_Demand']
        data_temp[key[59]] = value['Active_Power_Predicted_Demand']
        data_temp[key[60]] = value['Active_Power_Peak_Demand']
        data_temp[key[61]] = value['Active_Power_PK_DT_Demand']
        data_temp[key[62]] = value['Reactive_Power_Present_Demand']
        data_temp[key[63]] = value['Reactive_Power_Predicted_Demand']
        data_temp[key[64]] = value['Reactive_Power_Peak_Demand']
        data_temp[key[65]] = value['Reactive_Power_PK_DT_Demand']
        data_temp[key[66]] = value['Apparent_Power_Present_Demand']
        data_temp[key[67]] = value['Apparent_Power_Predicted_Demand']
        data_temp[key[68]] = value['Apparent_Power_Peak_Demand']
        data_temp[key[69]] = value['Apparent_Power_PK_DT_Demand']

        for val in list(data_temp.keys()):
            if data_temp[val] != data_temp[val]:
                data_temp.pop(val)

        return data_temp

    @staticmethod
    def key_order(key: str) -> int:
        import difflib
        app_order = ["substation_id",
                     "unitId",
                     "Start_time",
                     "Current_A",
                     "Current_B",
                     "Current_C",
                     "Current_N",
                     "Current_G",
                     "Current_Avg",
                     "Voltage_A_B",
                     "Voltage_B_C",
                     "Voltage_C_A",
                     "Voltage_L_L_Avg",
                     "Voltage_A_N",
                     "Voltage_B_N",
                     "Voltage_C_N",
                     "Voltage_L_N_Avg",
                     "Active_Power_A",
                     "Active_Power_B",
                     "Active_Power_C",
                     "Active_Power_Total",
                     "Reactive_Power_A",
                     "Reactive_Power_B",
                     "Reactive_Power_C",
                     "Reactive_Power_Total",
                     "Apparent_Power_A",
                     "Apparent_Power_B",
                     "Apparent_Power_C",
                     "Apparent_Power_Total",
                     "Power_Factor_A",
                     "Power_Factor_B",
                     "Power_Factor_C",
                     "Power_Factor_Total",
                     "Displacement_Power_Factor_A",
                     "Displacement_Power_Factor_B",
                     "Displacement_Power_Factor_C",
                     "Displacement_Power_Factor_Total",
                     "Frequency",
                     "Active_Energy_Delivered",
                     "Active_Energy_Received",
                     "Active_Energy_Delivered_Pos_Received",
                     "Active_Energy_Delivered_Neg_Received",
                     "Reactive_Energy_Delivered",
                     "Reactive_Energy_Received",
                     "Reactive_Energy_Delivered_Pos_Received",
                     "Reactive_Energy_Delivered_Neg_Received",
                     "Apparent_Energy_Delivered",
                     "Apparent_Energy_Received",
                     "Apparent_Energy_Delivered_Pos_Received",
                     "Apparent_Energy_Delivered_Neg_Received",
                     "Active_Power_Last_Demand",
                     "Reactive_Power_Last_Demand",
                     "Apparent_Power_Last_Demand",
                     "Current_Avg_Last_Demand",
                     "Current_Avg_Present_Demand",
                     "Current_Avg_Predicted_Demand",
                     "Current_Avg_Peak_Demand",
                     "Current_Avg_PK_DT_Demand",
                     "Active_Power_Present_Demand",
                     "Active_Power_Predicted_Demand",
                     "Active_Power_Peak_Demand",
                     "Active_Power_PK_DT_Demand",
                     "Reactive_Power_Present_Demand",
                     "Reactive_Power_Predicted_Demand",
                     "Reactive_Power_Peak_Demand",
                     "Reactive_Power_PK_DT_Demand",
                     "Apparent_Power_Present_Demand",
                     "Apparent_Power_Predicted_Demand",
                     "Apparent_Power_Peak_Demand",
                     "Apparent_Power_PK_DT_Demand"]

        key = difflib.get_close_matches(key, app_order)

        if len(key) != 0:
            key = key[0]
            if key == "substation_id":
                return 1
            elif key == "unitId":
                return 2
            elif key == "Start_time":
                return 3
            elif key == "Current_A":
                return 4
            elif key == "Current_B":
                return 5
            elif key == "Current_C":
                return 6
            elif key == "Current_N":
                return 7
            elif key == "Current_G":
                return 8
            elif key == "Current_Avg":
                return 9
            elif key == "Voltage_A_B":
                return 10
            elif key == "Voltage_B_C":
                return 11
            elif key == "Voltage_C_A":
                return 12
            elif key == "Voltage_L_L_Avg":
                return 13
            elif key == "Voltage_A_N":
                return 14
            elif key == "Voltage_B_N":
                return 15
            elif key == "Voltage_C_N":
                return 16
            elif key == "Voltage_L_N_Avg":
                return 17
            elif key == "Active_Power_A":
                return 18
            elif key == "Active_Power_B":
                return 19
            elif key == "Active_Power_C":
                return 20
            elif key == "Active_Power_Total":
                return 21
            elif key == "Reactive_Power_A":
                return 22
            elif key == "Reactive_Power_B":
                return 23
            elif key == "Reactive_Power_C":
                return 24
            elif key == "Reactive_Power_Total":
                return 25
            elif key == "Apparent_Power_A":
                return 26
            elif key == "Apparent_Power_B":
                return 27
            elif key == "Apparent_Power_C":
                return 28
            elif key == "Apparent_Power_Total":
                return 29
            elif key == "Power_Factor_A":
                return 30
            elif key == "Power_Factor_B":
                return 31
            elif key == "Power_Factor_C":
                return 32
            elif key == "Power_Factor_Total":
                return 33
            elif key == "Displacement_Power_Factor_A":
                return 34
            elif key == "Displacement_Power_Factor_B":
                return 35
            elif key == "Displacement_Power_Factor_C":
                return 36
            elif key == "Displacement_Power_Factor_Total":
                return 37
            elif key == "Frequency":
                return 38
            elif key == "Active_Energy_Delivered":
                return 39
            elif key == "Active_Energy_Received":
                return 40
            elif key == "Active_Energy_Delivered_Pos_Received":
                return 41
            elif key == "Active_Energy_Delivered_Neg_Received":
                return 42
            elif key == "Reactive_Energy_Delivered":
                return 43
            elif key == "Reactive_Energy_Received":
                return 44
            elif key == "Reactive_Energy_Delivered_Pos_Received":
                return 45
            elif key == "Reactive_Energy_Delivered_Neg_Received":
                return 46
            elif key == "Apparent_Energy_Delivered":
                return 47
            elif key == "Apparent_Energy_Received":
                return 48
            elif key == "Apparent_Energy_Delivered_Pos_Received":
                return 49
            elif key == "Apparent_Energy_Delivered_Neg_Received":
                return 50
            elif key == "Active_Power_Last_Demand":
                return 51
            elif key == "Active_Power_Present_Demand":
                return 52
            elif key == "Active_Power_Predicted_Demand":
                return 53
            elif key == "Active_Power_Peak_Demand":
                return 54
            elif key == "Active_Power_PK_DT_Demand":
                return 55
            elif key == "Reactive_Power_Last_Demand":
                return 56
            elif key == "Reactive_Power_Present_Demand":
                return 57
            elif key == "Reactive_Power_Predicted_Demand":
                return 58
            elif key == "Reactive_Power_Peak_Demand":
                return 59
            elif key == "Reactive_Power_PK_DT_Demand":
                return 60
            elif key == "Apparent_Power_Last_Demand":
                return 61
            elif key == "Apparent_Power_Present_Demand":
                return 62
            elif key == "Apparent_Power_Predicted_Demand":
                return 63
            elif key == "Apparent_Power_Peak_Demand":
                return 64
            elif key == "Apparent_Power_PK_DT_Demand":
                return 65
            elif key == "Current_Avg_Last_Demand":
                return 66
            elif key == "Current_Avg_Present_Demand":
                return 67
            elif key == "Current_Avg_Predicted_Demand":
                return 68
            elif key == "Current_Avg_Peak_Demand":
                return 69
            elif key == "Current_Avg_PK_DT_Demand":
                return 70

            else:
                return 0


def find_device(choose: tuple[int], devices: list[Device]) -> Device:
    substation = choose[0]
    unit = choose[1]
    for this_device in devices:
        if this_device.substation == substation:
            if this_device.unit == unit:
                return this_device
    return Device()
