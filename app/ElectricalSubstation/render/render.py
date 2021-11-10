from queue import Queue
from threading import Thread

import app.Logging.app_provider.admin.MersadLogging as Logging
from app.ElectricalSubstation.model.Device import find_device


class RenderingDataThread:
    def __init__(self, devices, messenger_queue=None, ui=None):
        self.ui = ui
        self.devices = devices
        self.messenger_queue = messenger_queue
        self.DataQ = Queue()
        self.stop_thread = False
        self.Thread = Thread(target=self.rendering_data, args=(lambda: self.stop_thread,))
        self.Thread.start()
        Logging.line_monitoring_log("Init Render", "Start")

    def rendering_data(self, stop_thread):
        while True:
            data = self.DataQ.get()
            self.DataQ.task_done()

            if data:
                find_device(substation_id=1, unitId=3, devices=self.devices)

                print(data)

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
            Logging.electrical_log("Restart Render", "Start")
