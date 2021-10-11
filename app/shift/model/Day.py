from core.config.Config import MainGetIsDayUPURL, CronJobTimeout, MainGetadminDayURL, time_format, day_time_format
from app.LineMonitoring.app_provider.api.ReadText import FailedText
import json
from datetime import datetime
from persiantools.jdatetime import JalaliDateTime


def isDayUpdated():
    status_code = 0
    try:
        response = requests.get(MainGetIsDayUPURL, timeout=CronJobTimeout)
    except requests.exceptions.HTTPError as errh:
        r = "Http Error:"
    except requests.exceptions.ConnectionError as errc:
        r = "Error Connecting Maybe Apache"
    except requests.exceptions.Timeout as errt:
        r = "Timeout Error Maybe SQL Error"
    except requests.exceptions.RequestException as err:
        r = "OOps: Something Else"

    else:
        status_code = response.status_code
        if status_code == 204:
            return False
        elif status_code == 205:
            return True
        elif status_code == 400:
            r = (response.json())["message"]
        else:
            r = "مشکل دیگه در سیستم است"
    return False


def adminDayCounter():
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        'postman-token': "96d1603f-b13b-0da7-a12e-467ec0dfa771"
    }
    status_code = 0
    try:
        response = requests.post(MainGetadminDayURL, headers=headers, timeout=CronJobTimeout)

    except requests.exceptions.HTTPError as errh:
        r = "Http Error:"
    except requests.exceptions.ConnectionError as errc:
        r = "Error Connecting Maybe Apache"
    except requests.exceptions.Timeout as errt:
        r = "Timeout Error Maybe SQL Error"
    except requests.exceptions.RequestException as err:
        r = "OOps: Something Else"

    else:
        if response.status_code == 200:
            r = response.text
            r = json.loads(r)
        elif response.status_code == 400:
            r = (response.json())["message"]
        else:
            r = FailedText
        status_code = response.status_code
    if status_code == 200:
        now_te = JalaliDateTime.to_jalali(datetime.strptime(r["Time"], time_format)).strftime(day_time_format)
        text = "گزارش تولید {Time} \n".format(Time=now_te)
        Data = r["Data"][0]

        if Data["counterAll"] is None or Data["counterAll"] is "0":
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
