from tinydb import TinyDB, Query

from core.config.Config import phone_db_path, phone_table_name


class PhoneData:
    def __init__(self, name: str = "", id_in: int = 0, send_on_off: bool = False, units: str = "-4", phase: str = "-4",
                 access: bool = False) -> None:
        self.Name = str(name)
        self.id = int(id_in)
        self.SendONOFF = bool(send_on_off)
        units = units.split(",")
        self.Units = []
        for i in units:
            self.Units.append(int(i))

        phase = phase.split(",")
        self.phase = []
        for i in phase:
            self.phase.append(int(i))

        self.Access = int(access)

    def on_off_active(self, send_on_off: bool) -> None:
        self.SendONOFF = bool(send_on_off)
        db = TinyDB(phone_db_path).table(phone_table_name)
        prop = Query()
        db.update({'SendONOFF': int(send_on_off)}, prop.id == self.id)

    def check_id(self, id_temp: int) -> bool:
        if id_temp > 0:
            if -4 in self.Units:
                return True
        if id_temp in self.Units:
            return True
        return False

    def check_phase(self, phase: int) -> bool:
        if phase == -4:
            return True
        if -4 in self.phase:
            return True
        if phase in self.phase:
            return True
        return False

    def get_abs_unit_id(self):
        # TODO:in ghalate bayad doros beshe az in nazar k return type ro nemishe doros moshakhas kard
        if -4 in self.Units:
            return True
        return [i for i in self.Units if i >= 1]

    def check_developer_access(self) -> bool:
        if -2 in self.Units:
            return True
        return False

    def check_access(self) -> bool:
        if self.Access:
            return True
        return False

    def check(self, id_temp: int, phase: int) -> bool:
        if self.check_id(id_temp) and self.check_phase(phase):
            return True
        return False

    def set_access(self, value: bool) -> None:
        self.Access = int(value)
        phone_db = TinyDB(phone_db_path).table(phone_table_name)
        phone_prop = Query()
        phone_db.update({'Access': value}, phone_prop.id == self.id)

    def get_phase(self):
        # TODO:in ghalate bayad doros beshe az in nazar k return type ro nemishe doros moshakhas kard
        if -4 in self.phase:
            return True
        else:
            return self.phase
