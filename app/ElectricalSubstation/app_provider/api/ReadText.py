import os

from app.ResourcePath.app_provider.admin.main import resource_path
from core.config.Config import HelpFileName

TextPath = "File/Text/"

os.makedirs(resource_path(TextPath), exist_ok=True)

TextFileName = 'BaleText.txt'
FilePath = resource_path(TextPath + TextFileName)
f = open(FilePath, "r", encoding='utf-8')

EnrollOK = f.readline()
EnrollRepeat = f.readline()
ActiveText = f.readline()
DeactivationText = f.readline()
FailedText = f.readline()
CheckingText = f.readline()
SendExportText = f.readline()
SendingHelpText = f.readline()
PDFReport = f.readline()
CSVReport = f.readline()
NotInsert = f.readline()
BlockText = f.readline()
ShowAccessText = f.readline()
PhoneCreateText = f.readline()
CounterResponseText = f.readline()
ActivityResponseText = f.readline()
AccessONText = f.readline()
AccessOFFText = f.readline()

f.close()

TextFileName = HelpFileName + ".txt"
f = open(TextFileName, "r", encoding='utf-8')
HelpText = f.read()

f.close()

TextFileName = 'PLCText.txt'
FilePath = resource_path(TextPath + TextFileName)
f = open(FilePath, "r", encoding='utf-8')

PLCDisconnectBaleText = f.readline()
PLCConnectBaleText = f.readline()
VirtualText = f.readline()

f.close()
