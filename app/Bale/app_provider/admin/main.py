import os
from time import sleep
from datetime import datetime
from queue import Queue
from threading import Thread
from typing import List

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from tinydb import TinyDB

import app.Logging.app_provider.admin.MersadLogging as Logging
from app.Bale.model.PhoneModel import PhoneData as Phones, PhoneData
from app.Bale.model.SMSPhoneModel import SMSPhoneData as SMSPhones
from app.LineMonitoring.app_provider.api.ReadText import EnrollOK, EnrollRepeat, ActiveText, DeactivationText, \
    CheckingText, SendExportText, SendingHelpText, PDFReport, CSVReport, NotInsert, BlockText, HelpText, \
    ShowAccessText, PhoneCreateText, AccessOFFText, AccessONText, FailedText
from app.ResourcePath.app_provider.admin.main import resource_path
from core.RH.ResponseHandler import CounterResponseHandler as RHCounter
from core.RH.ResponseHandler import GetActivityeHandler
from core.RH.ResponseHandler import PhoneNumberResponseHandler as RHPhone
from core.app_provider.api.get import site_connection, get_from_site_db
from core.config.Config import bale_token, bale_base_url, phone_db_path, sms_phone_db_path, main_get_activity_url, \
    main_get_counter_url, main_export_url, bale_get_timeout, help_file_name, help_pdf_timeout, login_developer, get_phones_url, \
    phones_get_timeout, phone_table_name, sms_phone_table_name, get_sms_phones_url
from core.model.DataType import bale_data, bale_app_name
from core.theme.pic import Pics


def get_online_counter(units, phase):
    if not units:
        return "واحدی برای شما تعریف نشده"
    else:
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'postman-token': "96d1603f-b13b-0da7-a12e-467ec0dfa771"
        }
        payload = ""
        if (units is True) and (phase is True):
            payload = ""
        elif (units is True) and not (phase is True):
            payload = "phase=(" + ",".join([str(item) for item in phase]) + ")"
        elif not (units is True) and (phase is True):
            payload = "unitId=(" + ",".join([str(item) for item in units]) + ")"
        elif not (units is True) and not (phase is True):
            payload = "unitId=(" + ",".join([str(item) for item in units]) + ")&phase=(" + ",".join(
                [str(item) for item in phase]) + ")"

        status, r = site_connection(main_get_counter_url, bale_get_timeout, data=payload, header=headers)[0:2]

        if not status:
            Logging.bale_log("Counter", str(r))
        return RHCounter(r, status)


def get_sensor_activity(units, phase):
    if not units:
        return "واحدی برای شما تعریف نشده"
    else:
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'postman-token': "96d1603f-b13b-0da7-a12e-467ec0dfa771"
        }
        payload = ""
        if (units is True) and (phase is True):
            payload = ""
        elif (units is True) and not (phase is True):
            payload = "phase=(" + ",".join([str(item) for item in phase]) + ")"
        elif not (units is True) and (phase is True):
            payload = "unitId=(" + ",".join([str(item) for item in units]) + ")"
        elif not (units is True) and not (phase is True):
            payload = "unitId=(" + ",".join([str(item) for item in units]) + ")&phase=(" + ",".join(
                [str(item) for item in phase]) + ")"
        status, r = site_connection(main_get_activity_url, bale_get_timeout, data=payload, header=headers)[0:2]

        if not status:
            Logging.bale_log("GetSensorActivity", str(r))
        return GetActivityeHandler(r, status)


class BaleMain:
    phones_bale: List[PhoneData]
    phones_SMS: List[SMSPhones]

    def __init__(self, sender_queue, bale_status_label=None, thread_label=None):
        self.Flag_Bale = False
        self.should_stop = False
        self.state = False
        self.stop_check = False
        self.Trying = False
        self.stop_thread = False
        self.BaleStatus_label = bale_status_label
        self.data_type = bale_data
        self.thread_label = thread_label
        self.sender_queue = sender_queue
        self.updater = Updater(token=bale_token, base_url=bale_base_url)
        dp = self.updater.dispatcher
        self.TextQ = Queue()
        self.create_phones()

        dp.add_handler(CommandHandler(command='AllCounter', callback=self.all_counter))
        dp.add_handler(CommandHandler(command='enroll', callback=self.enroll))
        dp.add_handler(CommandHandler(command='AllActivity', callback=self.all_activity))
        dp.add_handler(CommandHandler(command='ActiveONOFF', callback=self.active_on_off))
        dp.add_handler(CommandHandler(command='DeactiveONOFF', callback=self.deactivate_on_off))
        dp.add_handler(CommandHandler(command='ShiftReportCSV', callback=self.shift_report_csv))
        dp.add_handler(CommandHandler(command='ShiftReportPDF', callback=self.shift_report_pdf))
        dp.add_handler(CommandHandler(command='ShiftOFFReportCSV', callback=self.shift_off_report_csv))
        dp.add_handler(CommandHandler(command='ShiftOFFReportPDF', callback=self.shift_off_report_pdf))
        dp.add_handler(CommandHandler(command='HelpPDF', callback=self.help_pdf))
        dp.add_handler(CommandHandler(command='Help', callback=self.help))
        dp.add_handler(CommandHandler(command='MakePhone', callback=self.make_phone))
        dp.add_handler(CommandHandler(command='ShowAccess', callback=self.show_access))

        dp.add_handler(MessageHandler(Filters.text, self.checking_text))

        self.OpenThread = Thread(target=self.open_bale, args=(lambda: self.stop_thread,))
        self.OpenThread.start()
        Logging.bale_log("Bale Init", "OpenThread is run")
        self.SendThread = Thread(target=self.send_to_phones, args=(lambda: self.stop_thread,))
        self.SendThread.start()
        Logging.bale_log("Bale Init", "SendThread is run")

    def create_phones(self):
        r = TinyDB(phone_db_path).table(phone_table_name).all()
        phones = TinyDB(sms_phone_db_path).table(sms_phone_table_name).all()
        self.phones_bale = [Phones(i["Name"], i["id"], i["SendONOFF"], i["Units"], i["phase"], i["Access"]) for i in r]
        self.phones_SMS = [SMSPhones(i["Name"], i["Phone"], i["Units"], i["phase"], i["Access"]) for i in phones]

    def send_to_phones(self, stop_thread):
        while True:
            if self.Flag_Bale:
                text, id_temp, phase, choose = self.TextQ.get()
                self.TextQ.task_done()
                if text:
                    if choose == 1:
                        for i in self.phones_bale:
                            # if self.Flag_Bale == False:
                            #     self.TextQ.put([text , id_temp , phase , choose])
                            #     break
                            if i.SendONOFF or (id_temp < 0):
                                if i.Access:
                                    if i.check(id_temp, phase):
                                        try:
                                            self.updater.bot.send_message(i.id, text)
                                        except:
                                            self.Flag_Bale = False
                                            Logging.bale_log("Send Thread", "Error in send with id " + str(i.id))
                                            if login_developer:
                                                print("Error in send with id " + str(i.id))
                    if choose == 2:
                        for phone in self.phones_SMS:
                            if not self.Flag_Bale:
                                self.TextQ.put([text, id_temp, phase, choose])
                                break
                            if phone.Access:
                                if phone.Check(id_temp, phase):
                                    try:
                                        phone.Send(text)
                                    except:
                                        self.Flag_Bale = False
                                        Logging.bale_log("Send Thread",
                                                         "Error in send SMS with Number " + str(phone.Phone))
                                        if login_developer:
                                            print("Error in send SMS with Phone " + str(phone.Phone))
                else:
                    if stop_thread():
                        Logging.bale_log("Main Send Thread", "Stop")
                        print("stop Bale Send")
                        break
            else:
                sleep(1)
                if stop_thread():
                    Logging.bale_log("Main Send Thread", "Stop")
                    print("stop Bale Send")
                    break

    def open_bale(self, stop_thread):
        now = datetime.now()
        first = True
        while True:
            if stop_thread():
                Logging.bale_log("Main Open Thread", "Stop")
                print("stop Bale Open")
                break
            diff = datetime.now() - now
            if diff.seconds > 2 * 60 or first:
                first = False
                now = datetime.now()
                if not self.Flag_Bale:
                    if not self.Trying:
                        try:
                            self.Trying = True
                            self.updater.bot.delete_webhook()
                            self.updater.start_polling(poll_interval=2)
                            self.Flag_Bale = True
                            if self.BaleStatus_label is not None:
                                self.BaleStatus_label.setPixmap(Pics.checkMark)
                            Logging.bale_log("Main Open Thread", "Connect")
                        except:
                            self.Flag_Bale = False
                            if self.BaleStatus_label is not None:
                                self.BaleStatus_label.setPixmap(Pics.deleteMark)
                        self.Trying = False
            sleep(20)

    def enroll(self, bot, update):
        # TODO: bayad intori beshe k mostaghim befreste vase site v az to site ham update kone
        name = update.message.from_user.first_name
        id_temp = update.message.chat.id
        if RHPhone(name, id_temp):
            self.create_phones()
            self.sender_queue.put(
                {"app": bale_app_name,
                 "data": self.get_data(id_temp, name)})
            update.message.reply_text(EnrollOK.format(Name=name, id=id_temp))
        else:
            update.message.reply_text(EnrollRepeat.format(Name=name, id=id_temp))

    def all_counter(self, bot, update):
        id_temp = update.message.chat.id
        acc = self.handle_access(id_temp)
        if type(acc) == Phones:
            try:
                update.message.reply_text(get_online_counter(acc.get_abs_unit_id(), acc.get_phase()))
            except Exception as e:
                if acc.check_developer_access():
                    update.message.reply_text(e)
                Logging.bale_log("AllCounter", str(e))
        elif type(acc) == str:
            update.message.reply_text(acc)

    def all_activity(self, bot, update):
        id_temp = update.message.chat.id
        acc = self.handle_access(id_temp)
        if type(acc) == Phones:
            try:
                update.message.reply_text(get_sensor_activity(acc.get_abs_unit_id(), acc.get_phase()))
            except Exception as e:
                if acc.check_developer_access():
                    update.message.reply_text(e)
                Logging.bale_log("AllActivity", str(e))
        elif type(acc) == str:
            update.message.reply_text(acc)

    def active_on_off(self, bot, update):
        id_temp = update.message.chat.id
        acc = self.handle_access(id_temp)
        if type(acc) == Phones:
            try:
                acc.on_off_active(1)
                update.message.reply_text(ActiveText)
            except Exception as e:
                if acc.check_developer_access():
                    update.message.reply_text(e)
                Logging.bale_log("ActiveONOFF", str(e))
        elif type(acc) == str:
            update.message.reply_text(acc)

    def deactivate_on_off(self, bot, update):
        id_temp = update.message.chat.id
        acc = self.handle_access(id_temp)
        if type(acc) == Phones:
            try:
                acc.on_off_active(0)
                update.message.reply_text(DeactivationText)
            except Exception as e:
                if acc.check_developer_access():
                    update.message.reply_text(e)
                Logging.bale_log("DeactivateONOFF", str(e))
        elif type(acc) == str:
            update.message.reply_text(acc)

    def shift_report_pdf(self, bot, update):
        id_temp = update.message.chat.id
        acc = self.handle_access(id_temp)
        if type(acc) == Phones:
            s = update.message.reply_text(text=PDFReport)
            payload = "showField%5B%5D=data.phase&showField%5B%5D=data.unitId&showField%5B%5D=CONCAT(" \
                      "data.tile_width%2C%20'%C3%97'%2C%20data.tile_length)&showField%5B%5D=data.tile_name" \
                      "&showField%5B%5D=data.counterAll&showField%5B%5D=data.m1&showField%5B%5D=data.m2&showField" \
                      "%5B%5D=data.m3&showField%5B%5D=data.m4&showField%5B%5D=data.m5&showField%5B%5D=data.p1" \
                      "&showField%5B%5D=data.p2&showField%5B%5D=data.p3&showField%5B%5D=data.p4&showField%5B%5D" \
                      "=data.p5&getPDF=1 "
            headers = {
                'content-type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache",
                'postman-token': "5d696566-cf4e-c868-37af-e4888d8ba255"
            }
            status, r = site_connection(main_export_url, bale_get_timeout * 2, data=payload, header=headers)[0:2]
            bot.delete_message(id_temp, s['message_id'])

            # if acc.CheckDeveloperAccess():
            #     update.message.reply_text(r)
            if not status:
                update.message.reply_text(text=r)
            else:
                temp_path = resource_path("Export.pdf")
                try:
                    with open(temp_path, 'wb') as output:
                        output.write(r.content)
                    #     TODO:bayad hatman hatman check beshe chon content onvar mani nemdide
                    s = update.message.reply_text(text=SendExportText)
                    update.message.reply_document(document=open(file=temp_path, mode='rb'))
                    bot.delete_message(id_temp, s['message_id'])
                    os.remove(temp_path)
                except Exception as e:
                    if acc.check_developer_access():
                        update.message.reply_text(e)
                    Logging.bale_log("ReportPDF", str(e))
        elif type(acc) == str:
            update.message.reply_text(acc)

    def shift_report_csv(self, bot, update):
        id_temp = update.message.chat.id
        acc = self.handle_access(id_temp)
        if type(acc) == Phones:
            s = update.message.reply_text(text=CSVReport)
            payload = "showField%5B%5D=data.phase&showField%5B%5D=data.unitId&showField%5B%5D=CONCAT(" \
                      "data.tile_width%2C%20'%C3%97'%2C%20data.tile_length)&showField%5B%5D=data.tile_name" \
                      "&showField%5B%5D=data.counterAll&showField%5B%5D=data.m1&showField%5B%5D=data.m2&showField" \
                      "%5B%5D=data.m3&showField%5B%5D=data.m4&showField%5B%5D=data.m5&showField%5B%5D=data.p1" \
                      "&showField%5B%5D=data.p2&showField%5B%5D=data.p3&showField%5B%5D=data.p4&showField%5B%5D" \
                      "=data.p5&getPDF=0 "
            headers = {
                'content-type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache",
                'postman-token': "5d696566-cf4e-c868-37af-e4888d8ba255"
            }
            status, r = site_connection(main_export_url, bale_get_timeout * 2, data=payload, header=headers)[0:2]
            bot.delete_message(id_temp, s['message_id'])

            # if acc.CheckDeveloperAccess():
            #     update.message.reply_text(r)
            if not status:
                update.message.reply_text(text=r)
            else:
                temp_path = resource_path("Export.csv")
                try:
                    with open(temp_path, 'wb') as output:
                        output.write(r.content)
                    #     TODO:bayad hatman hatman check beshe chon content onvar mani nemdide
                    s = update.message.reply_text(text=SendExportText)
                    update.message.reply_document(document=open(file=temp_path, mode='rb'))
                    bot.delete_message(id_temp, s['message_id'])
                    os.remove(temp_path)
                except Exception as e:
                    if acc.check_developer_access():
                        update.message.reply_text(e)
                    Logging.bale_log("ReportCSV", str(e))
        elif type(acc) == str:
            update.message.reply_text(acc)

    def shift_off_report_pdf(self, bot, update):
        id_temp = update.message.chat.id
        acc = self.handle_access(id_temp)
        if type(acc) == Phones:
            s = update.message.reply_text(text=PDFReport)
            payload = "showField%5B%5D=data.phase&showField%5B%5D=data.unitId&showField%5B%5D=arch1.reason" \
                      "&showField%5B%5D=arch1.description&showField%5B%5D=arch1.JStart_time&showField%5B%5D" \
                      "=TIMESTAMPDIFF(MINUTE%2Carch1.Start_time%2Carch1.End_Time)&getPDF=1 "
            headers = {
                'content-type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache",
                'postman-token': "5d696566-cf4e-c868-37af-e4888d8ba255"
            }
            status, r = site_connection(main_export_url, bale_get_timeout * 2, data=payload, header=headers)[0:2]
            bot.delete_message(id_temp, s['message_id'])

            # if acc.CheckDeveloperAccess():
            #     update.message.reply_text(r)
            if not status:
                update.message.reply_text(text=r)
            else:
                temp_path = resource_path("OFFExport.pdf")
                try:
                    with open(temp_path, 'wb') as output:
                        output.write(r.content)
                    #     TODO:bayad hatman hatman check beshe chon content onvar mani nemdide
                    s = update.message.reply_text(text=SendExportText)
                    update.message.reply_document(document=open(file=temp_path, mode='rb'))
                    bot.delete_message(id_temp, s['message_id'])
                    os.remove(temp_path)
                except Exception as e:
                    if acc.check_developer_access():
                        update.message.reply_text(e)
                    Logging.bale_log("OFFReportPDF", str(e))
        elif type(acc) == str:
            update.message.reply_text(acc)

    def shift_off_report_csv(self, bot, update):
        id_temp = update.message.chat.id
        acc = self.handle_access(id_temp)
        if type(acc) == Phones:
            s = update.message.reply_text(text=CSVReport)
            payload = "showField%5B%5D=data.phase&showField%5B%5D=data.unitId&showField%5B%5D=arch1.reason" \
                      "&showField%5B%5D=arch1.description&showField%5B%5D=arch1.JStart_time&showField%5B%5D" \
                      "=TIMESTAMPDIFF(MINUTE%2Carch1.Start_time%2Carch1.End_Time)&getPDF=0 "
            headers = {
                'content-type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache",
                'postman-token': "5d696566-cf4e-c868-37af-e4888d8ba255"
            }
            status, r = site_connection(main_export_url, bale_get_timeout * 2, data=payload, header=headers)[0:2]
            bot.delete_message(id_temp, s['message_id'])

            # if acc.CheckDeveloperAccess():
            #     update.message.reply_text(r)
            if not status:
                update.message.reply_text(text=r)
            else:
                temp_path = resource_path("OFFExport.csv")
                try:
                    with open(temp_path, 'wb') as output:
                        output.write(r.content)
                    #     TODO:bayad hatman hatman check beshe chon content onvar mani nemdide
                    s = update.message.reply_text(text=SendExportText)
                    update.message.reply_document(document=open(file=temp_path, mode='rb'))
                    bot.delete_message(id_temp, s['message_id'])
                    os.remove(temp_path)
                except Exception as e:
                    if acc.check_developer_access():
                        update.message.reply_text(e)
                    Logging.bale_log("OFFReportCSV", str(e))
        elif type(acc) == str:
            update.message.reply_text(acc)

    def help_pdf(self, bot, update):
        id_temp = update.message.chat.id
        acc = self.handle_access(id_temp)
        if type(acc) == Phones:
            try:
                s = update.message.reply_text(text=SendingHelpText)
                update.message.reply_document(document=open(file=help_file_name + ".pdf", mode='rb'),
                                              timeout=help_pdf_timeout)
                bot.delete_message(id_temp, s['message_id'])
            except Exception as e:
                if acc.check_developer_access():
                    update.message.reply_text(e)
                update.message.reply_text(text=FailedText)
                Logging.bale_log("HelpPDF", str(e))
        elif type(acc) == str:
            update.message.reply_text(acc)

    def help(self, bot, update):
        id_temp = update.message.chat.id
        acc = self.handle_access(id_temp)
        if type(acc) == Phones:
            try:
                update.message.reply_text(HelpText)
            except Exception as e:
                if acc.check_developer_access():
                    update.message.reply_text(e)
                Logging.bale_log("Help", str(e))
        elif type(acc) == str:
            update.message.reply_text(acc)

    def make_phone(self, bot, update):
        try:
            id_temp = update.message.chat.id
            acc = self.handle_access(id_temp)
            if type(acc) == Phones:
                if acc.check_developer_access():
                    try:
                        self.create_phones()
                        update.message.reply_text(PhoneCreateText)
                    except Exception as e:
                        update.message.reply_text(e)
                else:
                    update.message.reply_text("دسترسی شما مناسب نیست")
            elif type(acc) == str:
                update.message.reply_text(acc)
        except Exception as e:
            update.message.reply_text(e)

    def show_access(self, bot, update):
        id_temp = update.message.chat.id
        acc = self.handle_access(id_temp)
        if type(acc) == Phones:
            if acc.check_developer_access():
                text_temp = ""
                for i in self.phones_bale:
                    text_temp += ShowAccessText.format(id=i.id, Name=i.Name, Access=i.Access)
                update.message.reply_text(text_temp)
            else:
                update.message.reply_text("دسترسی شما مناسب نیست")
        elif type(acc) == str:
            update.message.reply_text(acc)

    def checking_text(self, bot, update):
        id_temp = update.message.chat.id
        acc = self.handle_access(id_temp)
        if type(acc) == Phones:
            if acc.check_developer_access():
                text = update.message.text
                x = text.split(" : ")
                try:
                    id_rec = int(x[0])
                    text_rec = x[1]
                    iscommand, text = self.check_command(id_rec, text_rec)
                    if not iscommand:
                        self.updater.bot.send_message(id_rec, text_rec)
                    else:
                        update.message.reply_text(text)
                except Exception as e:
                    update.message.reply_text(str(e))
                    Logging.bale_log("Send Thread", "Error in send with id " + str(x[0]))
                return
            else:
                update.message.reply_text(CheckingText)
                self.TextQ.put([str(id_temp) + " : " + update.message.text, -2, -4, 1])
        elif type(acc) == str:
            update.message.reply_text(acc)

    def restart_thread(self):
        self.stop_thread = False
        if not (self.OpenThread.is_alive()):
            self.OpenThread = Thread(target=self.open_bale, args=(lambda: self.stop_thread,))
            self.OpenThread.start()
        if not (self.SendThread.is_alive()):
            self.SendThread = Thread(target=self.send_to_phones, args=(lambda: self.stop_thread,))
            self.SendThread.start()

    def get_phone(self, id_temp):
        for i in self.phones_bale:
            if i.id == id_temp:
                return i
        return False

    def handle_access(self, id_temp):
        phone = self.get_phone(id_temp)
        if phone is False:
            return NotInsert
        else:
            if phone.check_access():
                return phone
            else:
                return BlockText

    def check_command(self, id_temp, text):
        iscommand = False
        phone = self.get_phone(id_temp)
        if text == "Access ON":
            iscommand = True
            if type(phone) == Phones:
                phone.set_access(1)
                self.create_phones()
                self.updater.bot.send_message(id_temp, AccessONText)
                text = PhoneCreateText + AccessONText

        if text == "Access OFF":
            iscommand = True
            if type(phone) == Phones:
                phone.set_access(0)
                self.create_phones()
                self.updater.bot.send_message(id_temp, AccessOFFText)
                text = PhoneCreateText + AccessOFFText

        if phone is False:
            text = "شماره در سامانه ثبت نشده"

        return iscommand, text

    def state_thread(self, state=False, program=False):
        if program is False:
            if self.state:
                self.should_stop = True
                self.stop_func()
            else:
                self.should_stop = False
                self.start_func()
        else:
            if state is True:
                if not self.should_stop:
                    self.start_func()
            if state is False:
                self.stop_func()

    def start_func(self):
        self.stop_thread = False
        self.restart_thread()
        self.stop_check = False
        self.state = True
        self.thread_label.setIcon(Pics.ON)

    def stop_func(self):
        self.stop_thread = True
        self.TextQ.put([0, 0, 0, 0])
        self.stop_check = True
        self.state = False
        self.OpenThread.join()
        self.SendThread.join()
        self.thread_label.setIcon(Pics.OFF)

    def check(self):
        if not (self.OpenThread.is_alive() and self.SendThread.is_alive()):
            if not self.stop_check:
                self.stop_thread = False
                self.restart_thread()
            if self.state:
                self.thread_label.setIcon(Pics.OFF)
                self.state = False
        else:
            if not self.state:
                self.thread_label.setIcon(Pics.ON)
                self.state = True

    def get_data(self, id_temp, name):
        data_temp = dict(self.data_type)
        key = sorted(list(data_temp.keys()), key=self.key_order)
        data_temp[key[0]] = id_temp  # for id
        data_temp[key[1]] = name  # for label
        return data_temp

    @staticmethod
    def key_order(key):
        import difflib
        app_order = ["id", "name"]

        key = difflib.get_close_matches(key, app_order)

        if len(key) != 0:
            if key[0] == "id":
                return 1
            elif key[0] == "name":
                return 2
            else:
                return 0
        else:
            return 0

    @staticmethod
    def read_all_sms_phone():
        get_from_site_db(get_sms_phones_url, phones_get_timeout, sms_phone_db_path, sms_phone_table_name)

    @staticmethod
    def read_all_phone():
        get_from_site_db(get_phones_url, phones_get_timeout, phone_db_path, phone_table_name)

    def db_update_all(self):
        self.read_all_phone()
        self.read_all_sms_phone()

    def update_system(self):
        self.db_update_all()
        self.create_phones()
