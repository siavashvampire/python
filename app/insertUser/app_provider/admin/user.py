from core.app_provider.api.get import site_connection
from core.config.Config import main_add_user_url, user_timeout
from core.model.DataType import user_add_data


def insert_user(f_name, l_name, email, phone, password):
    payload = get_data(f_name, l_name, email, phone, password)

    site_connection(main_add_user_url, user_timeout * 2, data=payload)


def get_data(f_name, l_name, email, phone, password):
    data_temp = dict(user_add_data)
    key = sorted(list(data_temp.keys()), key=key_order)

    data_temp[key[0]] = f_name  # for fname
    data_temp[key[1]] = l_name  # for lname
    data_temp[key[2]] = email  # for email
    data_temp[key[3]] = phone  # for phone
    data_temp[key[4]] = password  # for password
    return data_temp


def key_order(key):
    import difflib
    app_order = ["fname", "lname", "email", "phone", "password"]

    key = difflib.get_close_matches(key, app_order)

    if len(key) != 0:
        if key[0] == "fname":
            return 1
        elif key[0] == "lname":
            return 2
        elif key[0] == "email":
            return 3
        elif key[0] == "phone":
            return 4
        elif key[0] == "password":
            return 5
        else:
            return 0
    else:
        return 0
