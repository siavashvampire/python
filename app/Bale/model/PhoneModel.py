from tinydb import TinyDB, Query

from core.config.Config import phone_db_path, phone_table_name


class PhoneData:
    def __init__(self, name, id_in, send_on_off, units, phase, access=0):
        self.Name = str(name)
        self.id = int(id_in)
        self.SendONOFF = int(send_on_off)
        units = units.split(",")
        self.Units = []
        for i in units:
            self.Units.append(int(i))

        phase = phase.split(",")
        self.phase = []
        for i in phase:
            self.phase.append(int(i))

        self.Access = int(access)

    def on_off_active(self, send_on_off):
        self.SendONOFF = send_on_off
        phone_db = TinyDB(phone_db_path).table(phone_table_name)
        phone_prop = Query()
        phone_db.update({'SendONOFF': send_on_off}, phone_prop.id == self.id)

    def check_id(self, id_temp):
        if id_temp > 0:
            if -4 in self.Units:
                return True
        if id_temp in self.Units:
            return True
        return False

    def check_phase(self, phase):
        if phase == -4:
            return True
        if -4 in self.phase:
            return True
        if phase in self.phase:
            return True
        return False

    def get_abs_unit_id(self):
        if -4 in self.Units:
            return True
        return [i for i in self.Units if i >= 1]

    def check_developer_access(self):
        if -2 in self.Units:
            return True
        return False

    def check_access(self):
        if self.Access:
            return True
        return False

    def check(self, id_temp, phase):
        if self.check_id(id_temp) and self.check_phase(phase):
            return True
        return False

    def set_access(self, value):
        self.Access = int(value)
        phone_db = TinyDB(phone_db_path).table(phone_table_name)
        phone_prop = Query()
        phone_db.update({'Access': value}, phone_prop.id == self.id)

    def get_phase(self):
        if -4 in self.phase:
            return True
        else:
            return self.phase
