import pywhatkit

from core.config.Config import choose_of_whatsApp


class PhoneModel:
    def __init__(self, choose: int, name: str, phone: int, units: str, phase: str, access: bool = 0) -> None:
        self.Name = str(name)
        self.id = int(phone)
        units = units.split(",")
        self.Units = []
        for i in units:
            self.Units.append(int(i))

        phase = phase.split(",")
        self.phase = []
        for i in phase:
            self.phase.append(int(i))
        self.Access = int(access)
        self.__choose = choose

    def check_id(self, id_in: int) -> bool:
        if id_in > 0:
            if -4 in self.Units:
                return True
        if id_in in self.Units:
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

    def check(self, id_temp: int, phase: int, choose: int) -> bool:
        if self.check_choose(choose):
            if self.check_access():
                if self.check_id(id_temp) and self.check_phase(phase):
                    return True
        return False

    def check_choose(self, choose: int) -> bool:
        return choose == self.__choose

    def check_access(self) -> bool:
        if self.Access:
            return True
        return False
