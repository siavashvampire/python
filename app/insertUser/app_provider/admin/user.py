from core.app_provider.api.get import site_connection
from core.config.Config import main_add_user_url, user_timeout


def insert_user(f_name, l_name, email, phone, password):
    payload = {"fname": str(f_name), "lname": str(l_name), "email": str(email), "phone": str(phone),
               "password": str(password), "groupId": "6", "verified": "1"}

    site_connection(main_add_user_url, user_timeout * 2, data=payload)
