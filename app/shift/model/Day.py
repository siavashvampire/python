from datetime import datetime

from persiantools.jdatetime import JalaliDateTime

from app.LineMonitoring.app_provider.api.ReadText import FailedText
from core.app_provider.api.get import site_connection, get_from_site_db
from core.config.Config import MainGetIsDayUPURL, CronJobTimeout, MainGetadminDayURL, time_format, day_time_format


def isDayUpdated():
    get = get_from_site_db(MainGetIsDayUPURL, CronJobTimeout)
    status = get[0]
    if status:
        return get[1]
    else:
        return False


def adminDayCounter():
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'postman-token': "96d1603f-b13b-0da7-a12e-467ec0dfa771"
    }
    status, r = site_connection(MainGetadminDayURL, CronJobTimeout, header=headers)[0:2]
    if status:
        now_te = JalaliDateTime.to_jalali(datetime.strptime(r["Time"], time_format)).strftime(day_time_format)
        text = "گزارش تولید {Time} \n".format(Time=now_te)
        Data = r["Data"][0]

        if Data["counterAll"] is None or Data["counterAll"] == "0":
            text += "داده ای در امروز ثبت نشده است"
        else:
            text += "فاز : {phase}\n".format(phase=str(Data["phase"]))
            text += "کل تولید : " + str(Data["counterAll"]) + " \n"
            if r["Budget"] is None:
                text += "انحراف از بودجه : " + "بودجه ای تعریف نشده است" + " \n"
            else:
                text += "انحراف از بودجه : " + str(int(Data["counterAll"]) - int(r["Budget"])) + " \n"
            text += "درجات : " + " \n"
            text += "1" + " : (" + str(Data["m1"]) + ") " + str(Data["p1"]) + "% \n"
            text += "2" + " : (" + str(Data["m2"]) + ") " + str(Data["p2"]) + "% \n"
            text += "U" + " : (" + str(Data["m4"]) + ") " + str(Data["p4"]) + "% \n"
            text += "W" + " : (" + str(Data["m5"]) + ") " + str(Data["p5"]) + "% \n"
            if str(Data["OFFTime"]) == "واحد توقف نداشته است":
                text += str(Data["OFFTime"])
            else:
                text += "مدت زمان توقف :" + str(Data["OFFTime"])
    else:
        text = FailedText
    return text
