from app.ResourcePath.app_provider.admin.main import resource_path
import os
from tinydb import TinyDB
import hashlib

ConfigPath = "../../File/Config/"
ConfigDBName = 'Config.json'
devCon = 1

os.makedirs(resource_path(ConfigPath), exist_ok=True)

ConfigDBPath = resource_path(ConfigPath + ConfigDBName)
ConfigDB = TinyDB(ConfigDBPath)
ConfigDB.drop_tables()
ConfigDB = TinyDB(ConfigDBPath).table('Config')

# start  Bale Config
# BaleToken           = '1326876710:66d645ae0c89cd745c8763de669e03c78bf3ab65' #developer

if devCon:
    BaleToken = '1516915829:443dc7da81a8cb716d19d8ceab0360203819ba62'  # New Bot
else:
    BaleToken = '1002539037:1d81d4d5b08a9aef9211073e3c1e43f06b8f9d16'  # original

Bale_Base_URL = "https://tapi.bale.ai/"
HelpFileName = 'File/Help/BaleHelp'
HelpPDFTimeOut = 100

ConfigDB.insert({"BaleToken": str(BaleToken)})
ConfigDB.update({"Bale_Base_URL": str(Bale_Base_URL)})
ConfigDB.update({"HelpFileName": str(HelpFileName)})
ConfigDB.update({"HelpPDFTimeOut": str(HelpPDFTimeOut)})
# end  Bale Config

# start  format Config
time_format = '%Y-%m-%d %H:%M:%S'
send_time_format = '%y-%m-%d %H:%M:%S'
day_time_format = '%Y/%m/%d'

ConfigDB.update({"time_format": str(time_format)})
ConfigDB.update({"send_time_format": str(send_time_format)})
ConfigDB.update({"day_time_format": str(day_time_format)})
# end  format Config

# start  PLC Config
RegisterForStartRead = 2088
RegisterForEndRead = 2089
RegisterForData = 4100
RegisterForCounter = 6099
RegisterForTest = 2098
if devCon:
    DisconnectAlarmTime = 5 * 60
else:
    DisconnectAlarmTime = 5 * 60
PLCTimeSleepMax = 1
PLCTimeSleepMin = 0
PLCRefreshTime = 5
PLCSleepTimeStepDown = 0.1
PLCSleepTimeStepUp = 0.01

ConfigDB.update({"RegisterForStartRead": str(RegisterForStartRead)})
ConfigDB.update({"RegisterForEndRead": str(RegisterForEndRead)})
ConfigDB.update({"RegisterForData": str(RegisterForData)})
ConfigDB.update({"RegisterForCounter": str(RegisterForCounter)})
ConfigDB.update({"RegisterForTest": str(RegisterForTest)})
ConfigDB.update({"DisconnectAlarmTime": str(DisconnectAlarmTime)})
ConfigDB.update({"PLCTimeSleepMax": str(PLCTimeSleepMax)})
ConfigDB.update({"PLCTimeSleepMin": str(PLCTimeSleepMin)})
ConfigDB.update({"PLCRefreshTime": str(PLCRefreshTime)})
ConfigDB.update({"PLCSleepTimeStepDown": str(PLCSleepTimeStepDown)})
ConfigDB.update({"PLCSleepTimeStepUp": str(PLCSleepTimeStepUp)})
# end  PLC Config

# Start  Timeouts Config
BaleGetTimeout = 80
LoginTimeout = 5
SendTimeout = 200
CheckTimeout = 30
SensorGetTimeout = 10
SwitchGetTimeout = 10
DAUnitsGetTimeout = 10
phones_get_timeout = 10
UserTimeout = 5
QSenderMaxWait = 100
SleepTime1 = 30
SleepTime2 = 120
SleepTime3 = 10
TimeDelayMainLoop = 15
CronJobTimeout = 500
ShiftCacheTime = 30

if devCon:
    ShiftCheckTime = 10
else:
    ShiftCheckTime = 20 * 60

ModbusTimeout = 3

ConfigDB.update({"BaleGetTimeout": str(BaleGetTimeout)})
ConfigDB.update({"LoginTimeout": str(LoginTimeout)})
ConfigDB.update({"SendTimeout": str(SendTimeout)})
ConfigDB.update({"CheckTimeout": str(CheckTimeout)})
ConfigDB.update({"SensorGetTimeout": str(SensorGetTimeout)})
ConfigDB.update({"SwitchGetTimeout": str(SwitchGetTimeout)})
ConfigDB.update({"DAUnitsGetTimeout": str(DAUnitsGetTimeout)})
ConfigDB.update({"phones_get_timeout": str(phones_get_timeout)})
ConfigDB.update({"UserTimeout": str(UserTimeout)})
ConfigDB.update({"QSenderMaxWait": str(QSenderMaxWait)})
ConfigDB.update({"SleepTime1": str(SleepTime1)})
ConfigDB.update({"SleepTime2": str(SleepTime2)})
ConfigDB.update({"SleepTime3": str(SleepTime3)})
ConfigDB.update({"TimeDelayMainLoop": str(TimeDelayMainLoop)})
ConfigDB.update({"CronJobTimeout": str(CronJobTimeout)})
ConfigDB.update({"ShiftCacheTime": str(ShiftCacheTime)})
ConfigDB.update({"ShiftCheckTime": str(ShiftCheckTime)})

ConfigDB.update({"ModbusTimeout": str(ModbusTimeout)})
# end  Timeouts Config

# Start  System Config
LogoutTime = 3600
BackupTime = 30
SensorONOFFTime = 10
mergeCheckTime = 30
MergeTime = 12
update_time = 20
update_system_timeout = 20
update_system_sleep_time = 20

ConfigDB.update({"LogoutTime": str(LogoutTime)})
ConfigDB.update({"BackupTime": str(BackupTime)})
ConfigDB.update({"SensorONOFFTime": str(SensorONOFFTime)})
ConfigDB.update({"mergeCheckTime": str(mergeCheckTime)})
ConfigDB.update({"MergeTime": str(MergeTime)})
ConfigDB.update({"update_time": str(update_time)})
ConfigDB.update({"update_system_timeout": str(update_system_timeout)})
ConfigDB.update({"update_system_sleep_time": str(update_system_sleep_time)})
# end  System Config

# Start  CamSwitch Config
OFFCamSwitchValue = 13000
ONCamSwitchValue = 26000

ConfigDB.update({"OFFCamSwitchValue": str(OFFCamSwitchValue)})
ConfigDB.update({"ONCamSwitchValue": str(ONCamSwitchValue)})
# end  CamSwitch Config


# Start  DB Config
if devCon:
    DBusername = 'Siavash'
    DBpassword = 'VamPire1468'
else:
    DBusername = 'root'
    DBpassword = 'AAaa1234'

database = 'test'
Costumer = 'Hafez Tiles'
RemoveDB = 1

ConfigDB.update({"DBusername": str(DBusername)})
ConfigDB.update({"DBpassword": str(DBpassword)})
ConfigDB.update({"database": str(database)})
ConfigDB.update({"Costumer": str(Costumer)})
ConfigDB.update({"RemoveDB": str(RemoveDB)})
# end  DB Config

# Start  SMS Config
SMSusername = "HafezManufactor"
SMSpassword = "HafezAAaa1234"
SMSPhone = "3000505"
PhoneTimeout = 10

ConfigDB.update({"SMSusername": str(SMSusername)})
ConfigDB.update({"SMSpassword": str(SMSpassword)})
ConfigDB.update({"SMSPhone": str(SMSPhone)})
ConfigDB.update({"PhoneTimeout": str(PhoneTimeout)})
# end  SMS Config

# Start  LocalDB Config
DBPath = "File/DataBase/"
LoggingDBName = 'LoggingDB.json'
PhoneDBName = 'PhonePropertyDB.json'
phone_table_name = 'Phone'
SMSPhoneDBName = 'PhonePropertyDB.json'
sms_phone_table_name = 'SMSPhone'
BackupDBName = 'BackupPropertyDB.json'
LastLogDBDBName = 'LastLogDB.json'
DADBName = 'DAPropertyDB.json'
DATableName = 'DAUnits'
SenderTableName = 'Data_Archive'
LogDBName = 'DataLogDB.json'
SensorDBName = 'SensorPropertyDB.json'
sensor_table_name = 'Sensor'
SwitchDBName = 'SensorPropertyDB.json'
switch_table_name = 'Switch'
DeviceDBName = 'SensorPropertyDB.json'
device_table_name = 'Switch'

ConfigDB.update({"DBPath": str(DBPath)})
ConfigDB.update({"LoggingDBName": str(LoggingDBName)})
ConfigDB.update({"PhoneDBName": str(PhoneDBName)})
ConfigDB.update({"phone_table_name": str(phone_table_name)})
ConfigDB.update({"SMSPhoneDBName": str(SMSPhoneDBName)})
ConfigDB.update({"sms_phone_table_name": str(sms_phone_table_name)})
ConfigDB.update({"BackupDBName": str(BackupDBName)})
ConfigDB.update({"LastLogDBDBName": str(LastLogDBDBName)})
ConfigDB.update({"DADBName": str(DADBName)})
ConfigDB.update({"DATableName": str(DATableName)})
ConfigDB.update({"SenderTableName": str(SenderTableName)})
ConfigDB.update({"LogDBName": str(LogDBName)})
ConfigDB.update({"SensorDBName": str(SensorDBName)})
ConfigDB.update({"sensor_table_name": str(sensor_table_name)})
ConfigDB.update({"SwitchDBName": str(SwitchDBName)})
ConfigDB.update({"switch_table_name": str(switch_table_name)})
ConfigDB.update({"DeviceDBName": str(DeviceDBName)})
ConfigDB.update({"device_table_name": str(device_table_name)})
# end  LocalDB Config

# Start  URL Config
if devCon:
    Main_URL = "http://192.168.1.4/Hafez/Monitoring_Tile/"
else:
    Main_URL = "http://localhost/"

GetSensorURL = "api/get/sensor"
GetSwitchURL = "api/get/camSwitch"
GetDeviceURL = "api/electrical/device"
Get_DAUnit_URL = "api/DAUnits"
get_phones_url = "api/phones"
get_sms_phones_url = "api/phones"
GetadminDayURL = "api/get/adminDayCounter"
GetIsDayUPURL = "api/get/isDayUpdated"
GetCounterURL = "api/get/Counter"
GetActivityURL = "api/get/sensorActivity"
update_system_url = "api/update"
urlLogin = "api/user/login"
urlcheckAccess = "api/checkAccess/index/"
GetCheckURL = "api/get/Check"
UserURL = "api/user/generateUser"
ActiveURL = "api/chageStatus"
SwitchURL = "api/chageStatus/camSwitch"
DefaultLogURL = "api/multi_call"
ExportURL = "api/export/"
CronMergeURL = "api/cronjob/mergeData"
CronShiftURL = "api/cronjob/updateShift"
CronDayURL = "api/cronjob/updateDay"
SMSPhoneURL = "http://ippanel.com/class/sms/webservice/send_url.php"
SendListFlag = 1
NForSendList = 50
boundaryForPayload = "----80085"

ConfigDB.update({"Main_URL": str(Main_URL)})
ConfigDB.update({"GetSensorURL": str(GetSensorURL)})
ConfigDB.update({"GetSwitchURL": str(GetSwitchURL)})
ConfigDB.update({"GetDeviceURL": str(GetDeviceURL)})
ConfigDB.update({"Get_DAUnit_URL": str(Get_DAUnit_URL)})
ConfigDB.update({"get_phones_url": str(get_phones_url)})
ConfigDB.update({"get_sms_phones_url": str(get_sms_phones_url)})
ConfigDB.update({"GetadminDayURL": str(GetadminDayURL)})
ConfigDB.update({"GetIsDayUPURL": str(GetIsDayUPURL)})
ConfigDB.update({"GetCounterURL": str(GetCounterURL)})
ConfigDB.update({"GetActivityURL": str(GetActivityURL)})
ConfigDB.update({"update_system_url": str(update_system_url)})
ConfigDB.update({"urlLogin": str(urlLogin)})
ConfigDB.update({"urlcheckAccess": str(urlcheckAccess)})
ConfigDB.update({"GetCheckURL": str(GetCheckURL)})
ConfigDB.update({"UserURL": str(UserURL)})
ConfigDB.update({"ActiveURL": str(ActiveURL)})
ConfigDB.update({"SwitchURL": str(SwitchURL)})
ConfigDB.update({"DefaultLogURL": str(DefaultLogURL)})
ConfigDB.update({"ExportURL": str(ExportURL)})
ConfigDB.update({"CronMergeURL": str(CronMergeURL)})
ConfigDB.update({"CronShiftURL": str(CronShiftURL)})
ConfigDB.update({"CronDayURL": str(CronDayURL)})
ConfigDB.update({"SMSPhoneURL": str(SMSPhoneURL)})
ConfigDB.update({"SendListFlag": str(SendListFlag)})
ConfigDB.update({"NForSendList": str(NForSendList)})
ConfigDB.update({"boundaryForPayload": str(boundaryForPayload)})
# end  URL Config

# Start  Developer Config
if devCon:
    DeveloperConfig = hashlib.md5(b'VamPire1468').digest()
else:
    DeveloperConfig = ""

ConfigDB.update({"DeveloperConfig": str(DeveloperConfig)})
# end  Developer Config

print("config Create Successfully")
