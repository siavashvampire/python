from datetime import datetime

from tinydb import TinyDB

from core.config.Config import logging_db_path, time_format

LoggingDB = TinyDB(logging_db_path)
Main = LoggingDB.table('Main')
PLC = LoggingDB.table('DA')
Render = LoggingDB.table('LineMonitoring')
electrical = LoggingDB.table('LineMonitoring')
Bale = LoggingDB.table('Bale')
Sender = LoggingDB.table('Sender')
# TODO: bayad inja y thread bezarin v dakhele hamin function haw queue on thread ro por konim

def write_type(location, result):
    return {'location': location, "result": result, "Time": str(datetime.now().strftime(time_format))}


def main_log(location, result):
    # Main.insert(write_type(location, result))
    pass


def da_log(location, result):
    # PLC.insert(write_type(location, result))
    pass


def line_monitoring_log(location, result):
    # Render.insert(write_type(location, result))
    pass


def electrical_log(location, result):
    # electrical.insert(write_type(location, result))
    pass


def bale_log(location, result):
    # Bale.insert(write_type(location, result))
    pass


def sender_log(location, result):
    Sender.insert(write_type(location, result))
    pass


def drop_main_db():
    LoggingDB.drop_table('Main')


def drop_da_db():
    LoggingDB.drop_table('DA')


def drop_line_monitoring_db():
    LoggingDB.drop_table('LineMonitoring')


def drop_bale_db():
    LoggingDB.drop_table('Bale')


def drop_sender_db():
    LoggingDB.drop_table('Sender')


def clear_all_db():
    LoggingDB.drop_tables()
