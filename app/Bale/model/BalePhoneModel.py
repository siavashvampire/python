from telegram import Bot
from tinydb import TinyDB, Query

from app.Bale.model.PhoneModel import PhoneModel
from core.config.Config import phone_db_path, phone_table_name, choose_of_bale


class BalePhoneModel(PhoneModel):
    def __init__(self, name: str = "", id_in: int = 0, send_on_off: bool = False, units: str = "-4", phase: str = "-4",
                 access: bool = False,bot : Bot = None) -> None:
        super().__init__(name=name, phone=id_in, units=units, phase=phase, access=access, choose=choose_of_bale)
        self.bot = bot
        self.SendONOFF = bool(send_on_off)

    def on_off_active(self, send_on_off: bool) -> None:
        self.SendONOFF = bool(send_on_off)
        db = TinyDB(phone_db_path).table(phone_table_name)
        prop = Query()
        db.update({'SendONOFF': int(send_on_off)}, prop.phone == self.phone)
        # Todo: bayad baraye site ham befrese khob

    def get_abs_unit_id(self):
        # TODO:in ghalate bayad doros beshe az in nazar k return type ro nemishe doros moshakhas kard
        if -4 in self.Units:
            return True
        return [i for i in self.Units if i >= 1]

    def check_developer_access(self) -> bool:
        if -2 in self.Units:
            return True
        return False

    def check(self, id_temp: int, phase: int, choose: int) -> bool:
        if self.check_choose(choose):
            if self.SendONOFF or (id_temp < 0):
                if self.check_access():
                    if self.check_id(id_temp) and self.check_phase(phase):
                        return True
        return False

    def set_access(self, value: bool) -> None:
        self.Access = int(value)
        phone_db = TinyDB(phone_db_path).table(phone_table_name)
        phone_prop = Query()
        phone_db.update({'Access': value}, phone_prop.phone == self.phone)

    def get_phase(self):
        # TODO:in ghalate bayad doros beshe az in nazar k return type ro nemishe doros moshakhas kard
        if -4 in self.phase:
            return True
        else:
            return self.phase

    def send(self,text:str):
        self.bot.send_message(self.id, text)