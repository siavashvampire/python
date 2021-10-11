from tinydb import TinyDB, Query

from core.config.Config import PhoneDBPath, phone_table_name

prop = Query()
db = TinyDB(PhoneDBPath)
db.drop_table(phone_table_name)
db.close()
db = TinyDB(PhoneDBPath).table(phone_table_name)
i = {"Name": "Siavash Sepahi", "id": 459504117, "SendONOFF": 1, "Access": 1, "Units": [-3, -2, -1], "phase": [0]}
db.upsert(i, prop.id == i["id"])
