from queue import Queue
from datetime import datetime
from threading import Thread

from persiantools.jdatetime import JalaliDateTime

import app.Logging.app_provider.admin.MersadLogging as Logging
from app.LineMonitoring.model.CamSwitch import find_switch_choose
from app.LineMonitoring.model.Sensor import find_sensor_choose
from core.config.Config import OFFCamSwitchValue, ONCamSwitchValue


class RenderingDataThread:
    def __init__(self, sensor, switch, messenger_queue=None,  ui=None):
        self.ui = ui
        self.switch = switch
        self.sensor = sensor
        self.messenger_queue = messenger_queue
        self.DataQ = Queue()
        self.stop_thread = False
        self.Thread = Thread(target=self.rendering_data, args=(lambda: self.stop_thread,))
        self.Thread.start()
        Logging.line_monitoring_log("Init Render", "Start")

    def rendering_data(self, stop_thread):
        while True:
            [data, choose] = self.DataQ.get()
            self.DataQ.task_done()
            if data:
                sensor_chosen = find_sensor_choose(choose, self.sensor)
                switch_chosen = find_switch_choose(choose, self.switch)

                if (switch_chosen.Switch_id and sensor_chosen.sensor_id) or (
                        switch_chosen.Switch_id and sensor_chosen.sensor_id):
                    r = "Sensor not Found , Choose : " + str(choose)
                    print(r)
                    Logging.line_monitoring_log("Check Choose", str(r))

                if sensor_chosen.sensor_id:
                    if self.ui.Setting.SendDataPrintFlag.isChecked():
                        bet_text = ":"
                        bet_text = " " + bet_text
                        bet_text = bet_text + " "
                        if choose < 10:
                            bet_text = "  " + bet_text
                        elif choose < 100:
                            bet_text = " " + bet_text
                        print(
                            "Send Data from Sensor {choose}{bet}{data}".format(choose=choose, data=data, bet=bet_text))
                    bale_report_flag, sms_report_flag = sensor_chosen.send(data)
                    if bale_report_flag:
                        now1 = JalaliDateTime.to_jalali(datetime.now()).strftime('در %y/%m/%d ساعت %H:%M:%S')
                        if self.ui.Setting.baleONOFFSendFlag.isChecked():
                            if self.ui.Setting.baleONOFFFlag.isChecked():
                                print("on Sensor {} send".format(sensor_chosen.sensor_id))
                            on_sensor_bale_text = str(sensor_chosen.Name) + " فاز " + str(
                                sensor_chosen.Phase) + " " + str(
                                now1) + "روشن شده است"
                            self.messenger_queue.put(
                                [on_sensor_bale_text, sensor_chosen.unitId, sensor_chosen.Phase, 1])
                    if sms_report_flag:
                        now1 = JalaliDateTime.to_jalali(datetime.now()).strftime('در %y/%m/%d ساعت %H:%M:%S')
                        on_sensor_sms_text = str(sensor_chosen.Name) + " فاز " + str(sensor_chosen.Phase) + " " + str(
                            now1) + "روشن شده است"
                        self.messenger_queue.put([on_sensor_sms_text, sensor_chosen.unitId, sensor_chosen.Phase, 2])

                if switch_chosen.Switch_id:
                    active_temp = ""
                    if data == OFFCamSwitchValue:
                        active_temp = "Deactivate"
                    if data == ONCamSwitchValue:
                        active_temp = "Active"
                    if self.ui.Setting.SendDataPrintFlag.isChecked():
                        bet_text = ":"
                        bet_text = " " + bet_text
                        bet_text = bet_text + " "
                        if choose < 10:
                            bet_text = "  " + bet_text
                        elif choose < 100:
                            bet_text = " " + bet_text
                        print("Send Data from switch {choose}{bet}{Active}".format(choose=choose, Active=active_temp,
                                                                                   bet=bet_text))
                    bale_report_flag, sms_report_flag = switch_chosen.send(data)
                    on_switch_text = str(switch_chosen.Name) + " فاز " + str(switch_chosen.Phase) + " " + str(
                        JalaliDateTime.to_jalali(datetime.now()).strftime(
                            'در %y/%m/%d ساعت %H:%M:%S')) + "روشن شده است"
                    if bale_report_flag:
                        self.messenger_queue.put([on_switch_text, switch_chosen.unitId, switch_chosen.Phase, 1])
                    if sms_report_flag:
                        self.messenger_queue.put([on_switch_text, switch_chosen.unitId, switch_chosen.Phase, 2])

            else:
                if stop_thread():
                    Logging.line_monitoring_log("Main Rendering Thread", "Stop")
                    print("stop Rendering")
                    break

    def restart_thread(self):
        if not (self.Thread.is_alive()):
            self.stop_thread = False
            self.Thread = Thread(target=self.rendering_data, args=(lambda: self.stop_thread,))
            self.Thread.start()
            Logging.line_monitoring_log("Restart Render", "Start")
