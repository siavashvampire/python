from datetime import datetime
from queue import Queue
from threading import Thread
from typing import Callable

from core.app_provider.api.get import get_from_site_db
from core.config.Config import update_time, main_update_system_url, update_system_timeout, update_system_sleep_time


class UpdateController:
    update_queue: Queue[bool]
    checkForUpdate: Thread

    def __init__(self, line_monitoring_update_func: Callable[[tuple[str,str]], None],
                 electrical_update_func: Callable[[], None],
                 bale_org_update_func: Callable[[], None],
                 da_units_update_func: Callable[[], None]) -> None:
        self.Flag_Bale = False
        self.should_stop = False
        self.state = False
        self.stop_check = False
        self.stop_thread = False
        self.last_check = datetime.now()

        self.line_monitoring_update_func = line_monitoring_update_func
        self.electrical_update_func = electrical_update_func
        self.bale_org_update_func = bale_org_update_func
        self.da_units_update_func = da_units_update_func

        self.update_queue = Queue()
        self.checkForUpdate = Thread(target=self.check_for_update, args=(lambda: self.stop_thread,))
        self.checkForUpdate.start()

    def check_for_update(self, stop_thread):
        while True:
            try:
                self.update_queue.get(timeout=update_system_sleep_time)
                self.update_queue.task_done()
                self.update_system()
            #     TODO:bayad hameye get haro intori konam k timeout dashte bashan na sleep
            except:
                pass

            if stop_thread():
                break

            if (datetime.now() - self.last_check).seconds > update_time:
                self.update_system()
                self.last_check = datetime.now()

    def update_system(self):
        get = get_from_site_db(main_update_system_url, update_system_timeout)

        if not get[0]:
            return None

        r = dict(get[1])
        keys = r.keys()
        app_order = ["LineMonitoring", "ElectricalSubstation", "contacts", "DAUnits"]

        if app_order[0] in keys and r[app_order[0]] is not None:
            print("LineMonitoring")
            self.line_monitoring_update_func(r[app_order[0]])

        if app_order[1] in keys and r[app_order[1]] is not None:
            print("ElectricalSubstation")
            self.electrical_update_func()
            self.da_units_update_func()

        if app_order[2] in keys and r[app_order[2]] is not None:
            print("contacts")
            self.bale_org_update_func()

        if app_order[3] in keys and r[app_order[3]] is not None:
            print("DAUnits")
            self.da_units_update_func()

    def update_all(self):
        self.bale_org_update_func()
        self.line_monitoring_update_func(("sensor_update", "switch_update"))
        self.electrical_update_func()
        self.da_units_update_func()


