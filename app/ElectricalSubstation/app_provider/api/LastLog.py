from datetime import datetime

from tinydb import TinyDB, Query

from core.config.Config import LastLogDBPath, time_format

LogProp = Query()


def update(Sensor_id):
    LastLogDB = TinyDB(LastLogDBPath).table('LastLog')
    now = datetime.now()
    now = now.strftime(time_format)
    LastLogDB.upsert({'Sensor_id': str(Sensor_id), 'Last_Time': str(now)}, LogProp.Sensor_id == str(Sensor_id))


def get(Sensor_id):
    LastLogDB = TinyDB(LastLogDBPath).table('LastLog')
    sea = LastLogDB.get(LogProp.Sensor_id == str(Sensor_id))
    if sea is None:
        return sea
    else:
        return sea["Last_Time"]


def getABSecond(diff):
    if not diff:
        return 0
    sec = diff.years * 365 * 24 * 60 * 60
    sec += diff.months * 30 * 24 * 60 * 60
    sec += diff.days * 24 * 60 * 60
    sec += diff.hours * 60 * 60
    sec += diff.minutes * 60
    sec += diff.seconds
    return sec


def getText(diff):
    if not diff:
        return "0 seconds "
    text = ""
    if diff.years:
        text += "%d years " % diff.years
    if diff.months:
        text += "%d months " % diff.months
    if diff.days:
        text += "%d days " % diff.days
    if diff.hours:
        text += "%d hours " % diff.hours
    if diff.minutes:
        text += "%d minutes " % diff.minutes
    if diff.seconds:
        text += "%d seconds " % diff.seconds
    return text
