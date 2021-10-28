import subprocess
import zipfile
import os
from PyQt5.QtWidgets import QFileDialog
from datetime import datetime
from core.config.Config import system_version, db_username, db_password, database, costumer, remove_db_flag, time_format
import app.Logging.app_provider.admin.MersadLogging as Logging


class BackupModel:
    def __init__(self, DBid=0, Path="C:\Mersad Monitoring/backup/", FileName="SQLBackup", Name="", Time=12,
                 username=db_username, password=db_password, database=database, UI=None, LastBackup=None, queue=None):
        self.Path = Path
        self.FileName = FileName
        self.Name = Name
        self.Time = Time
        self.username = username
        self.password = password
        self.database = database
        self.DBid = DBid
        self.queue = queue
        if LastBackup is None:
            LastBackup = datetime.now()
        self.LastBackup = LastBackup
        if DBid:
            if self.DBid < 5 and UI is not None:
                self.Backup_Name = UI.Backup_Name[self.DBid - 1]
                self.Backup_Path = UI.Backup_Path[self.DBid - 1]
                self.Backup_FileName = UI.Backup_FileName[self.DBid - 1]
                self.Backup_Time = UI.Backup_Time[self.DBid - 1]
                self.Choose_Path = UI.Choose_Path_pb[self.DBid - 1]
                self.Backup_pb = UI.Backup_pb[self.DBid - 1]

                self.Backup_Name.setText(str(self.Name))
                self.Backup_Time.setText(str(self.Time))
                self.Backup_FileName.setText(str(self.FileName))
                self.Backup_Path.setText(str(self.Path))
                self.Choose_Path.setEnabled(True)
                self.Choose_Path.clicked.connect(self.SetUI)

                self.Backup_pb.setEnabled(True)
                self.Backup_pb.clicked.connect(self.Send2queue)
                from core.theme.color.color import PB_BG_color_deactivate
                self.Backup_pb.setStyleSheet("background-color: rgba(" + PB_BG_color_deactivate + ");color: black;")
                self.Choose_Path.setStyleSheet("background-color: rgba(" + PB_BG_color_deactivate + ");color: black;")
            else:
                self.Backup_Name = ""
                self.Backup_Path = ""
                self.Backup_FileName = ""
                self.Backup_Time = ""

    def MakeBackUp(self):
        os.makedirs(self.Path, exist_ok=True)

        try:
            FileNameExtension = ".sql"
            self.updateTime()
            FilePathTemp = self.Path + "/" + self.FileName + '_' + self.LastBackup.strftime('%y-%m-%d')
            if remove_db_flag:
                for root, dirs, files in os.walk(self.Path + "/"):
                    for file in files:
                        if file.endswith(FileNameExtension) or file.endswith('.zip'):
                            os.remove(os.path.join(root, file))
            with open(FilePathTemp + FileNameExtension, 'w') as output:
                output.write('-- In the Name of God')
                output.write('\n')
                output.write('-- Database Backup')
                output.write('\n')
                output.write('-- Created by Siavash Sepahi !')
                output.write('\n')
                output.write('-- Backup Name : ')
                output.write(str(self.Name))
                output.write('\n')
                output.write('-- Generation Time : ')
                output.write(self.LastBackup.strftime(time_format))
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
            with zipfile.ZipFile(FilePathTemp + '.zip', 'w', zipfile.ZIP_DEFLATED) as myzip:
                # for file in os.listdir(self.Path + "/"):
                #     if file.endswith(FileNameExtension):
                #         myzip.write(os.path.join(root, file),
                #                    os.path.relpath(os.path.join(root, file),
                #                                    os.path.join(self.Path + "/", '..')))
                myzip.write(FilePathTemp + FileNameExtension,
                            os.path.relpath(FilePathTemp + FileNameExtension, os.path.join(self.Path + "/", '..')))
            os.remove(FilePathTemp + FileNameExtension)
        except Exception as e:
            Logging.main_log("MakeBackUP", str(e))

    def SetUI(self):
        file_name = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        if file_name:
            self.Backup_Path.setText(str(file_name))

    def updateTime(self):
        self.LastBackup = datetime.now()

    def Send2queue(self):
        self.queue.put(self.DBid)



