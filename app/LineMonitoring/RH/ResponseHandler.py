from tinydb import TinyDB, Query

from app.LineMonitoring.app_provider.api.ReadText import CounterResponseText, ActivityResponseText
from core.config.Config import phone_db_path


def CounterResponseHandler(r, status_code):
    if r == True:
        massage = "داده ای تاکنون ثبت نشده است"
    else:
        massage = ""
        if (status_code == 0):
            print(r)
        elif (status_code == 400):
            print("DB Error")
            print(r)
        elif (status_code == 200):
            for i in r:
                massage += CounterResponseText.format(Name=i["Sensor_name"], Phase=i["phase"], counter=i["counter"],
                                                      Tile=i["tile_name"])
    return massage


def PhoneNumberResponseHandler(Name, id):
    PhoneProp = Query()
    PhoneDB = TinyDB(phone_db_path).table(phone_table_name)

    sea = PhoneDB.search(PhoneProp.id == id)
    if (sea == []):
        PhoneDB.insert({'Name': str(Name), 'id': id, 'SendONOFF': 1, 'Access': 0, 'Units': [0], 'phase': [0]})
        insertflag = True
    else:
        PhoneDB.update({'Name': str(Name)}, PhoneProp.id == id)
        insertflag = False
    return insertflag


def GetActivityeHandler(r, status_code):
    if r == True:
        massage = "داده ای تاکنون ثبت نشده است"
        return (massage)
    massage = ""
    if (status_code == 0):
        print(r)
    elif (status_code == 404):
        print("Non Existing URL Path")
        print(r)
    elif (status_code == 400):
        print("DB Error")
        print(r)
    elif (status_code == 500):
        print("Code Error")
        print(r)
    elif (status_code == 200):
        try:
            for i in r:
                if int(i["Active"]):
                    Activetext = " فعال "
                else:
                    Activetext = "غیر فعال "
                massage += ActivityResponseText.format(Name=i["Name"], Phase=i["Phase"], Active=Activetext,
                                                       unit=i["unit"])
            return massage

        except Exception as e:
            print("bad Response in SensorActivity")
            print(e)

    else:
        print("Non Handeling Error in RH")
        print(status_code)
        print(r)
    massage = "خطایی رخ داده است"
    return (massage)
