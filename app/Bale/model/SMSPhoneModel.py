from core.app_provider.api.get import site_connection
from core.config.Config import sms_username, sms_password, sms_phone, phone_timeout, sms_phone_send_url


class SMSPhoneData:
    def __init__(self, name, phone, units, phase, access=0):
        self.Name = str(name)
        self.Phone = int(phone)
        units = units.split(",")
        self.Units = []
        for i in units:
            self.Units.append(int(i))

        phase = phase.split(",")
        self.phase = []
        for i in phase:
            self.phase.append(int(i))
        self.Access = int(access)

    def check_id(self, id_in):
        if id_in > 0:
            if -4 in self.Units:
                return True
        if id_in in self.Units:
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

    def check(self, id_temp, phase):
        if self.check_id(id_temp) and self.check_phase(phase):
            return True
        return False

    def send(self, text):
        querystring = {"from": sms_phone, "to": "0" + str(self.Phone), "msg": text, "uname": sms_username,
                       "pass": sms_password}

        r = site_connection(sms_phone_send_url, phone_timeout, params=querystring)[1]
        return r
