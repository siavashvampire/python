from datetime import datetime
from typing import Union

from tinydb import TinyDB, Query

from core.config.Config import time_format, device_table_name, device_db_path
from core.model.DataType import Device_new_log_app, Device_new_log_class, Device_new_log_method, \
    Device_new_log_data


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

        data_temp[key[9]] = value['Current_Unbalance_A']
        data_temp[key[10]] = value['Current_Unbalance_B']
        data_temp[key[11]] = value['Current_Unbalance_C']
        data_temp[key[12]] = value['Current_Unbalance_Worst']

        data_temp[key[13]] = value['Voltage_A_B']
        data_temp[key[14]] = value['Voltage_B_C']
        data_temp[key[15]] = value['Voltage_C_A']
        data_temp[key[16]] = value['Voltage_L_L_Avg']
        data_temp[key[17]] = value['Voltage_A_N']
        data_temp[key[18]] = value['Voltage_B_N']
        data_temp[key[19]] = value['Voltage_C_N']
        data_temp[key[20]] = value['Voltage_L_N_Avg']

        data_temp[key[21]] = value['Voltage_Unbalance_A_B']
        data_temp[key[22]] = value['Voltage_Unbalance_B_C']
        data_temp[key[23]] = value['Voltage_Unbalance_C_A']
        data_temp[key[24]] = value['Voltage_Unbalance_L_L_Worst']
        data_temp[key[25]] = value['Voltage_Unbalance_A_N']
        data_temp[key[26]] = value['Voltage_Unbalance_B_N']
        data_temp[key[27]] = value['Voltage_Unbalance_C_N']
        data_temp[key[28]] = value['Voltage_Unbalance_L_N_Worst']

        data_temp[key[29]] = value['Active_Power_A']
        data_temp[key[30]] = value['Active_Power_B']
        data_temp[key[31]] = value['Active_Power_C']
        data_temp[key[32]] = value['Active_Power_Total']
        data_temp[key[33]] = value['Reactive_Power_A']
        data_temp[key[34]] = value['Reactive_Power_B']
        data_temp[key[35]] = value['Reactive_Power_C']
        data_temp[key[36]] = value['Reactive_Power_Total']
        data_temp[key[37]] = value['Apparent_Power_A']
        data_temp[key[38]] = value['Apparent_Power_B']
        data_temp[key[39]] = value['Apparent_Power_C']
        data_temp[key[40]] = value['Apparent_Power_Total']

        data_temp[key[41]] = value['Power_Factor_A']
        data_temp[key[42]] = value['Power_Factor_B']
        data_temp[key[43]] = value['Power_Factor_C']
        data_temp[key[44]] = value['Power_Factor_Total']
        data_temp[key[45]] = value['Displacement_Power_Factor_A']
        data_temp[key[46]] = value['Displacement_Power_Factor_B']
        data_temp[key[47]] = value['Displacement_Power_Factor_C']
        data_temp[key[48]] = value['Displacement_Power_Factor_Total']

        data_temp[key[49]] = value['Frequency']

        data_temp[key[50]] = value['Active_Energy_Delivered_Into_Load']
        data_temp[key[51]] = value['Active_Energy_Received_Out_of_Load']
        data_temp[key[52]] = value['Active_Energy_Delivered_Pos_Received']
        data_temp[key[53]] = value['Active_Energy_Delivered_Neg_Received']
        data_temp[key[54]] = value['Reactive_Energy_Delivered']
        data_temp[key[55]] = value['Reactive_Energy_Received']
        data_temp[key[56]] = value['Reactive_Energy_Delivered_Pos_Received']
        data_temp[key[57]] = value['Reactive_Energy_Delivered_Neg_Received']
        data_temp[key[58]] = value['Apparent_Energy_Delivered']
        data_temp[key[59]] = value['Apparent_Energy_Received']
        data_temp[key[60]] = value['Apparent_Energy_Delivered_Pos_Received']
        data_temp[key[61]] = value['Apparent_Energy_Delivered_Neg_Received']

        data_temp[key[62]] = value['Reactive_Energy_in_Quadrant_I']
        data_temp[key[63]] = value['Reactive_Energy_in_Quadrant_II']
        data_temp[key[64]] = value['Reactive_Energy_in_Quadrant_III']
        data_temp[key[65]] = value['Reactive_Energy_in_Quadrant_IV']

        data_temp[key[66]] = value['Active_Energy_Delivered_Into_Load_Permanent']
        data_temp[key[67]] = value['Active_Energy_Received_Out_of_Load_Permanent']
        data_temp[key[68]] = value['Active_Energy_Delivered_Pos_Received_Permanent']
        data_temp[key[69]] = value['Active_Energy_Delivered_Neg_Received_Permanent']
        data_temp[key[70]] = value['Reactive_Energy_Delivered_Permanent']
        data_temp[key[71]] = value['Reactive_Energy_Received_Permanent']
        data_temp[key[72]] = value['Reactive_Energy_Delivered_Pos_Received_Permanent']
        data_temp[key[73]] = value['Reactive_Energy_Delivered_Neg_Received_Permanent']
        data_temp[key[74]] = value['Apparent_Energy_Delivered_Permanent']
        data_temp[key[75]] = value['Apparent_Energy_Received_Permanent']
        data_temp[key[76]] = value['Apparent_Energy_Delivered_Pos_Received_Permanent']
        data_temp[key[77]] = value['Apparent_Energy_Delivered_Neg_Received_Permanent']

        data_temp[key[78]] = value['Active_Energy_Delivered_Phase_A']
        data_temp[key[79]] = value['Active_Energy_Delivered_Phase_B']
        data_temp[key[80]] = value['Active_Energy_Delivered_Phase_C']
        data_temp[key[81]] = value['Reactive_Energy_Delivered_Phase_A']
        data_temp[key[82]] = value['Reactive_Energy_Delivered_Phase_B']
        data_temp[key[83]] = value['Reactive_Energy_Delivered_Phase_C']
        data_temp[key[84]] = value['Apparent_Energy_Delivered_Phase_A']
        data_temp[key[85]] = value['Apparent_Energy_Delivered_Phase_B']
        data_temp[key[86]] = value['Apparent_Energy_Delivered_Phase_C']

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
                     "Current_Unbalance_A",
                     "Current_Unbalance_B",
                     "Current_Unbalance_C",
                     "Current_Unbalance_Worst",
                     "Voltage_A_B",
                     "Voltage_B_C",
                     "Voltage_C_A",
                     "Voltage_L_L_Avg",
                     "Voltage_A_N",
                     "Voltage_B_N",
                     "Voltage_C_N",
                     "Voltage_L_N_Avg",
                     "Voltage_Unbalance_A_B",
                     "Voltage_Unbalance_B_C",
                     "Voltage_Unbalance_C_A",
                     "Voltage_Unbalance_L_L_Worst",
                     "Voltage_Unbalance_A_N",
                     "Voltage_Unbalance_B_N",
                     "Voltage_Unbalance_C_N",
                     "Voltage_Unbalance_L_N_Worst",
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
                     "Active_Energy_Delivered_Into_Load",
                     "Active_Energy_Received_Out_of_Load",
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
                     "Reactive_Energy_in_Quadrant_I",
                     "Reactive_Energy_in_Quadrant_II",
                     "Reactive_Energy_in_Quadrant_III",
                     "Reactive_Energy_in_Quadrant_IV",
                     "Active_Energy_Delivered_Into_Load_Permanent",
                     "Active_Energy_Received_Out_of_Load_Permanent",
                     "Active_Energy_Delivered_Pos_Received_Permanent",
                     "Active_Energy_Delivered_Neg_Received_Permanent",
                     "Reactive_Energy_Delivered_Permanent",
                     "Reactive_Energy_Received_Permanent",
                     "Reactive_Energy_Delivered_Pos_Received_Permanent",
                     "Reactive_Energy_Delivered_Neg_Received_Permanent",
                     "Apparent_Energy_Delivered_Permanent",
                     "Apparent_Energy_Received_Permanent",
                     "Apparent_Energy_Delivered_Pos_Received_Permanent",
                     "Apparent_Energy_Delivered_Neg_Received_Permanent",
                     "Active_Energy_Delivered_Phase_A",
                     "Active_Energy_Delivered_Phase_B",
                     "Active_Energy_Delivered_Phase_C",
                     "Reactive_Energy_Delivered_Phase_A",
                     "Reactive_Energy_Delivered_Phase_B",
                     "Reactive_Energy_Delivered_Phase_C",
                     "Apparent_Energy_Delivered_Phase_A",
                     "Apparent_Energy_Delivered_Phase_B",
                     "Apparent_Energy_Delivered_Phase_C"]

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
            elif key == "Current_Unbalance_A":
                return 10
            elif key == "Current_Unbalance_B":
                return 11
            elif key == "Current_Unbalance_C":
                return 12
            elif key == "Current_Unbalance_Worst":
                return 13
            elif key == "Voltage_A_B":
                return 14
            elif key == "Voltage_B_C":
                return 15
            elif key == "Voltage_C_A":
                return 16
            elif key == "Voltage_L_L_Avg":
                return 17
            elif key == "Voltage_A_N":
                return 18
            elif key == "Voltage_B_N":
                return 19
            elif key == "Voltage_C_N":
                return 20
            elif key == "Voltage_L_N_Avg":
                return 21
            elif key == "Voltage_Unbalance_A_B":
                return 22
            elif key == "Voltage_Unbalance_B_C":
                return 23
            elif key == "Voltage_Unbalance_C_A":
                return 24
            elif key == "Voltage_Unbalance_L_L_Worst":
                return 25
            elif key == "Voltage_Unbalance_A_N":
                return 26
            elif key == "Voltage_Unbalance_B_N":
                return 27
            elif key == "Voltage_Unbalance_C_N":
                return 28
            elif key == "Voltage_Unbalance_L_N_Worst":
                return 29
            elif key == "Active_Power_A":
                return 30
            elif key == "Active_Power_B":
                return 31
            elif key == "Active_Power_C":
                return 32
            elif key == "Active_Power_Total":
                return 33
            elif key == "Reactive_Power_A":
                return 34
            elif key == "Reactive_Power_B":
                return 35
            elif key == "Reactive_Power_C":
                return 36
            elif key == "Reactive_Power_Total":
                return 38
            elif key == "Apparent_Power_A":
                return 39
            elif key == "Apparent_Power_B":
                return 40
            elif key == "Apparent_Power_C":
                return 41
            elif key == "Apparent_Power_Total":
                return 42
            elif key == "Power_Factor_A":
                return 43
            elif key == "Power_Factor_B":
                return 44
            elif key == "Power_Factor_C":
                return 45
            elif key == "Power_Factor_Total":
                return 46
            elif key == "Displacement_Power_Factor_A":
                return 47
            elif key == "Displacement_Power_Factor_B":
                return 48
            elif key == "Displacement_Power_Factor_C":
                return 49
            elif key == "Displacement_Power_Factor_Total":
                return 50
            elif key == "Frequency":
                return 51
            elif key == "Active_Energy_Delivered_Into_Load":
                return 52
            elif key == "Active_Energy_Received_Out_of_Load":
                return 53
            elif key == "Active_Energy_Delivered_Pos_Received":
                return 54
            elif key == "Active_Energy_Delivered_Neg_Received":
                return 55
            elif key == "Reactive_Energy_Delivered":
                return 56
            elif key == "Reactive_Energy_Received":
                return 57
            elif key == "Reactive_Energy_Delivered_Pos_Received":
                return 58
            elif key == "Reactive_Energy_Delivered_Neg_Received":
                return 59
            elif key == "Apparent_Energy_Delivered":
                return 60
            elif key == "Apparent_Energy_Received":
                return 61
            elif key == "Apparent_Energy_Delivered_Pos_Received":
                return 62
            elif key == "Apparent_Energy_Delivered_Neg_Received":
                return 63
            elif key == "Reactive_Energy_in_Quadrant_I":
                return 64
            elif key == "Reactive_Energy_in_Quadrant_II":
                return 65
            elif key == "Reactive_Energy_in_Quadrant_III":
                return 66
            elif key == "Reactive_Energy_in_Quadrant_IV":
                return 67
            elif key == "Active_Energy_Delivered_Into_Load_Permanent":
                return 68
            elif key == "Active_Energy_Received_Out_of_Load_Permanent":
                return 69
            elif key == "Active_Energy_Delivered_Pos_Received_Permanent":
                return 70
            elif key == "Active_Energy_Delivered_Neg_Received_Permanent":
                return 71
            elif key == "Reactive_Energy_Delivered_Permanent":
                return 72
            elif key == "Reactive_Energy_Received_Permanent":
                return 73
            elif key == "Reactive_Energy_Delivered_Pos_Received_Permanent":
                return 74
            elif key == "Reactive_Energy_Delivered_Neg_Received_Permanent":
                return 75
            elif key == "Apparent_Energy_Delivered_Permanent":
                return 76
            elif key == "Apparent_Energy_Received_Permanent":
                return 77
            elif key == "Apparent_Energy_Delivered_Pos_Received_Permanent":
                return 78
            elif key == "Apparent_Energy_Delivered_Neg_Received_Permanent":
                return 79
            elif key == "Active_Energy_Delivered_Phase_A":
                return 80
            elif key == "Active_Energy_Delivered_Phase_B":
                return 81
            elif key == "Active_Energy_Delivered_Phase_C":
                return 82
            elif key == "Reactive_Energy_Delivered_Phase_A":
                return 83
            elif key == "Reactive_Energy_Delivered_Phase_B":
                return 84
            elif key == "Reactive_Energy_Delivered_Phase_C":
                return 85
            elif key == "Apparent_Energy_Delivered_Phase_A":
                return 86
            elif key == "Apparent_Energy_Delivered_Phase_B":
                return 87
            elif key == "Apparent_Energy_Delivered_Phase_C":
                return 88
            else:
                return 0


def find_device(choose: tuple[int], devices: list[Device]) -> Device:
    substation = choose[0]
    unit = choose[1]
    for this_device in devices:
        if this_device.substation == substation:
            if this_device.unit == unit:
                # print(this_device.substation_name)
                return this_device
    return Device()
