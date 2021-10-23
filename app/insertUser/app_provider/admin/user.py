import json
from core.config.Config import MainUserURL, UserTimeout


def InsertWorkerUser(fname, lname, email, phone, password):
    payload = {"fname": str(fname), "lname": str(lname), "email": str(email), "phone": str(phone),
               "password": str(password), "groupId": "6", "verified": "1"}
    status_code = 0
    try:
        response = requests.post(MainUserURL, data=payload, timeout=UserTimeout)
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
            r = response.text
        status_code = response.status_code
    return r, status_code
