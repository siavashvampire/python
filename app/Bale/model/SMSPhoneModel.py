

from core.config.Config import sms_username, sms_password, sms_phone, phone_timeout, sms_phone_send_url


class SMSPhoneData:
    def __init__(self, name, phone, units, phase, access=0):
        self.Name = str(name)
        self.Phone = int(phone)
        self.Units = units
        self.phase = phase
        self.Access = int(access)

    def check_id(self, id):
        if id > 0:
            if -4 in self.Units:
                return True
        if id in self.Units:
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

    def Check(self, id, phase):
        if self.check_id(id) and self.check_phase(phase):
            return True
        return False

    def Send(self, text):
        querystring = {"from": sms_phone, "to": "0" + str(self.Phone), "msg": text, "uname": sms_username,
                       "pass": sms_password}
        response = requests.post(sms_phone_send_url, params=querystring, timeout=phone_timeout)
        return response.text
