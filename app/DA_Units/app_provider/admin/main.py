from queue import Queue
from typing import Union

from PyQt5.QtWidgets import QLabel
from tinydb import TinyDB, Query
from tinydb.table import Table

from app.DA_Units.model.PLCModels import Delta12SE, GateWay
from app.DA_Units.model.PLCModels import clear_plc_ui
from core.app_provider.api.get import get_from_site_db
from core.config.Config import da_unit_db_path, da_units_get_timeout, main_get_da_unit_url, da_unit_table_name
from core.theme.pic import Pics


class DAUnits:
    electrical_substation_queue: Queue[list[tuple[int, int], dict[str, Union[int, float]]]]
    thread_label: QLabel
    should_stop: bool
    plc_db: Table
    messenger_queue: Queue[list[str, int, int, int]]
    line_monitoring_queue: Queue[list[int, int]]
    units: list[Union[Delta12SE, GateWay]]
    state: bool
    stop_check: bool

    def __init__(self, messenger_queue: Queue[list[str, int, int, int]], line_monitoring_queue: Queue[list[int, int]],
                 electrical_substation_queue: Queue[list[tuple[int, int], dict[str, Union[int, float]]]],
                 thread_label: QLabel) -> None:
        self.thread_label = thread_label
        self.should_stop = False
        self.plc_db = TinyDB(da_unit_db_path).table(da_unit_table_name)
        self.messenger_queue = messenger_queue
        self.line_monitoring_queue = line_monitoring_queue
        self.electrical_substation_queue = electrical_substation_queue
        self.units = []
        self.state = False
        self.stop_check = False
        self.create_units()

    def create_units(self) -> None:
        if len(self.plc_db):
            self.units = []
            for i in self.plc_db.search(Query().type == "PLC_delta_DVP_12SE"):
                self.units.append(Delta12SE(db_id=i.doc_id,
                                            messenger_queue=self.messenger_queue,
                                            line_monitoring_queue=self.line_monitoring_queue))

            for j in self.plc_db.search(Query().type == "MERSAD_GATEWAY"):
                self.units.append(GateWay(db_id=j.doc_id,
                                          messenger_queue=self.messenger_queue,
                                          line_monitoring_queue=self.line_monitoring_queue,
                                          electrical_substation_queue=self.electrical_substation_queue))

            print("PLCsDB Created!")
            print("{} devices connected".format(len(self.units)))
            # for plc in self.units:
            #     plc.run_thread()
        else:
            self.units = []

    def check_da_status(self):
        connect_da = True
        for plc in self.units:
            if not plc.Connected:
                connect_da = 0
        return connect_da

    def check(self):
        alive_plc = True
        for plc in self.units:
            if not (plc.ReadingDataThread.is_alive()):
                alive_plc = False
        if not alive_plc:
            if not self.stop_check:
                for plc in self.units:
                    plc.stop_thread = True
                for plc in self.units:
                    plc.ReadingDataThread.join()
                for plc in self.units:
                    plc.restart_thread()
            if self.state:
                self.thread_label.setIcon(Pics.OFF)
                self.state = False
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
        for plc in self.units:
            plc.stop_thread = True
        for plc in self.units:
            if plc.ReadingDataThread.is_alive():
                plc.ReadingDataThread.join()
            else:
                print("plc " + plc.Name + " not alive")
        #     TODO:check konim bebinim age ghablesh tamom shode bashe join mide
        self.stop_check = True
        self.state = False
        self.thread_label.setIcon(Pics.OFF)
        print("stop Da units")

    def start_func(self):
        for plc in self.units:
            plc.stop_thread = False
            plc.restart_thread()
        self.stop_check = False
        self.state = True
        self.thread_label.setIcon(Pics.ON)

    def submit_plc(self):
        for plc in self.units:
            plc.stop_thread = True
        for plc in self.units:
            plc.ReadingDataThread.join()
        clear_plc_ui(self)
        self.create_units()

    @staticmethod
    def read_all_units():
        get_from_site_db(get_url=main_get_da_unit_url, get_timeout=da_units_get_timeout, db_path=da_unit_db_path,
                         table_name=da_unit_table_name)

    def update_system(self, where_should_update: tuple[str] = ()) -> None:
        self.read_all_units()

        self.should_stop = True
        self.state_thread(state=False, program=True)

        self.create_units()

        self.should_stop = False
        self.state_thread(state=True, program=True)
