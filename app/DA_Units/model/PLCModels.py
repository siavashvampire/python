import threading
import winsound
from datetime import datetime
from queue import Queue
from threading import Thread
from time import sleep
from typing import Callable, Union

from PyQt5.QtGui import QPixmap
from dateutil.relativedelta import relativedelta
from persiantools.jdatetime import JalaliDateTime
from pyModbusTCP import utils
from pyModbusTCP.client import ModbusClient
from tinydb import TinyDB

import app.Logging.app_provider.admin.MersadLogging as Logging
from app.ElectricalSubstation.app_provider.admin.main import get_devices_by_substation_id
from app.ElectricalSubstation.model.Device import Device
from app.LineMonitoring.app_provider.api.LastLog import getABSecond, getText
from app.LineMonitoring.app_provider.api.ReadText import PLCConnectBaleText, PLCDisconnectBaleText, VirtualText
from core.config.Config import da_unit_db_path, modbus_timeout, plc_time_sleep_max, plc_time_sleep_min, \
    plc_refresh_time, \
    plc_sleep_time_step_up, plc_sleep_time_step_down, disconnect_alarm_time, send_time_format, da_unit_table_name, \
    time_between_read_from_each_device
from core.config.Config import register_for_data, register_for_counter, register_for_start_read, register_for_end_read


def clear_plc_ui(ui) -> None:
    for i in range(4):
        ui.lineEdit_Name[i].setText("")
        ui.lineEdit_IP[i].setText("")
        ui.lineEdit_TestPort[i].setText("")
        ui.lbl_Test_Virtual[i].setText("")
        ui.PLC_Status_lbl[i].setText("")
        ui.PLC_Status_lbl[i].setStyleSheet("background: transparent")
        ui.PLC_Counter_lbl[i].setText("")
        ui.PLC_Counter_lbl[i].setStyleSheet("background: transparent")
        ui.PLC_Status_lbl[i].clear()
        ui.checkBox_Test_Virtual[i].setEnabled(False)
        ui.checkBox_Counter[i].setEnabled(False)
        ui.checkBox_Counter[i].setChecked(False)
        ui.checkBox_Test_Virtual[i].setChecked(False)


def extract_choose(data: int) -> tuple[int, int]:
    choose = data % 1000
    data = (data // 1000) * 1000
    return choose, data


def electrical_extract_choose(data: dict[str, Union[int, float]]) -> tuple[int, int]:
    return data['substation_id'], data['unitId']


class Delta12SE:
    DBid: int
    deleteMark: QPixmap
    checkMark: QPixmap
    ret_num: int
    disc_msg_sent: bool
    Connected: bool
    first_good: bool
    first_bad: bool
    SleepTime: int
    ReadCounter: int
    DataCounter: int
    DPS: int
    RPS: int
    TimeDis: datetime
    DiffTime: relativedelta
    thread_func: Callable[[Callable[[], bool]], None]
    MessengerQ: Queue[list[str, int, int, int]]
    line_monitoring_queue: Queue[list[int, int]]
    stop_thread: bool
    ReadingDataThread: Thread
    Port: int
    TestPort: int
    app_name: str
    IP: str
    Name: str
    client: ModbusClient

    def __init__(self, db_id: int = 0, ip: str = "192.168.1.240", port: int = 502, name: str = "", test_port: int = 0,
                 messenger_queue: Queue[list[str, int, int, int]] = None,
                 app_name: str = "LineMonitoring",
                 line_monitoring_queue: Queue[list[int, int]] = None) -> None:
        from core.theme.pic import Pics

        self.DBid = db_id
        self.deleteMark = Pics.deleteMark
        self.checkMark = Pics.checkMark
        self.Port = port
        self.TestPort = test_port
        self.IP = ip
        self.Name = name
        self.app_name = app_name
        self.ret_num = 0
        self.disc_msg_sent = False
        self.Connected = False
        self.first_good = True
        self.first_bad = True
        self.SleepTime = 0
        self.ReadCounter = 0
        self.DataCounter = 0
        self.DPS = 0
        self.RPS = 0

        self.TimeDis = datetime.now()
        self.DiffTime = relativedelta()

        if messenger_queue is not None:
            self.MessengerQ = messenger_queue

        self.line_monitoring_queue = line_monitoring_queue
        self.stop_thread = False

        if db_id:
            self.update()

        # if self.DBid < 5 and UI is not None:
        #     self.PLC_Status_lbl = UI.PLC_Status_lbl[self.DBid - 1]
        #     self.PLC_Counter_lbl = UI.PLC_Counter_lbl[self.DBid - 1]
        #     self.lbl_Test = UI.lbl_Test_Virtual[self.DBid - 1]
        #     self.checkBox_Test = UI.checkBox_Test_Virtual[self.DBid - 1]
        #     self.checkBox_Counter = UI.checkBox_Counter[self.DBid - 1]
        #     self.Name_LE = UI.lineEdit_Name[self.DBid - 1]
        #     self.IP_LE = UI.lineEdit_IP[self.DBid - 1]
        #     self.TestPort_LE = UI.lineEdit_TestPort[self.DBid - 1]
        #
        #     self.Name_LE.setText(str(self.Name))
        #     self.IP_LE.setText(str(self.IP))
        #     self.TestPort_LE.setText(str(self.TestPort))
        # else:
        #     self.PLC_Status_lbl = ""
        #     self.PLC_Counter_lbl = ""
        #     self.lbl_Test = ""
        #     self.checkBox_Test = ""
        #     self.checkBox_Counter = ""
        #     self.Name_LE = ""
        #     self.IP_LE = ""
        #     self.TestPort_LE = ""

    def run_thread(self):
        self.ReadingDataThread.start()
        Logging.da_log("Init PLC " + self.Name, "PLC " + self.Name + " start")

    def update(self):
        sea = TinyDB(da_unit_db_path).table(da_unit_table_name).get(doc_id=self.DBid)
        self.Port = 502
        self.TestPort = int(sea["testPort"])
        self.app_name = sea["app"]
        self.IP = sea["IP"]
        self.Name = sea["label"]

        self.client = ModbusClient(host=self.IP, port=self.Port, auto_open=True, auto_close=False,
                                   timeout=modbus_timeout, debug=False)

        if self.app_name == "LineMonitoring":
            self.thread_func = self.line_monitoring_read_data_from_plc_thread

        self.ReadingDataThread = threading.Thread(target=self.thread_func,
                                                  args=(lambda: self.stop_thread,))

        # TODO: age app dg bod chi kar kone??

    def disconnect(self):
        if self.first_bad:
            try:
                winsound.Beep(5000, 100)
                winsound.Beep(4000, 100)
                winsound.Beep(3000, 100)
            except Exception as e:
                pass

            self.Connected = False
            self.first_good = True
            self.first_bad = False
            self.TimeDis = datetime.now()
            # self.PLC_Status_lbl.setPixmap(self.deleteMark)
            # self.PLC_Counter_lbl.setStyleSheet("background-color: red;color: white;")
            # self.checkBox_Test.setEnabled(False)
            # self.checkBox_Test.setChecked(False)
            # self.checkBox_Counter.setEnabled(False)
            # self.checkBox_Counter.setChecked(False)

        # self.PLC_Counter_lbl.setText(str(self.ret_num))
        self.DiffTime = relativedelta(datetime.now(), self.TimeDis)
        if getABSecond(self.DiffTime) > disconnect_alarm_time and (not self.disc_msg_sent):
            self.disc_msg_sent = True
            now1 = JalaliDateTime.to_jalali(self.TimeDis).strftime(send_time_format)

            self.MessengerQ.put([PLCDisconnectBaleText.format(Name=self.Name, Time=now1), -1, -4, 1])
            self.MessengerQ.put([PLCDisconnectBaleText.format(Name=self.Name, Time=now1), -1, -4, 2])
            Logging.da_log("Disconnected", "PLC " + self.Name + " Disconnected")

    def connect(self):
        if self.first_good:

            try:
                winsound.Beep(3000, 100)
                winsound.Beep(4000, 100)
                winsound.Beep(5000, 100)
            except:
                pass
            if self.disc_msg_sent:
                now1 = JalaliDateTime.to_jalali(datetime.now()).strftime(send_time_format)
                self.MessengerQ.put(
                    [PLCConnectBaleText.format(Name=self.Name, DiffTime=getText(self.DiffTime), Time=now1), -1, -4, 1])
                self.MessengerQ.put(
                    [PLCConnectBaleText.format(Name=self.Name, DiffTime=getText(self.DiffTime), Time=now1), -1, -4, 2])
                Logging.da_log("Connected", "PLC " + self.Name + " Connected")

            print("connected to PLC {} after {}".format(self.Name, getText(self.DiffTime)))
            self.ret_num = 0
            # self.PLC_Counter_lbl.setStyleSheet("background-color: rgba(" + GreenColor + ");color: white;")
            # self.PLC_Counter_lbl.setText(str(self.ret_num))
            # self.PLC_Status_lbl.setPixmap(self.checkMark)
            # self.checkBox_Test.setEnabled(True)
            # self.checkBox_Counter.setEnabled(True)

            self.Connected = True
            self.first_bad = True
            self.first_good = False
            self.disc_msg_sent = False

    def test(self, data):
        if self.MessengerQ is not None:
            self.MessengerQ.put([VirtualText.format(Name=self.Name, format=self.TestPort, data=data), -2, -4, 1])
            self.MessengerQ.put([VirtualText.format(Name=self.Name, format=self.TestPort, data=data), -2, -4, 2])
        # self.lbl_Test.setText(str(data))

    def counter(self):
        data = int(self.client.read_holding_registers(register_for_counter, 1)[0])
        if data > 32767:
            data = data - 65536
        self.ret_num = data
        # self.PLC_Counter_lbl.setText(str(self.ret_num))

    def cal_sleep_time(self):
        dps = self.DPS * 1.2
        if not (dps * 1.3 > self.RPS > dps):
            if dps >= self.RPS:
                self.SleepTime -= plc_sleep_time_step_down
            else:
                self.SleepTime += plc_sleep_time_step_up
        if self.SleepTime <= plc_time_sleep_min:
            self.SleepTime = plc_time_sleep_min
        if self.SleepTime >= plc_time_sleep_max:
            self.SleepTime = plc_time_sleep_max
        self.SleepTime = round(self.SleepTime, 2)

    def restart_thread(self):
        if not (self.ReadingDataThread.is_alive()):
            self.stop_thread = False
            self.ReadingDataThread = threading.Thread(target=self.thread_func,
                                                      args=(lambda: self.stop_thread,))
            self.ReadingDataThread.start()
            Logging.da_log("Restart PLC " + self.Name, "PLC " + self.Name + " restart")

    def line_monitoring_read_data_from_plc_thread(self, stop_thread: Callable[[], bool]) -> None:
        sleep(1)
        now_sleep = datetime.now()
        while True:
            if stop_thread():
                Logging.da_log("Reading Data Thread " + self.Name, "PLC " + self.Name + " Stop")
                print("stop PLC " + self.Name)
                break
            sleep(self.SleepTime)
            try:
                # plc_is_open = self.client.is_open()
                plc_is_open = self.client.open()
                if not plc_is_open:
                    self.ReadCounter = 0
                    self.DataCounter = 0
                    self.ret_num += 1
                    print("PLC " + str(self.Name) + " disconnected! | retry number : " + str(self.ret_num))
                    self.disconnect()

                if plc_is_open:
                    self.ReadCounter += 1
                    if (datetime.now() - now_sleep).seconds >= plc_refresh_time:
                        now_sleep = datetime.now()
                        self.DPS = self.DataCounter
                        self.RPS = self.ReadCounter
                        self.ReadCounter = 0
                        self.DataCounter = 0
                        # if not self.checkBox_Counter.isChecked():
                        #     self.PLC_Counter_lbl.setText(str(self.RPS / PLCRefreshTime))
                        self.cal_sleep_time()
                    data, choose = self.line_monitoring_read_data_from_plc()
                    if data is not None:
                        if data:
                            self.DataCounter += 1
                            self.line_monitoring_queue.put([data, choose])

                    self.connect()
                    # if self.checkBox_Test.isChecked():
                    #     self.client.write_single_coil(RegisterForTest, 1)
                    # else:
                    #     self.client.write_single_coil(RegisterForTest, 0)
                    #
                    # if self.checkBox_Counter.isChecked():
                    #     self.SleepTime = 0
                    #     try:
                    #         self.Counter()
                    #     except:
                    #         pass
            except Exception as e:
                Logging.da_log("send and receive " + str(self.DBid), str(e))
                break

    def line_monitoring_read_data_from_plc(self):
        self.client.write_single_coil(register_for_start_read, True)
        data = self.client.read_holding_registers(register_for_data, 1)
        self.client.write_single_coil(register_for_end_read, True)
        if data is not None:
            data = int(data[0])
            if data:
                choose, data = extract_choose(data)
                if choose == int(self.TestPort):
                    self.test(data)
                    return 0, None
                return data, choose
            else:
                return 0, None
        else:
            return None, None


class GateWay:
    DBid: int
    deleteMark: QPixmap
    checkMark: QPixmap
    ret_num: int
    disc_msg_sent: bool
    Connected: bool
    first_good: bool
    first_bad: bool
    SleepTime: int
    ReadCounter: int
    DataCounter: int
    DPS: int
    RPS: int
    TimeDis: datetime
    DiffTime: relativedelta
    read_data: bool
    MessengerQ: Queue[list[str, int, int, int]]
    line_monitoring_queue: Queue[list[int, int]]
    electrical_substation_queue: Queue[list[tuple[int, int], dict[str, Union[int, float]]]]
    thread_func: Callable[[Callable[[], bool]], None]
    stop_thread: bool
    Port: int
    TestPort: int
    IP: str
    Name: str
    client: ModbusClient
    ReadingDataThread: Thread
    electrical_devices: list[Device]
    electrical_substation_id: int
    app_name: str

    def __init__(self, db_id: int = 0, ip: str = "192.168.1.237", port: int = 502, name: str = "", test_port: int = 0,
                 messenger_queue: Queue[list[str, int, int, int]] = None,
                 app_name: str = "ElectricalSubstation_0",
                 line_monitoring_queue: Queue[list[int, int]] = None,
                 electrical_substation_queue: Queue[
                     list[tuple[int, int], dict[str, Union[int, float]]]] = None) -> None:
        from core.theme.pic import Pics

        self.DBid = db_id
        self.deleteMark = Pics.deleteMark
        self.checkMark = Pics.checkMark
        self.Port = port
        self.TestPort = test_port
        self.IP = ip
        self.Name = name
        self.app_name = app_name
        self.ret_num = 0
        self.disc_msg_sent = False
        self.Connected = False
        self.first_good = True
        self.first_bad = True
        self.SleepTime = 0
        self.ReadCounter = 0
        self.DataCounter = 0
        self.DPS = 0
        self.RPS = 0
        self.read_data = False

        self.TimeDis = datetime.now()
        self.DiffTime = relativedelta()

        if messenger_queue is not None:
            self.MessengerQ = messenger_queue

        self.line_monitoring_queue = line_monitoring_queue
        self.electrical_substation_queue = electrical_substation_queue
        self.stop_thread = False

        if db_id:
            self.update()

        # if self.DBid < 5 and UI is not None:
        #     self.PLC_Status_lbl = UI.PLC_Status_lbl[self.DBid - 1]
        #     self.PLC_Counter_lbl = UI.PLC_Counter_lbl[self.DBid - 1]
        #     self.lbl_Test = UI.lbl_Test_Virtual[self.DBid - 1]
        #     self.checkBox_Test = UI.checkBox_Test_Virtual[self.DBid - 1]
        #     self.checkBox_Counter = UI.checkBox_Counter[self.DBid - 1]
        #     self.Name_LE = UI.lineEdit_Name[self.DBid - 1]
        #     self.IP_LE = UI.lineEdit_IP[self.DBid - 1]
        #     self.TestPort_LE = UI.lineEdit_TestPort[self.DBid - 1]
        #
        #     self.Name_LE.setText(str(self.Name))
        #     self.IP_LE.setText(str(self.IP))
        #     self.TestPort_LE.setText(str(self.TestPort))
        # else:
        #     self.PLC_Status_lbl = ""
        #     self.PLC_Counter_lbl = ""
        #     self.lbl_Test = ""
        #     self.checkBox_Test = ""
        #     self.checkBox_Counter = ""
        #     self.Name_LE = ""
        #     self.IP_LE = ""
        #     self.TestPort_LE = ""

    def run_thread(self) -> None:
        self.ReadingDataThread.start()
        Logging.da_log("Init PLC " + self.Name, "PLC " + self.Name + " start")

    def update(self) -> None:
        sea = TinyDB(da_unit_db_path).table(da_unit_table_name).get(doc_id=self.DBid)
        self.Port = 502
        self.TestPort = sea["testPort"]
        self.app_name = sea["app"]
        self.IP = sea["IP"]
        self.Name = sea["label"]

        if self.app_name == "Mersad Monitoring System":
            self.thread_func = self.line_monitoring_read_data_from_plc_thread
        elif "ElectricalSubstation" in self.app_name:
            s = self.app_name.split("_")
            self.app_name = s[0]
            self.electrical_substation_id = int(s[1])
            self.electrical_devices = get_devices_by_substation_id(self.electrical_substation_id)
            self.thread_func = self.electrical_substation_read_data_from_plc_thread

        self.client = ModbusClient(host=self.IP, port=self.Port, auto_open=True, auto_close=False,
                                   timeout=modbus_timeout, debug=False)

        self.ReadingDataThread = threading.Thread(target=self.thread_func,
                                                  args=(lambda: self.stop_thread,))

    def disconnect(self) -> None:
        if self.first_bad:
            try:
                winsound.Beep(5000, 100)
                winsound.Beep(4000, 100)
                winsound.Beep(3000, 100)
            except Exception as e:
                pass

            self.Connected = False
            self.first_good = True
            self.first_bad = False
            self.TimeDis = datetime.now()
            # self.PLC_Status_lbl.setPixmap(self.deleteMark)
            # self.PLC_Counter_lbl.setStyleSheet("background-color: red;color: white;")
            # self.checkBox_Test.setEnabled(False)
            # self.checkBox_Test.setChecked(False)
            # self.checkBox_Counter.setEnabled(False)
            # self.checkBox_Counter.setChecked(False)

        # self.PLC_Counter_lbl.setText(str(self.ret_num))
        self.DiffTime = relativedelta(datetime.now(), self.TimeDis)
        if getABSecond(self.DiffTime) > disconnect_alarm_time and (not self.disc_msg_sent):
            self.disc_msg_sent = True
            now1 = JalaliDateTime.to_jalali(self.TimeDis).strftime(send_time_format)

            self.MessengerQ.put([PLCDisconnectBaleText.format(Name=self.Name, Time=now1), -1, -4, 1])
            self.MessengerQ.put([PLCDisconnectBaleText.format(Name=self.Name, Time=now1), -1, -4, 2])
            Logging.da_log("Disconnected", "PLC " + self.Name + " Disconnected")

    def connect(self) -> None:
        if self.first_good:

            try:
                winsound.Beep(3000, 100)
                winsound.Beep(4000, 100)
                winsound.Beep(5000, 100)
            except Exception as e:
                pass
            if self.disc_msg_sent:
                now1 = JalaliDateTime.to_jalali(datetime.now()).strftime(send_time_format)
                self.MessengerQ.put(
                    [PLCConnectBaleText.format(Name=self.Name, DiffTime=getText(self.DiffTime), Time=now1), -1, -4, 1])
                self.MessengerQ.put(
                    [PLCConnectBaleText.format(Name=self.Name, DiffTime=getText(self.DiffTime), Time=now1), -1, -4, 2])
                Logging.da_log("Connected", "PLC " + self.Name + " Connected")

            print("connected to PLC {} after {}".format(self.Name, getText(self.DiffTime)))
            self.ret_num = 0
            # self.PLC_Counter_lbl.setStyleSheet("background-color: rgba(" + GreenColor + ");color: white;")
            # self.PLC_Counter_lbl.setText(str(self.ret_num))
            # self.PLC_Status_lbl.setPixmap(self.checkMark)
            # self.checkBox_Test.setEnabled(True)
            # self.checkBox_Counter.setEnabled(True)

            self.Connected = True
            self.first_bad = True
            self.first_good = False
            self.disc_msg_sent = False

    def test(self, data: int) -> None:
        """
        test DAUnits that is alive or not with make a port on and
        Args:
            data: the amount of time that sensor is on in second
        """
        if self.MessengerQ is not None:
            self.MessengerQ.put([VirtualText.format(Name=self.Name, format=self.TestPort, data=data), -2, -4, 1])
            self.MessengerQ.put([VirtualText.format(Name=self.Name, format=self.TestPort, data=data), -2, -4, 2])
        # self.lbl_Test.setText(str(data))

    def counter(self) -> None:
        data = int(self.client.read_holding_registers(register_for_counter, 1)[0])
        if data > 32767:
            data = data - 65536
        self.ret_num = data
        # self.PLC_Counter_lbl.setText(str(self.ret_num))

    def cal_sleep_time(self) -> None:
        dps = self.DPS * 1.2
        if not (dps * 1.3 > self.RPS > dps):
            if dps >= self.RPS:
                self.SleepTime -= plc_sleep_time_step_down
            else:
                self.SleepTime += plc_sleep_time_step_up
        if self.SleepTime <= plc_time_sleep_min:
            self.SleepTime = plc_time_sleep_min
        if self.SleepTime >= plc_time_sleep_max:
            self.SleepTime = plc_time_sleep_max

        if self.read_data:
            self.SleepTime += time_between_read_from_each_device
            self.read_data = False
        self.SleepTime = round(self.SleepTime, 2)

    def restart_thread(self) -> None:
        if not (self.ReadingDataThread.is_alive()):
            self.stop_thread = False
            self.ReadingDataThread = threading.Thread(target=self.thread_func,
                                                      args=(lambda: self.stop_thread,))
            self.ReadingDataThread.start()
            Logging.da_log("Restart PLC " + self.Name, "PLC " + self.Name + " restart")

    def line_monitoring_read_data_from_plc_thread(self, stop_thread: Callable[[], bool]) -> None:
        sleep(1)
        now_sleep = datetime.now()
        while True:
            if stop_thread():
                Logging.da_log("Reading Data Thread " + self.Name, "PLC " + self.Name + " Stop")
                print("stop gateway " + self.Name)
                break
            sleep(self.SleepTime)
            try:
                # plc_is_open = self.client.is_open()
                plc_is_open = self.client.open()
                if not plc_is_open:
                    self.ReadCounter = 0
                    self.DataCounter = 0
                    self.ret_num += 1
                    print("PLC " + str(self.Name) + " disconnected! | retry number : " + str(self.ret_num))
                    self.disconnect()

                if plc_is_open:
                    self.ReadCounter += 1
                    if (datetime.now() - now_sleep).seconds >= plc_refresh_time:
                        now_sleep = datetime.now()
                        self.DPS = self.DataCounter
                        self.RPS = self.ReadCounter
                        self.ReadCounter = 0
                        self.DataCounter = 0
                        # if not self.checkBox_Counter.isChecked():
                        #     self.PLC_Counter_lbl.setText(str(self.RPS / PLCRefreshTime))
                        self.cal_sleep_time()
                    data, choose = self.line_monitoring_read_data_from_plc()
                    if data is not None:
                        if data:
                            self.DataCounter += 1
                            self.line_monitoring_queue.put([data, choose])

                    self.connect()
                    # if self.checkBox_Test.isChecked():
                    #     self.client.write_single_coil(RegisterForTest, 1)
                    # else:
                    #     self.client.write_single_coil(RegisterForTest, 0)
                    #
                    # if self.checkBox_Counter.isChecked():
                    #     self.SleepTime = 0
                    #     try:
                    #         self.Counter()
                    #     except:
                    #         pass
            except Exception as e:
                Logging.da_log("send and receive " + str(self.DBid), str(e))
                break

    def line_monitoring_read_data_from_plc(self):
        # Todo:in doros nashode bayad doros she az nazar annotation
        self.client.write_single_coil(register_for_start_read, True)
        data = self.client.read_holding_registers(register_for_data, 1)
        self.client.write_single_coil(register_for_end_read, True)
        if data is not None:
            data = int(data[0])
            if data:
                choose, data = extract_choose(data)
                if choose == int(self.TestPort):
                    self.test(data)
                    return 0, None
                return data, choose
            else:
                return 0, None
        else:
            return None, None

    def electrical_substation_read_data_from_plc_thread(self, stop_thread: Callable[[], bool]) -> None:
        sleep(1)
        now_sleep = datetime.now()
        while True:
            if stop_thread():
                Logging.da_log("Reading Data Thread " + self.Name, "PLC " + self.Name + " Stop")
                print("stop gateway " + self.Name)
                break

            for i in self.electrical_devices:
                this_unit_id = i.unit
                sleep(self.SleepTime)
                try:
                    # plc_is_open = self.client.is_open()
                    plc_is_open = self.client.open()

                    if not plc_is_open:
                        self.ReadCounter = 0
                        self.DataCounter = 0
                        self.ret_num += 1

                        print("PLC " + str(self.Name) + " disconnected! | retry number : " + str(self.ret_num))
                        self.disconnect()

                    if plc_is_open:
                        self.ReadCounter += 1
                        if (datetime.now() - now_sleep).seconds >= plc_refresh_time:
                            now_sleep = datetime.now()
                            self.DPS = self.DataCounter
                            self.RPS = self.ReadCounter
                            self.ReadCounter = 0
                            self.DataCounter = 0
                            # if not self.checkBox_Counter.isChecked():
                            #     self.PLC_Counter_lbl.setText(str(self.RPS / PLCRefreshTime))
                            self.cal_sleep_time()

                        if (datetime.now() - i.last_read_time_from_device).seconds >= i.refresh_time:
                            data = self.electrical_substation_data_from_plc(this_unit_id)
                            i.last_read_time_from_device = datetime.now()

                            if data["substation_id"] != 0:
                                if data:
                                    self.DataCounter += 1
                                    self.read_data = True
                                    self.cal_sleep_time()
                                    choose = electrical_extract_choose(data)
                                    self.electrical_substation_queue.put([choose, data])
                            else:
                                pass
                                # TODO: vaghti k none has gozaresh bede to log
                                # print("data from unit {} is None!".format(this_unit_id))

                        self.connect()

                except Exception as e:
                    print(e)
                    Logging.da_log("send and receive " + str(self.DBid), str(e))
                    break

    def electrical_substation_data_from_plc(self, rs_485_address: int) -> dict[str, Union[int, float]]:
        self.client.unit_id(rs_485_address)

        incoming_data_part1 = self.multiple_register_read("holding", 3000, 17, "FLOAT32")
        # print(incoming_data_part1)
        num = incoming_data_part1[0]
        if not num != num:
            incoming_data_part2 = self.multiple_register_read("holding", 3036, 21, "FLOAT32")
            incoming_data_part3 = self.multiple_register_read("holding", 3078, 8, "4Q_FP_PF")
            incoming_data_part4 = self.multiple_register_read("holding", 3110, 1, "FLOAT32")
            incoming_data_part5 = self.multiple_register_read("holding", 3194, 1, "FLOAT32")
            incoming_data_part6 = self.multiple_register_read("holding", 3204, 12, "INT64")
            incoming_data_part7 = self.multiple_register_read("holding", 3272, 4, "INT64")
            incoming_data_part8 = self.multiple_register_read("holding", 3304, 12, "INT64")
            incoming_data_part9 = self.multiple_register_read("holding", 3518, 9, "INT64")
            try:
                if incoming_data_part1 is not None:
                    incoming_data = incoming_data_part1 + \
                                    incoming_data_part2 + \
                                    incoming_data_part3 + \
                                    incoming_data_part4 + \
                                    incoming_data_part5 + \
                                    incoming_data_part6 + \
                                    incoming_data_part7 + \
                                    incoming_data_part8 + \
                                    incoming_data_part9
                else:
                    return {"substation_id": 0}

                dict_data_out = {
                    "substation_id": self.electrical_substation_id,
                    "unitId": rs_485_address,
                    "Current_A": incoming_data[0],
                    "Current_B": incoming_data[1],
                    "Current_C": incoming_data[2],
                    "Current_N": incoming_data[3],
                    "Current_G": incoming_data[4],
                    "Current_Avg": incoming_data[5],

                    "Current_Unbalance_A": incoming_data[6],
                    "Current_Unbalance_B": incoming_data[7],
                    "Current_Unbalance_C": incoming_data[8],
                    "Current_Unbalance_Worst": incoming_data[9],

                    "Voltage_A_B": incoming_data[10],
                    "Voltage_B_C": incoming_data[11],
                    "Voltage_C_A": incoming_data[12],
                    "Voltage_L_L_Avg": incoming_data[13],
                    "Voltage_A_N": incoming_data[14],
                    "Voltage_B_N": incoming_data[15],
                    "Voltage_C_N": incoming_data[16],
                    "Voltage_L_N_Avg": incoming_data[17],

                    "Voltage_Unbalance_A_B": incoming_data[18],
                    "Voltage_Unbalance_B_C": incoming_data[19],
                    "Voltage_Unbalance_C_A": incoming_data[20],
                    "Voltage_Unbalance_L_L_Worst": incoming_data[21],
                    "Voltage_Unbalance_A_N": incoming_data[22],
                    "Voltage_Unbalance_B_N": incoming_data[23],
                    "Voltage_Unbalance_C_N": incoming_data[24],
                    "Voltage_Unbalance_L_N_Worst": incoming_data[25],

                    "Active_Power_A": incoming_data[26],
                    "Active_Power_B": incoming_data[27],
                    "Active_Power_C": incoming_data[28],
                    "Active_Power_Total": incoming_data[29],
                    "Reactive_Power_A": incoming_data[30],
                    "Reactive_Power_B": incoming_data[31],
                    "Reactive_Power_C": incoming_data[32],
                    "Reactive_Power_Total": incoming_data[33],
                    "Apparent_Power_A": incoming_data[34],
                    "Apparent_Power_B": incoming_data[35],
                    "Apparent_Power_C": incoming_data[36],
                    "Apparent_Power_Total": incoming_data[37],

                    "Power_Factor_A": incoming_data[38],
                    "Power_Factor_B": incoming_data[39],
                    "Power_Factor_C": incoming_data[40],
                    # "Power_Factor_Total": incoming_data[41],
                    "Power_Factor_Total": incoming_data[47],
                    "Displacement_Power_Factor_A": incoming_data[42],
                    "Displacement_Power_Factor_B": incoming_data[43],
                    "Displacement_Power_Factor_C": incoming_data[44],
                    "Displacement_Power_Factor_Total": incoming_data[45],

                    "Frequency": incoming_data[46],

                    # "Power_Factor_Total_IEEE": incoming_data[47],

                    "Active_Energy_Delivered_Into_Load": incoming_data[48],
                    "Active_Energy_Received_Out_of_Load": incoming_data[49],
                    "Active_Energy_Delivered_Pos_Received": incoming_data[50],
                    "Active_Energy_Delivered_Neg_Received": incoming_data[51],
                    "Reactive_Energy_Delivered": incoming_data[52],
                    "Reactive_Energy_Received": incoming_data[53],
                    "Reactive_Energy_Delivered_Pos_Received": incoming_data[54],
                    "Reactive_Energy_Delivered_Neg_Received": incoming_data[55],
                    "Apparent_Energy_Delivered": incoming_data[56],
                    "Apparent_Energy_Received": incoming_data[57],
                    "Apparent_Energy_Delivered_Pos_Received": incoming_data[58],
                    "Apparent_Energy_Delivered_Neg_Received": incoming_data[59],

                    "Reactive_Energy_in_Quadrant_I": incoming_data[60],
                    "Reactive_Energy_in_Quadrant_II": incoming_data[61],
                    "Reactive_Energy_in_Quadrant_III": incoming_data[62],
                    "Reactive_Energy_in_Quadrant_IV": incoming_data[63],

                    "Active_Energy_Delivered_Into_Load_Permanent": incoming_data[64],
                    "Active_Energy_Received_Out_of_Load_Permanent": incoming_data[65],
                    "Active_Energy_Delivered_Pos_Received_Permanent": incoming_data[66],
                    "Active_Energy_Delivered_Neg_Received_Permanent": incoming_data[67],
                    "Reactive_Energy_Delivered_Permanent": incoming_data[68],
                    "Reactive_Energy_Received_Permanent": incoming_data[69],
                    "Reactive_Energy_Delivered_Pos_Received_Permanent": incoming_data[70],
                    "Reactive_Energy_Delivered_Neg_Received_Permanent": incoming_data[71],
                    "Apparent_Energy_Delivered_Permanent": incoming_data[72],
                    "Apparent_Energy_Received_Permanent": incoming_data[73],
                    "Apparent_Energy_Delivered_Pos_Received_Permanent": incoming_data[74],
                    "Apparent_Energy_Delivered_Neg_Received_Permanent": incoming_data[75],

                    "Active_Energy_Delivered_Phase_A": incoming_data[76],
                    "Active_Energy_Delivered_Phase_B": incoming_data[77],
                    "Active_Energy_Delivered_Phase_C": incoming_data[78],
                    "Reactive_Energy_Delivered_Phase_A": incoming_data[79],
                    "Reactive_Energy_Delivered_Phase_B": incoming_data[80],
                    "Reactive_Energy_Delivered_Phase_C": incoming_data[81],
                    "Apparent_Energy_Delivered_Phase_A": incoming_data[82],
                    "Apparent_Energy_Delivered_Phase_B": incoming_data[83],
                    "Apparent_Energy_Delivered_Phase_C": incoming_data[84]
                }

                # json_data_out = json.dumps(dict_data_out, indent=2)

                return dict_data_out

            except:
                print("Error in Read Data From PM2100")
        else:
            return {"substation_id": 0}

    def single_register_read(self, _input_or_holding, _address, _data_type, _big_endian=False):
        data = 0
        if _data_type == "32bit_float":
            if _input_or_holding == "input":
                data = self.client.read_input_registers(_address, 2)
            if _input_or_holding == "holding":
                data = self.client.read_holding_registers(_address, 2)
            if data:
                list_32_bits = utils.word_list_to_long(data, big_endian=_big_endian)
                float_32bit_val = round(utils.decode_ieee(list_32_bits[0]), 2)

                return float_32bit_val

        if _data_type == "16bit_uint":
            if _input_or_holding == "input":
                data = self.client.read_input_registers(_address, 1)
            if _input_or_holding == "holding":
                data = self.client.read_holding_registers(_address, 1)

            if data:
                uint_16bit_val = data[0]

                return uint_16bit_val

    def multiple_register_read(self, _input_or_holding, _address, _length, _data_type, _big_endian=False):
        data = 0
        if _data_type == "FLOAT32":
            list_float_32bit = []
            if _input_or_holding == "input":
                data = self.client.read_input_registers(_address, 2 * _length)
            if _input_or_holding == "holding":
                data = self.client.read_holding_registers(_address, 2 * _length)
            if data:
                list_32_bits = utils.word_list_to_long(data, big_endian=_big_endian)
                for val in list_32_bits:
                    list_float_32bit.append(round(utils.decode_ieee(val), 2))

                return list_float_32bit

        if _data_type == "INT16":
            if _input_or_holding == "input":
                data = self.client.read_input_registers(_address, _length)
            if _input_or_holding == "holding":
                data = self.client.read_holding_registers(_address, _length)
            if data:
                list_uint_16bit = data

                return list_uint_16bit

        if _data_type == "4Q_FP_PF":
            list_4_q_fp_pf = []
            if _input_or_holding == "input":
                data = self.client.read_input_registers(_address, _length * 2)
            if _input_or_holding == "holding":
                data = self.client.read_holding_registers(_address, _length * 2)
            if data:
                list_32_bits = utils.word_list_to_long(data, big_endian=_big_endian)
                for val in list_32_bits:
                    list_4_q_fp_pf.append(round(utils.decode_ieee(val), 2))

                return list_4_q_fp_pf

        if _data_type == "INT64":
            list_int_64 = []
            if _input_or_holding == "input":
                data = self.client.read_input_registers(_address, _length * 4)
            if _input_or_holding == "holding":
                data = self.client.read_holding_registers(_address, _length * 4)
            if data:
                while len(data) >= 4:
                    this_int_64 = (data[0:4][3] << 16 * 3) + (data[0:4][2] << 16 * 2) + (data[0:4][1] << 16 * 1) + \
                                  data[0:4][
                                      0]
                    list_int_64.append(this_int_64)
                    del data[0:4]

                return list_int_64

    def read_on_timer(self):
        self.client.unit_id(13)
        a = self.multiple_register_read("input", 1, 1, "INT64")
        if a:
            if a[0]:
                sec = a[0] / 1000
                minute = sec / 60
                hour = minute / 60

                print("sec = ", round(sec, 1), " | ", "min = ", round(minute, 1), " | ", "hour = ", round(hour, 1))
                return sec, minute, hour

        return -1, -1, -1

    def read_on_board_sensors(self):
        self.client.unit_id(13)
        a = self.multiple_register_read("input", 1000, 1, "INT16")
        if a:
            if a[0]:
                # print(a[0])
                return a[0]

        return -1

    def read_temperature(self):
        self.client.unit_id(13)
        a = self.multiple_register_read("input", 5, 1, "FLOAT32")
        if a:
            if a[0]:
                # print(a[0])
                return a[0]

        return -1
