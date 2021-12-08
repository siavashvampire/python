from queue import Queue
from time import sleep
from datetime import datetime
from threading import Thread
from typing import List, Callable

from tinydb import TinyDB, Query
from tinydb.table import Table

import app.Logging.app_provider.admin.MersadLogging as Logging
from app.backup.model.dbbackupModel import BackupModel
from core.config.Config import backup_db_path, backup_time, time_format, backup_table_name


class BackupMain:
    state: bool
    stop_check: bool
    should_stop: bool
    BackupDB: Table
    BackupQ: Queue[int]
    stop_thread: bool
    Thread: Thread
    Backup: List[BackupModel]
    last_check: datetime

    def __init__(self, ui=None) -> None:
        self.state = False
        self.stop_check = False
        self.should_stop = False
        self.BackupDB = TinyDB(backup_db_path).table(backup_table_name)
        self.BackupQ = Queue()
        self.stop_thread = False
        self.Thread = Thread(target=self.backup_thread, args=(lambda: self.stop_thread,))
        self.ui = ui
        self.Backup = []
        self.create_backup()
        self.last_check = datetime.now()

    def run_thread(self) -> None:
        self.Thread.start()

    def backup_thread(self, stop_thread: Callable[[], bool]) -> None:
        sleep(1)
        while True:
            try:
                id_temp = self.BackupQ.get(timeout=10)
                self.BackupQ.task_done()
                bup = self.find_backup(id_temp)
                if bup.db_id:
                    bup.make_backup()
                    prop = Query()
                    self.BackupDB.update({'LastBackup': bup.last_backup_time.strftime(time_format)},
                                         prop.Path == str(bup.path))
            except:
                if stop_thread():
                    Logging.main_log("Main Backup Thread", "Stop")
                    print("stop Backup")
                    break

            if (datetime.now() - self.last_check).seconds > backup_time * 60:
                self.check_backup_time()
                self.last_check = datetime.now()

    def create_backup(self) -> None:
        self.Backup.clear()
        r = self.BackupDB.all()
        for i in r:
            self.Backup.append(BackupModel(db_id=i.doc_id, queue=self.BackupQ,
                                           last_backup_time=datetime.strptime(i["LastBackup"], time_format),
                                           time=i["Time"], path=i["Path"], file_name=i["FileName"], name=i["Name"],
                                           ui=self.ui))
        print("Backup Created!")

    def get_backup_from_ui(self) -> None:
        prop = Query()
        db: TinyDB = TinyDB(backup_db_path)
        db.drop_tables()
        db.close()
        self.BackupDB = TinyDB(backup_db_path).table(backup_table_name)
        for i in range(4):
            if str(self.ui.Backup_Name[i].text()):
                time = str(self.ui.Backup_Time[i].text())
                name = str(self.ui.Backup_Name[i].text())
                path = str(self.ui.Backup_Path[i].text())
                file_name = str(self.ui.Backup_FileName[i].text())

                if not time:
                    time = str(12)
                if not path:
                    path = r"C:\Mersad Monitoring/backup/"
                if not file_name:
                    file_name = "SQLBackup"
                self.BackupDB.upsert({'Name': str(name), 'Time': str(time), 'FileName': str(file_name),
                                      'LastBackup': str(datetime.now().strftime(time_format)),
                                      'Path': str(path)}, prop.Path == str(path))

    def clear_backup_ui(self) -> None:
        from core.theme.color.color import PB_BG_color_deactivate, PB_Text_color_deactivate

        for i in range(4):
            self.ui.Backup_Time[i].setText("")
            self.ui.Backup_Name[i].setText("")
            self.ui.Backup_Path[i].setText("")
            self.ui.Backup_FileName[i].setText("")
            self.ui.Backup_pb[i].setEnabled(False)
            self.ui.Choose_Path_pb[i].setEnabled(False)
            self.ui.Backup_pb[i].setStyleSheet(
                "background-color: rgba(" + PB_BG_color_deactivate + ");color: rgba(" + PB_Text_color_deactivate + ");")
            self.ui.Choose_Path_pb[i].setStyleSheet(
                "background-color: rgba(" + PB_BG_color_deactivate + ");color: rgba(" + PB_Text_color_deactivate + ");")

    def check_backup_time(self) -> None:
        for r in self.Backup:
            diff = datetime.now() - r.last_backup_time
            hours = diff.seconds // 3600 + diff.days * 24
            if hours >= int(r.time):
                self.BackupQ.put(r.db_id)

    def find_backup(self, id_temp: int) -> BackupModel:
        for r in self.Backup:
            if r.db_id == id_temp:
                return r
        return BackupModel()

    def restart_thread(self) -> None:
        if not (self.Thread.is_alive()):
            self.stop_thread = False
            self.Thread = Thread(target=self.backup_thread, args=(lambda: self.stop_thread,))
            self.Thread.start()

    def update_app(self) -> None:
        self.get_backup_from_ui()
        self.clear_backup_ui()
        self.create_backup()

    def check(self) -> None:
        if not (self.Thread.is_alive()):
            self.restart_thread()
            self.stop_thread = False

    def state_thread(self, state: bool = False, program: bool = False) -> None:
        if program is False:
            if self.state:
                self.should_stop = True
                self.stop_func()
            else:
                self.should_stop = False
                self.start_func()
        else:
            if state is True:
                if not self.should_stop:
                    self.start_func()
            if state is False:
                self.stop_func()

    def stop_func(self) -> None:
        self.stop_thread = True
        self.Thread.join()
        self.stop_check = True
        self.state = False

    def start_func(self) -> None:
        self.stop_thread = False
        self.restart_thread()
        self.stop_check = False
        self.state = True
