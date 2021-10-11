from tinydb import TinyDB, Query

from app.LineMonitoring.app_provider.api.ReadText import CounterResponseText, ActivityResponseText
from core.config.Config import PhoneDBPath, NForSendList, phone_table_name


def get_rh(r, status_code, db_path, table_name):
    if status_code == 0:
        print(r)
    elif status_code == 404:
        print("Non Existing URL Path")
        print(r)
    elif status_code == 400:
        print("DB Error")
        print(r)
    elif status_code == 500:
        print("internal Code Error")
        print(r)
    elif status_code == 200:
        try:
            prop = Query()
            db = TinyDB(db_path)
            db.drop_table(table_name)
            db.close()
            db = TinyDB(db_path).table(table_name)
            for i in r:
                db.upsert(i, prop.id == i["id"])

        except Exception as e:
            print("bad Response in get_rh")

    else:
        print("Non Handling Error in RH")
        print(status_code)


def PhoneNumberResponseHandler(Name, phone_id):
    insertflag = False
    PhoneProp = Query()
    PhoneDB = TinyDB(PhoneDBPath).table(phone_table_name)
    sea = PhoneDB.search(PhoneProp.id == phone_id)
    if (sea == []):
        PhoneDB.insert({'Name': str(Name), 'id': phone_id, 'SendONOFF': 1, 'Access': 0, 'Units': [0], 'phase': [0]})
        insertflag = True
    else:
        PhoneDB.update({'Name': str(Name)}, PhoneProp.id == phone_id)
        insertflag = False
    return insertflag


def CounterResponseHandler(r, status):
    if r == True:
        massage = "داده ای تاکنون ثبت نشده است"
    else:
        massage = ""
        if not status:
            print(r)
        else:
            for i in r:
                massage += CounterResponseText.format(Name=i["Sensor_name"], Phase=i["phase"], counter=i["counter"],
                                                      Tile=i["tile_name"])
    return massage


def GetActivityeHandler(r, status):
    if r == True:
        massage = "داده ای تاکنون ثبت نشده است"
        return (massage)
    massage = ""

    if not status:
        print(r)
    else:
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

    massage = "خطایی رخ داده است"
    return massage


def send_data(r, status):
    error = False
    good = False
    index = 0
    if status in [200, 204, 205]:
        good = True
        index = NForSendList
        r = ""
    elif status == 400:
        r = r["message"]
        index = r["indexOfProblem"]
        error = r["result"]
        if index == 0:
            good = False
        else:
            good = True
    else:
        r = "status code : " + str(status) + " , " + str(r)
    return good, index, error
