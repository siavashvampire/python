import json

import requests

import app.Logging.app_provider.admin.MersadLogging as Logging
from app.LineMonitoring.app_provider.api.ReadText import FailedText
from core.RH.ResponseHandler import get_rh


def get_from_site_db(get_url, get_timeout, db_path='', table_name=''):
    status_code = 0
    status = False
    try:
        response = requests.get(get_url, timeout=get_timeout)
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
        if status_code == 200:
            r = response.text
            try:
                r = json.loads(r)
            except Exception as e:
                print("bad response")
                return False, "bad response " + str(e)
            status = True
        elif status_code == 400:
            r = (response.json())["message"]
        else:
            r = "مشکل دیگه در سیستم است"

    if status_code != 200:
        Logging.line_monitoring_log("get " + get_url, str(r))

    if db_path != '':  # TODO: bayad check konim shart doros bar gharar mishe ya na
        get_rh(r, status_code, db_path, table_name)
    return status, r


def site_connection(url, timeout, data=None, header=None):
    try:
        response = requests.post(url, data=data, headers=header, timeout=timeout)
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
        if status_code == 200:
            r = response.json()
            if r["status"] is True:
                return r["status"], r
        elif status_code == 404:
            r = "Non Existing URL Path"
        elif status_code == 400:
            r = "Code Error"
        elif status_code == 500:
            r = "DB Error"
        else:
            r = FailedText
        return False, r
    return False, r
