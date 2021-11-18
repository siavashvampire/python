import subprocess
import zipfile
import os
from queue import Queue

from PyQt5.QtWidgets import QFileDialog, QLineEdit, QPushButton
from datetime import datetime
from core.config.Config import system_version, db_username, db_password, db_name, costumer, remove_db_flag, time_format
import app.Logging.app_provider.admin.MersadLogging as Logging


class BackupModel:
    path: str
    file_name: str
    name: str
    time: int
    username: str
    password: str
    database: str
    db_id: int
    queue: Queue
    last_backup_time: datetime
    Backup_Name: QLineEdit
    Backup_Path: QLineEdit
    Backup_FileName: QLineEdit
    Backup_Time: QLineEdit
    Choose_Path_pb: QPushButton
    Backup_pb: QPushButton

    def __init__(self, db_id: int = 0, path: str = "C:\Mersad Monitoring/backup/", file_name: str = "SQLBackup",
                 name: str = "", time: int = 12, username: str = db_username, password: str = db_password,
                 database: str = db_name, ui=None, last_backup_time: datetime = None, queue: Queue = None) -> None:
        self.path = path
        self.file_name = file_name
        self.name = name
        self.time = time
        self.username = username
        self.password = password
        self.database = database
        self.db_id = db_id
        self.queue = queue

        if last_backup_time is None:
            last_backup_time = datetime.now()
        self.last_backup_time = last_backup_time
        if self.db_id:
            if self.db_id < 5 and ui is not None:
                self.Backup_Name = ui.Backup_Name[self.db_id - 1]
                self.Backup_Path = ui.Backup_Path[self.db_id - 1]
                self.Backup_FileName = ui.Backup_FileName[self.db_id - 1]
                self.Backup_Time = ui.Backup_Time[self.db_id - 1]
                self.Choose_Path = ui.Choose_Path_pb[self.db_id - 1]
                self.Backup_pb = ui.Backup_pb[self.db_id - 1]

                self.Backup_Name.setText(str(self.name))
                self.Backup_Time.setText(str(self.time))
                self.Backup_FileName.setText(str(self.file_name))
                self.Backup_Path.setText(str(self.path))
                self.Choose_Path.setEnabled(True)
                self.Choose_Path.clicked.connect(self.set_ui)

                self.Backup_pb.setEnabled(True)
                self.Backup_pb.clicked.connect(self.send_to_main_queue)
                from core.theme.color.color import PB_BG_color_deactivate
                self.Backup_pb.setStyleSheet("background-color: rgba(" + PB_BG_color_deactivate + ");color: black;")
                self.Choose_Path.setStyleSheet("background-color: rgba(" + PB_BG_color_deactivate + ");color: black;")
            else:
                self.Backup_Name = QLineEdit()
                self.Backup_Path = QLineEdit()
                self.Backup_FileName = QLineEdit()
                self.Backup_Time = QLineEdit()

    def make_backup(self) -> None:
        os.makedirs(self.path, exist_ok=True)

        try:
            file_name_extension = ".sql"
            self.update_last_backup_time()
            file_path_temp = self.path + "/" + self.file_name + '_' + self.last_backup_time.strftime('%y-%m-%d')
            if remove_db_flag:
                for root, dirs, files in os.walk(self.path + "/"):
                    for file in files:
                        if file.endswith(file_name_extension) or file.endswith('.zip'):
                            os.remove(os.path.join(root, file))
            with open(file_path_temp + file_name_extension, 'w') as output:
                output.write('-- In the Name of God')
                output.write('\n')
                output.write('-- Database Backup')
                output.write('\n')
                output.write('-- Created by Siavash Sepahi !')
                output.write('\n')
                output.write('-- Backup Name : ')
                output.write(str(self.name))
                output.write('\n')
                output.write('-- Generation Time : ')
                output.write(self.last_backup_time.strftime(time_format))
                output.write('\n')
                output.write('-- ')
                output.write(system_version)
                output.write('\n')
                output.write('-- Company: Mersad')
                output.write('\n')
                output.write('-- Database: ' + self.database)
                output.write('\n')
                output.write('-- Costumer: ' + costumer)
                output.write('\n')
                output.write('\n')
                output.write('-- ------------------------------------------------------')
                output.write('\n')
                c = subprocess.run(['mysqldump', '-u', self.username, '-p%s' % self.password, self.database],
                                   stdout=output, shell=True)
            with zipfile.ZipFile(file_path_temp + '.zip', 'w', zipfile.ZIP_DEFLATED) as myzip:
                # for file in os.listdir(self.Path + "/"):
                #     if file.endswith(FileNameExtension):
                #         myzip.write(os.path.join(root, file),
                #                    os.path.relpath(os.path.join(root, file),
                #                                    os.path.join(self.Path + "/", '..')))
                myzip.write(file_path_temp + file_name_extension,
                            os.path.relpath(file_path_temp + file_name_extension, os.path.join(self.path + "/", '..')))
            os.remove(file_path_temp + file_name_extension)
        except Exception as e:
            Logging.main_log("MakeBackUP", str(e))

    def set_ui(self) -> None:
        file_name = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        if file_name:
            self.Backup_Path.setText(str(file_name))

    def update_last_backup_time(self) -> None:
        self.last_backup_time = datetime.now()

    def send_to_main_queue(self) -> None:
        self.queue.put(self.db_id)
