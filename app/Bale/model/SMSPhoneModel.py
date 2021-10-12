

from core.config.Config import SMSusername, SMSpassword, SMSPhone, PhoneTimeout, SMSPhoneURL


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
        querystring = {"from": SMSPhone, "to": "0" + str(self.Phone), "msg": text, "uname": SMSusername,
                       "pass": SMSpassword}
        response = requests.post(SMSPhoneURL, params=querystring, timeout=PhoneTimeout)
        return response.text
