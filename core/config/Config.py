from app.ResourcePath.app_provider.admin.main import resource_path
import os
from tinydb import TinyDB
import hashlib

ConfigPath = "File/Config/"
ConfigDBName = 'Config.json'

os.makedirs(resource_path(ConfigPath), exist_ok=True)

ConfigDBPath = resource_path(ConfigPath + ConfigDBName)
ConfigTB = TinyDB(ConfigDBPath).table('Config')

sAll = ConfigTB.all()[0]
# sAll = ConfigTB.get(doc_id=1)

if not len(ConfigTB):
    print(len(ConfigTB))
    print("import Config First")

# Start  Bale Config
BaleToken = sAll["BaleToken"]
Bale_Base_URL = sAll["Bale_Base_URL"]
HelpFileName = sAll["HelpFileName"]
HelpFileName = resource_path(HelpFileName)
HelpPDFTimeOut = int(sAll["HelpPDFTimeOut"])
# end  Bale Config

# start  format Config
time_format = sAll["time_format"]
send_time_format = sAll["send_time_format"]
day_time_format = sAll["day_time_format"]
# end  format Config

# Start  PLC Config
RegisterForStartRead = int(sAll["RegisterForStartRead"])
RegisterForEndRead = int(sAll["RegisterForEndRead"])
RegisterForData = int(sAll["RegisterForData"])
RegisterForCounter = int(sAll["RegisterForCounter"])
RegisterForTest = int(sAll["RegisterForTest"])
DisconnectAlarmTime = float(sAll["DisconnectAlarmTime"])
PLCTimeSleepMax = float(sAll["PLCTimeSleepMax"])
PLCTimeSleepMin = float(sAll["PLCTimeSleepMin"])
PLCRefreshTime = float(sAll["PLCRefreshTime"])
PLCSleepTimeStepDown = float(sAll["PLCSleepTimeStepDown"])
PLCSleepTimeStepUp = float(sAll["PLCSleepTimeStepUp"])
# end  PLC Config

# Start  Timeouts Config
BaleGetTimeout = int(sAll["BaleGetTimeout"])
LoginTimeout = int(sAll["LoginTimeout"])
SendTimeout = int(sAll["SendTimeout"])
CheckTimeout = int(sAll["CheckTimeout"])
SensorGetTimeout = int(sAll["SensorGetTimeout"])
SwitchGetTimeout = int(sAll["SwitchGetTimeout"])
DAUnitsGetTimeout = int(sAll["DAUnitsGetTimeout"])
phones_get_timeout = int(sAll["phones_get_timeout"])
UserTimeout = int(sAll["UserTimeout"])
QSenderMaxWait = int(sAll["QSenderMaxWait"])
SleepTime1 = int(sAll["SleepTime1"])
SleepTime2 = int(sAll["SleepTime2"])
SleepTime3 = int(sAll["SleepTime3"])
TimeDelayMainLoop = int(sAll["TimeDelayMainLoop"])
CronJobTimeout = int(sAll["CronJobTimeout"])
ShiftCacheTime = int(sAll["ShiftCacheTime"])
ShiftCheckTime = int(sAll["ShiftCheckTime"])

ModbusTimeout = int(sAll["ModbusTimeout"])
# end  Timeouts Config

# Start  System Config
LogoutTime = int(sAll["LogoutTime"])
BackupTime = int(sAll["BackupTime"])
SensorONOFFTime = int(sAll["SensorONOFFTime"])
mergeCheckTime = int(sAll["mergeCheckTime"])
MergeTime = int(sAll["MergeTime"])
update_time = int(sAll["update_time"])
update_system_timeout = int(sAll["update_system_timeout"])
update_system_sleep_time = int(sAll["update_system_sleep_time"])
# end  System Config

# Start  CamSwitch Config
OFFCamSwitchValue = int(sAll["OFFCamSwitchValue"])
ONCamSwitchValue = int(sAll["ONCamSwitchValue"])
# end  CamSwitch Config

# Start  DB Config
SystemVersion = "Monitoring Version: 0.4"
DBusername = sAll["DBusername"]
DBpassword = sAll["DBpassword"]
database = sAll["database"]
Costumer = sAll["Costumer"]
RemoveDB = int(sAll["RemoveDB"])
# end  DB Config

# Start  SMS Config
SMSusername = sAll["SMSusername"]
SMSpassword = sAll["SMSpassword"]
SMSPhone = sAll["SMSPhone"]
PhoneTimeout = int(sAll["PhoneTimeout"])
# end  SMS Config

# Start  LocalDB Config
DBPath = sAll["DBPath"]
LoggingDBName = sAll["LoggingDBName"]
PhoneDBName = sAll["PhoneDBName"]
phone_table_name = sAll["phone_table_name"]
SMSPhoneDBName = sAll["SMSPhoneDBName"]
sms_phone_table_name = sAll["sms_phone_table_name"]
BackupDBName = sAll["BackupDBName"]
LastLogDBDBName = sAll["LastLogDBDBName"]
DADBName = sAll["DADBName"]
DATableName = sAll["DATableName"]
SenderTableName = sAll["SenderTableName"]
LogDBName = sAll["LogDBName"]
SensorDBName = sAll["SensorDBName"]
sensor_table_name = sAll["sensor_table_name"]
SwitchDBName = sAll["SwitchDBName"]
switch_table_name = sAll["switch_table_name"]
DeviceDBName = sAll["DeviceDBName"]
device_table_name = sAll["device_table_name"]

LoggingDBPath = resource_path(DBPath + LoggingDBName)
PhoneDBPath = resource_path(DBPath + PhoneDBName)
SMSPhoneDBPath = resource_path(DBPath + SMSPhoneDBName)
BackupDBPath = resource_path(DBPath + BackupDBName)
LastLogDBPath = resource_path(DBPath + LastLogDBDBName)
DADBPath = resource_path(DBPath + DADBName)
LogDBPath = resource_path(DBPath + LogDBName)
SensorDBPath = resource_path(DBPath + SensorDBName)
SwitchDBPath = resource_path(DBPath + SwitchDBName)
DeviceDBPath = resource_path(DBPath + DeviceDBName)
# end  LocalDB Config

# Start  URL Config
Main_URL = sAll["Main_URL"]
GetSensorURL = sAll["GetSensorURL"]
GetSwitchURL = sAll["GetSwitchURL"]
GetDeviceURL = sAll["GetDeviceURL"]
Get_DAUnit_URL = sAll["Get_DAUnit_URL"]
get_phones_url = sAll["get_phones_url"]
get_sms_phones_url = sAll["get_sms_phones_url"]
GetadminDayURL = sAll["GetadminDayURL"]
GetIsDayUPURL = sAll["GetIsDayUPURL"]
GetCounterURL = sAll["GetCounterURL"]
GetActivityURL = sAll["GetActivityURL"]
update_system_url = sAll["update_system_url"]
urlLogin = sAll["urlLogin"]
urlcheckAccess = sAll["urlcheckAccess"]
GetCheckURL = sAll["GetCheckURL"]
UserURL = sAll["UserURL"]
ActiveURL = sAll["ActiveURL"]
SwitchURL = sAll["SwitchURL"]
DefaultLogURL = sAll["DefaultLogURL"]
ExportURL = sAll["ExportURL"]
CronMergeURL = sAll["CronMergeURL"]
CronShiftURL = sAll["CronShiftURL"]
CronDayURL = sAll["CronDayURL"]
SMSPhoneURL = sAll["SMSPhoneURL"]

MainGetSensorURL = Main_URL + GetSensorURL
MainGetSwitchURL = Main_URL + GetSwitchURL
MainGetDeviceURL = Main_URL + GetDeviceURL
Main_Get_DAUnit_URL = Main_URL + Get_DAUnit_URL
main_get_phones_url = Main_URL + get_phones_url
MainGetadminDayURL = Main_URL + GetadminDayURL
MainGetIsDayUPURL = Main_URL + GetIsDayUPURL
MainGetCounterURL = Main_URL + GetCounterURL
MainGetActivityURL = Main_URL + GetActivityURL
main_update_system_url = Main_URL + update_system_url
MainurlLogin = Main_URL + urlLogin
MainurlCheckAccess = Main_URL + urlcheckAccess
MainGetCheckURL = Main_URL + GetCheckURL
MainUserURL = Main_URL + UserURL
MainActiveURL = Main_URL + ActiveURL
MainSwitchURL = Main_URL + SwitchURL
MainDefaultLogURL = Main_URL + DefaultLogURL
MainExportURL = Main_URL + ExportURL
MainCronMergeURL = Main_URL + CronMergeURL
MainCronShiftURL = Main_URL + CronShiftURL
MainCronDayURL = Main_URL + CronDayURL

SendListFlag = int(sAll["SendListFlag"])
NForSendList = int(sAll["NForSendList"])
boundaryForPayload = sAll["boundaryForPayload"]
# end  URL Config

# Start  Developer Config
DeveloperConfig = sAll["DeveloperConfig"]

LoginDeveloper = 0
if DeveloperConfig == str(hashlib.md5(b'VamPire1468').digest()):
    LoginDeveloper = 1
# end  Developer Config
