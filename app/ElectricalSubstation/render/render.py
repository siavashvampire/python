from queue import Queue
from threading import Thread
from typing import Union, Callable

import app.Logging.app_provider.admin.MersadLogging as Logging
from app.ElectricalSubstation.model.Device import find_device, Device


class RenderingDataThread:
    devices: list[Device]
    messenger_queue: Queue[list[str, int, int, int]]
    DataQ: Queue[list[tuple[int, int], dict[str, Union[int, float]]]]
    stop_thread: bool
    Thread: Thread

    def __init__(self, devices: list[Device], messenger_queue: Queue[list[str, int, int, int]] = None, ui=None) -> None:
        self.ui = ui
        self.devices = devices
        self.messenger_queue = messenger_queue
        self.DataQ = Queue()
        self.stop_thread = False
        self.Thread = Thread(target=self.rendering_data, args=(lambda: self.stop_thread,))
        self.Thread.start()
        Logging.line_monitoring_log("Init Render", "Start")

    def rendering_data(self, stop_thread:Callable[[], bool]):
        while True:
            [choose, data] = self.DataQ.get()
            # print(data)
            self.DataQ.task_done()

            if data["substation_id"] != 0:
                # TODO:in data k miad if data ghalate v kolan none dadan ghalate
                found_device = find_device(choose, devices=self.devices)
                found_device.send(data)
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
