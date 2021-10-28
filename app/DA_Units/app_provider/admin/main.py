from tinydb import TinyDB, Query

from app.DA_Units.model.PLCModels import Delta12SE, GateWay
from app.DA_Units.model.PLCModels import clear_plc_ui
from core.app_provider.api.get import get_from_site_db
from core.config.Config import da_unit_db_path, da_units_get_timeout, main_get_da_unit_url, da_unit_table_name
from core.theme.pic import Pics


class DAUnits:
    def __init__(self, messenger_q, line_monitoring_queue, electrical_substation_queue, thread_label):
        self.thread_label = thread_label
        self.should_stop = False
        self.plc_db = TinyDB(da_unit_db_path).table(da_unit_table_name)
        self.messenger_q = messenger_q
        self.line_monitoring_queue = line_monitoring_queue
        self.electrical_substation_queue = electrical_substation_queue
        self.units = []
        self.state = False
        self.stop_check = False
        # self.update_system()
        # TODO:update system bayad baresh darim
        self.create_units()

    def create_units(self):
        if len(self.plc_db):
            self.units = []
            for i in self.plc_db.search(Query().type == "PLC_delta_DVP_12SE"):
                self.units.append(Delta12SE(db_id=i.doc_id,
                                            messenger_queue=self.messenger_q,
                                            line_monitoring_queue=self.line_monitoring_queue,
                                            electrical_substation_queue=self.electrical_substation_queue))

            for j in self.plc_db.search(Query().type == "MERSAD_GATEWAY"):
                self.units.append(GateWay(db_id=j.doc_id,
                                          messenger_queue=self.messenger_q,
                                          line_monitoring_queue=self.line_monitoring_queue,
                                          electrical_substation_queue=self.electrical_substation_queue))

            # TODO:bayad joda she bayad jaye all bashe onaie k fght PLC hastan v onaie k fght gateway hastan
            print("PLCsDB Created!")
            for plc in self.units:
                plc.run_thread()
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
                print(plc.Name)
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
            plc.ReadingDataThread.join()
        #     TODO:check konim bebinim age ghablesh tamom shode bashe join mide
        self.stop_check = True
        self.state = False
        self.thread_label.setIcon(Pics.OFF)
        print("stop Line")

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

    def update_system(self):
        self.read_all_units()
        self.create_units()
