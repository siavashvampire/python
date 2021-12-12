import pywhatkit

from core.config.Config import choose_of_whatsApp

from app.Bale.model.PhoneModel import PhoneModel


class WhatsAppModel(PhoneModel):

    def __init__(self, name: str, phone: int, units: str, phase: str, access: bool = 0) -> None:
        super().__init__(name=name, phone=phone, units=units, phase=phase, access=access, choose=choose_of_whatsApp)

    def send(self, text: str) -> None:
        pywhatkit.sendwhatmsg_instantly("+989379206248", text, 15, True, 6)
        # pywhatkit.sendwhatmsg("+989171129092", text, now.hour, now.minute, 15, True, 6)
        # pywhatkit.sendwhats_image("+989171129092", path + "core/theme/pic/pic/MERSAD_Logo.png", "test aks", 15, True, 6)
        # pywhatkit.sendwhatmsg_to_group("HwypPTAYoxa8jsmqJQi3cM", text, now.hour, now.minute, 15, True, 6)
        # https://web.whatsapp.com/accept?code=HwypPTAYoxa8jsmqJQi3cM
