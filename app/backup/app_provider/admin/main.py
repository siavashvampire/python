from queue import Queue
from time import sleep
from datetime import datetime
from threading import Thread
from typing import List

from tinydb import TinyDB, Query

import app.Logging.app_provider.admin.MersadLogging as Logging
from app.backup.model.dbbackupModel import BackupModel
from core.config.Config import BackupDBPath, BackupTime, time_format


class BackupMain:
    Backup: List[BackupModel]

    def __init__(self, ui=None):
        self.state = False
        self.stop_check = False
        self.should_stop = False
        self.BackupDB = TinyDB(BackupDBPath).table('Backup')
        self.BackupQ = Queue()
        self.stop_thread = False
        self.Thread = Thread(target=self.backup_thread, args=(lambda: self.stop_thread,))
        self.ui = ui
        self.create_backup()
        self.last_check = datetime.now()

    def run_thread(self):
        self.Thread.start()

    def backup_thread(self, stop_thread):
        sleep(1)
        while True:
            try:
                id_temp = self.BackupQ.get(block=False)
                self.BackupQ.task_done()
                bup = self.find_backup(id_temp)
                bup.MakeBackUp()
                backup_prop = Query()
                self.BackupDB.update({'LastBackup': bup.LastBackup.strftime(time_format)},
                                     backup_prop.Path == str(bup.Path))
            except:
                sleep(10)
                if stop_thread():
                    Logging.main_log("Main Backup Thread", "Stop")
                    print("stop Backup")
                    break

            if (datetime.now() - self.last_check).seconds > BackupTime * 60:
                self.check_backup_time()
                self.last_check = datetime.now()

    def create_backup(self):
        if len(self.BackupDB):
            r = self.BackupDB.all()
            self.Backup = [BackupModel(DBid=i.doc_id, queue=self.BackupQ,
                                       LastBackup=datetime.strptime(i["LastBackup"], time_format),
                                       Time=i["Time"], Path=i["Path"], FileName=i["FileName"], Name=i["Name"],
                                       UI=self.ui) for i in r]
            print("Backup Created!")

    def get_backup_from_ui(self):
        BackupProp = Query()
        self.BackupDB = TinyDB(BackupDBPath)
        self.BackupDB.drop_tables()
        self.BackupDB.close()
        self.BackupDB = TinyDB(BackupDBPath).table('Backup')
        for i in range(4):
            if str(self.ui.Backup_Name[i].text()) is not "":
                Time = str(self.ui.Backup_Time[i].text())
                Name = str(self.ui.Backup_Name[i].text())
                Path = str(self.ui.Backup_Path[i].text())
                FileName = str(self.ui.Backup_FileName[i].text())

                if Time is "":
                    Time = str(12)
                if Path is "":
                    Path = r"C:\Mersad Monitoring/backup/"
                if FileName is "":
                    FileName = "SQLBackup"
                self.BackupDB.upsert({'Name': str(Name), 'Time': str(Time), 'FileName': str(FileName),
                                      'LastBackup': str(datetime.now().strftime(time_format)),
                                      'Path': str(Path)}, BackupProp.Path == str(Path))

    def clear_backup_ui(self):
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

    def check_backup_time(self):
        for r in self.Backup:
            diff = datetime.now() - r.LastBackup
            hours = diff.seconds // 3600 + diff.days * 24
            if hours >= int(r.Time):
                self.BackupQ.put(r.DBid)

    def find_backup(self, id_temp):
        for r in self.Backup:
            if r.DBid == id_temp:
                return r

    def restart_thread(self):
        if not (self.Thread.is_alive()):
            self.stop_thread = False
            self.Thread = Thread(target=self.backup_thread, args=(lambda: self.stop_thread,))
            self.Thread.start()

    def update_app(self):
        self.get_backup_from_ui()
        self.clear_backup_ui()
        self.create_backup()

    def check(self):
        if not (self.Thread.is_alive()):
            self.restart_thread()
            self.stop_thread = False

    def state_thread(self, state=False, program=False):
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

    def stop_func(self):
        self.stop_thread = True
        self.Thread.join()
        self.stop_check = True
        self.state = False

    def start_func(self):
        self.stop_thread = False
        self.restart_thread()
        self.stop_check = False
        self.state = True
