from app.Bale.model.PhoneModel import PhoneModel
from core.app_provider.api.get import site_connection
from core.config.Config import sms_username, sms_password, sms_phone, phone_timeout, sms_phone_send_url, choose_of_sms


class SMSPhoneData(PhoneModel):

    def __init__(self, name: str, phone: int, units: str, phase: str, access: bool = 0) -> None:
        super().__init__(name=name, phone=phone, units=units, phase=phase, access=access, choose=choose_of_sms)

    def send(self, text: str) -> str:
        querystring = {"from": sms_phone, "to": "0" + str(self.id), "msg": text, "uname": sms_username,
                       "pass": sms_password}

        return site_connection(sms_phone_send_url, phone_timeout, params=querystring)[1]
