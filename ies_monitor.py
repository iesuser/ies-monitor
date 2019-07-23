#!/usr/bin/python3
# -*- coding: utf-8 -*-


""" შენიშნები
1. mysql -დან მონაცემების წამოღება ხდება პირდაპირი კავშირით . მოსაფიქრებელია ალტერნატიული გზა
2. Segmentation fault (core dumped) ზოგჯერ წერს , სანახავია მიზეზი!!!
"""
import sys
import pymysql  # 0.9.3
import sqlite3
import socket
import json
import time
import threading
import os
import argparse
import logging
import select
import datetime

from PyQt5 import QtCore, QtGui, QtWidgets, uic  # 5.12.2
from message_dialog import Ui_Dialog

# ies_monitor სკრიპტის ip-i რომელზედაც ვიღებთ სერვერიდან შეტყობინებას ies_monitoring_server-დან
# ip - ს ვგებულობთ სერვერთან დაკავშირების მერე
# არ არის საჭირო ხელით გაწერა, თავიდან არის ცარიელი
ies_monitor_ip = ""

# ies_monitor სკრიპტის port რომელზედაც ვიღებთ სერვერიდან შეტყობინებას ies_monitoring_server-დან
ies_monitor_port = 54321

# log ფაილის სახელი
log_filename = "log"

# ies_monitoring_server-თან კავშირის შემოწმების მიახლოებითი ინტერვალი წამებში
test_ies_monitoring_server_connection_delay = 5

# ies_monitoring_server-ის ip-ი მისამართი
ies_monitoring_server_ip = "10.0.0.153"

# ies_monitoring_server-ის პორტი
ies_monitoring_server_port = 12345

# mysql-ის ip მისამართი
mysql_server_ip = "localhost"

# mysql სერვერის user-ი
mysql_server_user = "root"

# mysql-სერვერის user-ის პაროლი
mysql_user_pass = "AcharuliXachapuri123!"

# mysql-სერვერის მონაცემთა ბაზის სახელი
mysql_database_name = "ies_monitoring_server"

# mysql-სერვერის პორტი
mysql_server_port = 3306

# მესიჯის buffer_size
buffer_size = 2048

# დაყოვნება პროგრამის ისეთ ციკლებში სადაც საჭიროა/რეკომენდირებულია შენელებული მუშაობა
delay = 0.1


# -------------------------------------------------------------------------------------------------


# კონსტანტები გამოიყენება სერვერთან კავშირის სტატუსის განსაზღვრისთვის
# სერვერთან კავშირი გაწყვეტილია
DISCONNECTED = 0
# სერვერთან დაკავშირებულია
CONNECTED = 1
# სერვერთან კავშირის შემოწმება
TESTING = 2


class ConsoleFormatter(logging.Formatter):
    """
    კლასით განვსაზღვრავთ ტერმინალში გამოტანილი მესიჯის ფორმატს.

    """
    date_format = "%H:%M:%S"
    default_format = "%(asctime)s [%(levelname)s] %(msg)s"
    info_format = "%(msg)s"

    def __init__(self):
        super().__init__(fmt=ConsoleFormatter.default_format, datefmt=ConsoleFormatter.date_format, style='%')

    def format(self, record):
        # დავიმახსოვროთ თავდაპირველი ფორმატი
        format_orig = self._style._fmt

        if record.levelno == logging.INFO:
            self._style._fmt = ConsoleFormatter.info_format

        # შევცვალოთ თავდაპირველი ფორმატი
        result = logging.Formatter.format(self, record)

        # დავაბრუნოთ თავდაპირველი ფორმატი
        self._style._fmt = format_orig

        return result


# parser - ის შექმნა
parser = argparse.ArgumentParser(description="???!! ...დასაწერია პროგრამის განმარტება")
parser.add_argument('-d', '--debug', action='store_true', help='ლოგგერის დონის შეცვლა debug ზე')
args = parser.parse_args()

# logger - ის შექმნა
logger = logging.getLogger('ies_monitoring_server_logger')
logger.setLevel(logging.DEBUG)

# შევქმნათ console handler - ი და განვსაზღვროთ დონე და ფორმატი
console_handler = logging.StreamHandler(sys.stdout)

# არგუმენტიდან გამომდინარე დავაყენოთ ტერმინალში ლოგგერის დონე
if args.debug:
    console_handler.setLevel(logging.DEBUG)
else:
    console_handler.setLevel(logging.INFO)

console_formatter = ConsoleFormatter()
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# FileHandler - ის შექმნა. დონის და ფორმატის განსაზღვრა
log_file_handler = logging.FileHandler(log_filename)
log_file_handler.setLevel(logging.DEBUG)
log_file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
log_file_handler.setFormatter(log_file_formatter)
logger.addHandler(log_file_handler)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('main_window.ui', self)

        # ცვლადი რომლის საშუალებით პროგრამის დახურვისას ითიშება თრედები
        self.application_is_closing = False

        # სერვერთან კავშირის სტატუსი
        self.connection_state = DISCONNECTED

        # socket - ობიექტის შექმნა
        self.listener_socket = socket.socket()

        reconnect = QtWidgets.QAction("&Reconnect", self)
        reconnect.triggered.connect(lambda: self.send_registration_request_to_ies_monitoring_server(start_listening_thread=False))

        menu_bar = self.menuBar()
        connect_menu = menu_bar.addMenu('&Connection')
        connect_menu.addAction(reconnect)

        # QAction ობიექტის შექმნა
        main_window_close_action = QtWidgets.QAction("Quit", self)

        # main_window_close_action ხდომილების შემთხვევაში გამოვიძახოთ main_window_close_event ფუნქცია
        main_window_close_action.triggered.connect(self.closeEvent)

        # message_table - ზე ორჯერ დაჭერით გამოვიძახოთ message_table_double_click
        self.message_table.doubleClicked.connect(self.message_table_double_click)

        # ???
        self.mysql_table_col_names = [
            "message_id", "sent_message_datetime", "message_type",
            "message_title", "text", "client_ip", "client_script_name"
        ]

        # ???
        self.mysql_table_col_readable_names = [
            "ID", "Time", "Message Type",
            "Message Title", "Message",
            "Client IP", "Script Name"
        ]

        # ეშვება update_connection_status ფუნქცია თრედად
        threading.Thread(target=self.update_connection_status).start()

        # ეშვება communicate_to_ies_monitoring_server_thread ფუნქცია თრედად
        threading.Thread(target=self.communicate_to_ies_monitoring_server_thread).start()

        # ვიძახებთ set_qtablewidget_style ფუნქციას
        self.set_qtablewidget_style()

        # ვიძახებთ connect_to_mysql ფუნქციას
        self.connect_to_mysql()

        # ვიძახებთ load_messages_from_mysql ფუნქციას
        self.load_messages_from_mysql()

        # ვიძახებთ connect_to_sqlite ფუნქციას
        self.connect_to_sqlite()

        # ვიძახებთ check_opened_messages ფუნქციას
        self.check_opened_messages()

    def update_connection_status(self):
        """ ფუნქცია სტატუს ბარში აჩვენებს ies_monitoring_server -თან კავშირის სტატუსს """

        while self.application_is_closing is False:
            if self.connection_state is CONNECTED:
                self.statusbar.showMessage("CONNECTED")
            elif self.connection_state is TESTING:
                self.statusbar.showMessage("TESTING")
            elif self.connection_state is DISCONNECTED:
                self.statusbar.showMessage("DISCONNECTED")
            time.sleep(delay)

    def connect_ies_monitoring_server(self, verbose=True):
        """ ფუნქცია უკავშირდება ies_monitoring_server-ს """

        # connection სოკეტის შექმნა
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # დავუკავშირდეთ ies_monitoring_server-ს
            connection.connect((ies_monitoring_server_ip, ies_monitoring_server_port))
            if verbose is True:
                logger.debug("სერვერთან კავშირი დამყარებულია")
        except Exception as ex:
            if verbose is True:
                logger.warning("სერვერთან კავშირი ვერ დამყარდა. " + str(ex))
            return False
        return connection

    def connection_close(self, connection, addr=None):
        """ ხურავს (კავშირს სერვერთან) პარამეტრად გადაცემულ connection socket ობიექტს """

        if addr is None:
            logger.debug("listener_socket სოკეტის დახურვა " + str(connection.getsockname()))
        else:
            logger.debug("კავშირის დახურვა " + str(addr))
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()

    def dictionary_to_bytes(self, dictionary_message):
        """ dictionary ტიპის ობიექტი გადაყავს bytes ტიპში
        რადგან socket ობიექტის გამოყენებით მონაცემები იგზავნება bytes ტიპში
        მოსახერხებელია რომ გვქონდეს ფუნქციები რომელიც dictionary-ის გადაიყვანს
        bytes ტიპში და პირიქით """
        return bytes(json.dumps(dictionary_message), 'utf-8')

    def bytes_to_dictionary(self, json_text):
        """ json ტექსტს აკონვერტირებს dictionary ტიპში """
        return json.loads(json_text.decode("utf-8"))

    def communicate_to_ies_monitoring_server_thread(self):
        """
            ფუნქცია ამოწმებს სერვერთან კავშირს, კავშირის დამყარების შემთხვევაში ვგებულობთ მიმდინარე
            ies_monitor-ის ip-ის, ეშვება listening_to_ies_monitoring_server ფუნქცია (ies_monitor-იწყებს მოსმენას)
            და ვაგზავნით რეგისტრაციის მოთხოვნას სანამ სერვერი არ გამოაგზავნის რეგისტრაციის დადასტურებას

        """

        # ies_monitoring_server-თან დაკავშირება
        connection = self.connect_ies_monitoring_server(verbose=False)

        # სერვერთან დაკავშირების მცდელობის დრო
        test_server_connection_datetime = datetime.datetime.now()

        # ციკლი სერვერთან დასაკავშირებლად. ციკლიდან გამოვდივართ იმ შემთხვევაში თუ
        # კავშირი დამყარდა სერვერთან ან თუ პროგრამა იხურება
        while connection is False and self.application_is_closing is False:
            # შევამოწმოთ თუ სერვერთან დაკავშირების ცდიდან გავიდა test_ies_monitoring_server_connection_delay წამი
            if (datetime.datetime.now() - test_server_connection_datetime) > datetime.timedelta(seconds=test_ies_monitoring_server_connection_delay):
                logger.warning("პროგრამის ჩატვირთვის პროცესში ვერ მოხერხდა სერვერთან დაკავშირება")
                # ies_monitoring_server-თან დაკავშირება
                connection = self.connect_ies_monitoring_server(verbose=False)

                # სერვერთან დაკავშირების მცდელობის დრო
                test_server_connection_datetime = datetime.datetime.now()

            # დაყოვნება
            time.sleep(delay)

        # თუ კავშირი დამყარდა ies_monitoring_server-თან
        if connection is not False:
            global ies_monitor_ip

            # შევინახოთ მიმდინარე ies_monitor-ის ip
            ies_monitor_ip = connection.getsockname()[0]

            logger.debug("პროგრამის ჩატვირთვის პროცესში სერვერთან კავშირი დამყარდა და განისაზღვრა "
                         "ies_monitor-ის ip მისამართი: {}".format(ies_monitor_ip))
            # ies_monitor-იწყებს მოსმენას
            threading.Thread(target=self.listening_to_ies_monitoring_server).start()

            self.register_to_ies_monitoring_server()

    def register_to_ies_monitoring_server(self):
        """ ფუნქცია აგზავნის რეგისტრაციის მოთხოვნას ies_monitoring_server -თან და ელოდება მისგან დასტურს """

        # შეტყობინება რეგისტრაციაზე არ გაგზავნილა
        registration_message_sent = False

        self.registration_verified = False

        # ციკლი სერვერთან რეგისტრაციის დასადასტურებლად
        # ციკლიდან გამოვდივართ იმ შემთხვევაში თუ სერვერიდან მივიღეთ რეგისტრაციის მოთხოვნაზე დასტური
        # ან თუ პროგრამა იხურება
        while self.registration_verified is False and self.application_is_closing is False:
            # თუ შეტყობინება არ გაგზავნილა რეგისტრაციის მოთხოვნისთვის
            if registration_message_sent is False:
                # რეგისტრაციის მოთხოვნის გაგზავნა
                registration_message_sent = self.send_registration_request_to_ies_monitoring_server()
                # რეგისტრაციის მოთხოვნის გაგზავნის მცდელობის დრო
                try_sent_registration_datetime = datetime.datetime.now()

                # ციკლი სერვერთან რეგისტრაციის შეტყობინების გასაგზავნად
                # ციკლიდან გამოვდივართ იმ შემთხვევაში თუ რეგისრაციის შეტყობინება გაიგზავნა
                # ან თუ პროგრამა იხურება
                while registration_message_sent is False and self.application_is_closing is False:
                    # შევამოწმოთ თუ სერვერთან რეგისტრაციის შეტყობინების გაგზავნის ცდიდან გავიდა test_ies_monitoring_server_connection_delay წამი
                    if (datetime.datetime.now() - try_sent_registration_datetime) > datetime.timedelta(seconds=test_ies_monitoring_server_connection_delay):
                        # რეგისტრაციის მოთხოვნის გაგზავნა
                        registration_message_sent = self.send_registration_request_to_ies_monitoring_server()

                        # რეგისტრაციის მოთხოვნის გაგზავნის მცდელობის დრო
                        try_sent_registration_datetime = datetime.datetime.now()
                    # დაყოვნება
                    time.sleep(delay)

                # რეგისტრაციის მოთხოვნის გაგზავნის დრო
                sent_registration_datetime = datetime.datetime.now()

            # შევამოწმოთ თუ სერვერთან რეგისტრაციის შეტყობინების გაგზავნიდან გავიდა test_ies_monitoring_server_connection_delay წამი
            if (datetime.datetime.now() - sent_registration_datetime) > datetime.timedelta(seconds=test_ies_monitoring_server_connection_delay):
                # შეტყობინება რეგისტრაციაზე არ გაგზავნილა
                registration_message_sent = False
            # დაყოვნება
            time.sleep(delay)

    def send_message_to_ies_monitoring_server(self, message):
        """ ფუნქციიის საშუალებით შეიძლება შეტყობინების გაგზავნა ies_monitoring_server-თან """

        # სოკეტის შექმნა
        ies_monitoring_server_connection = self.connect_ies_monitoring_server(verbose=False)

        # ies_monitor-თან დაკავშირება
        if ies_monitoring_server_connection is False:
            logger.warning("შეტყობინება ვერ გაიგზავნა, ies_monitoring_server-თან კავშირი ვერ დამყარდა\n{}"
                           .format(message))
            return

        try:
            # შეტყობინების გაგზავნა
            ies_monitoring_server_connection.send(self.dictionary_to_bytes(message))
            logger.debug("შეტყობინება გაიგზავნა ies_monitoring_server-თან\n{}"
                         .format(message))
        except Exception as ex:
            logger.warning("შეტყობინება ვერ გაიგზავნა ies_monitoring_server-თან\n{}\n{}"
                           .format(message, str(ex)))

        # სოკეტის დახურვა
        self.connection_close(ies_monitoring_server_connection, ies_monitoring_server_connection.getsockname())

    def testing_connection_to_ies_monitoring_server(self):  # ???
        """ ფუნქცია უგზავნის Hello პაკეტებს ies_monitoring_server -ს რითაც მოწმდება კავშირის არსებობა """

        # Hello პაკეტის შექმნა
        server_message = {
            "who_am_i": "ies_monitor",
            "message_category": "hello",
            "ip": ies_monitor_ip,
            "port": ies_monitor_port
        }

        # Hello პაკეტის გაგზავნა
        self.send_message_to_ies_monitoring_server(server_message)

        # შევინახოთ Hello პაკეტის გაგზავნის დრო
        sent_datetime = datetime.datetime.now()

        # პაკეტის გაგზავნის დროს ითვლება რომ კავშირი არ გვაქვს სერვერთან
        self.connection_state = TESTING

        # ციკლი რომელიც მუდმივად აგზავნის Hello პაკეტებს
        while True and self.application_is_closing is False:
            if (datetime.datetime.now() - sent_datetime) > datetime.timedelta(seconds=test_ies_monitoring_server_connection_delay):
                # Hello პაკეტის გაგზავნა
                self.send_message_to_ies_monitoring_server(server_message)

                # შევინახოთ Hello პაკეტის გაგზავნის დრო
                sent_datetime = datetime.datetime.now()

                # პაკეტის გაგზავნის დროს ითვლება რომ კავშირი არ გვაქვს სერვერთან
                self.connection_state = TESTING

            # ციკლი რომელიც ელოდება სერვერიდან Hello პაკეტის მიღებას
            while self.connection_state is TESTING:
                # ციკლის სტაბილური მუშაობისთვის
                time.sleep(delay)

                # შევამოწმოთ რა დრო გავიდა Hello პაკეტის გაგზავნის შემდეგ
                if (datetime.datetime.now() - sent_datetime) > datetime.timedelta(seconds=test_ies_monitoring_server_connection_delay * 2):
                    self.connection_state = DISCONNECTED
                    logger.warning("სერვერთან კავშირი გაწყდა")
                    self.register_to_ies_monitoring_server()
                    return

            # ციკლის სტაბილური მუშაობისთვის
            time.sleep(delay)

    def response_ies_monitoring_server(self, message, addr):
        """
            ფუნქცია განასხვავებს ies_monitoring_server -ისგან მიღებულ შეტყობინებებს
            1. თუ მოსულია registration_verified შეტყობინება მაშინ ies_monitoring_server -თან კავშირის სტატუსი ხდება "CONNECTED" და
               ეშვება testing_connection_to_ies_monitoring_server თრედი
            2. თუ მოსულია database_updated შეტყობინება ეს ნიშნავს, რომ ies_monitoring_server -ის მონაცემთა ბაზაში
               დაემატა ახალი შეტყობინება და შესაბამისად უნდა მოხდეს მონაცემების ხელახალი წამოღება
            3. თუ მოსულია hello პაკეტი მაშინ ies_monitoring_server -თან კავშირის სტატუსი ხდება "CONNECTED"
        """

        # შევამოწმოთ message dictionary-ის თუ აქვს message_category ინდექსი
        if "message_category" not in message:
            logger.warning("response_ies_monitoring_server ფუნქციას მიეწოდა message dictionary \
                            რომელსაც არ აქვს message_category key-ი")
            return

        # შევამოწმოთ მესიჯის კატეგორია
        if message["message_category"] == "registration_verified":
            logger.info("ies_monitor-ი წარმატებით დარეგისტრირდა ies_monitoring_server-ზე")
            self.registration_verified = True
            self.connection_state = CONNECTED

            # ეშვება თრედი რომელიც მუდმივად ამოწმებს სერვერთან კავშირს
            threading.Thread(target=self.testing_connection_to_ies_monitoring_server).start()

        elif message["message_category"] == "database_updated":
            logger.info("სერვერიდან მოვიდა შეტყობინება იმის შესახებ, რომ მის მონაცემთა ბაზაში დაემატა ახალი შეტყობინება")

            self.load_messages_from_mysql()

            # ვიძახებთ connect_to_sqlite ფუნქციას
            self.connect_to_sqlite()

            # ვიძახებთ check_opened_messages ფუნქციას
            self.check_opened_messages()

        elif message["message_category"] == "hello":
            self.connection_state = CONNECTED
            logger.debug("სერვერიდან მოვიდა hello შეტყობინება იმის დასტურად რომ სერვერი ხელმისაწვდომია")

    def server_message_handler_thread(self, connection, addr):
        """ ფუნქცია ამუშავებს მიღებულ შეტყობინებებს წასაკითხად და განასხვავებს გამომგზავნს """

        while True and self.application_is_closing is False:
            # დაყოვნება
            time.sleep(delay)

            # select.select ფუნქცია აბრუნებს readers list-ში ისეთ socket-ებს რომელშიც მოსულია წასაკითხი ინფორმაცია
            # ბოლო პარამეტრად მითითებული გვაქვს 0 რადგან ფუნქცია არ დაელოდოს ისეთ სოკეტს რომელზეც შეიძლება წაკითხვა
            readers, _, _, = select.select([connection], [], [], 0)

            # შევამოწმოთ readers list-ი თუ არ არის ცარიელი, რაც ამ შემთხვევაში ნიშნავს იმას რომ connection
            # socket-ზე მოსულია წასაკითხი ინფორმაცია
            if readers:
                # წავიკითხოთ client-სგან გამოგზავნილი შეტყობინება
                json_message = connection.recv(buffer_size)

                # იმ შემთხვევაში თუ კავშირი გაწყდა json_message იქნბა ცარიელი
                if not json_message.decode("utf-8"):
                    self.connection_close(connection, addr)
                    # ციკლიდან გამოსვლა. ამ შემთხვევაში თრედის დახურვა
                    break
                else:
                    # წაკითხული შეტყობინება bytes ობიექტიდან გადავიყვანოთ dictionary ობიექტში
                    message = self.bytes_to_dictionary(json_message)

                    # შევამოწმოთ თუ message dictionary-ის არ აქვს who_am_i key-ი
                    if "who_am_i" not in message:
                        logger.warning("მოსულია ისეთი შეტყობინება რომელსაც არ აქვს who_am_i key-ი")
                        # თუ არ გვაქვს who_am_i key-ი ესეიგი მოსულია საეჭვო მესიჯი და ვხურავთ თრედს
                        break

                    # შევამოწმოთ თუ შეტყობინება მოსულია ies_monitor.py - სგან
                    elif message["who_am_i"] == "ies_monitoring_server":
                        self.response_ies_monitoring_server(message, addr)
                        break

    def listening_to_ies_monitoring_server(self):
        """ ფუნქცია ხსნის პორტს და იწყებს მოსმენას """

        # ვუთითებთ სოკეტის პარამეტრებს
        self.listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # მოსმენის დაწყება
        self.listener_socket.bind((ies_monitor_ip, ies_monitor_port))

        # ვუთითებთ მაქსიმალურ კლიენტების რაოდენობას ვინც ელოდება კავშირის დამყარებაზე თანხმობას
        self.listener_socket.listen(10)

        logger.debug("ies_monitor-ი მზად არის შეტყობინების მისაღებად")

        while self.application_is_closing is False:
            try:
                # თუ client-ი მზად არის კავშირის დასამყარებლად დავეთანხმოთ
                connection, addr = self.listener_socket.accept()

                # გამოაქვს დაკავშირებული კლიენტის მისამართი
                logger.debug("შეტყობინების გამოსაგზავნად დაგვიკავშირდა: " + str(addr))

                # თითოეულ დაკავშირებულ client-ისთვის შევქმნათ და გავუშვათ
                # ცალკე thread-ი client_handler_thread ფუნქციის საშუალებით
                threading.Thread(target=self.server_message_handler_thread, args=(connection, addr)).start()
            except socket.error:
                break
            except Exception as ex:
                logger.error("შეცდომა listening_to_ies_monitoring_server Thread-ში:\n" + str(ex))
                break

    def send_registration_request_to_ies_monitoring_server(self):
        """ მიმდინარე ies_monitor-ის რეგისტრაცია ies_monitoring_server-ზე ხდება ip-ს და პორტის
            გაგზავნით. რეგისტრაციის მერე ies_monitoring_server-ი შეგვატყოვინებს ყველა ახალ
            შეტყობინებას """

        # ies_monitoring_server-თან დაკავშირება
        connection = self.connect_ies_monitoring_server(verbose=False)

        # შევამოწმოთ სერვერთან კავშირი თუ დამყარდა
        if connection is False:
            logger.warning("რეგისტრაციის პაკეტის გასაგზავნად სერვერთან კავშირი ვერ დამყარდა")
            return False

        logger.debug("სერვერთან კავშირი დამყარდა რეგისტრაციის პაკეტის გასაგზავნად")
        # სერვერთან გასაგზავნი შეტყობინება
        server_message = {
            "who_am_i": "ies_monitor",
            "message_category": "registration",
            "ip": ies_monitor_ip,
            "port": ies_monitor_port
        }

        try:
            # შეტყობინების გაგზავნა/რეგისტრაცია ies_monitoring_server-ზე
            connection.send(self.dictionary_to_bytes(server_message))
            logger.debug("სერვერზე გაიგზავნა რეგისტრაციის შეტყობინება")
        except Exception as ex:
            logger.error("შეცდომა ies_monitoring_server-ზე რეგისტრაციის დროს:\n" + str(ex))
            return False

        return True

    def check_opened_messages(self):
        """ ვამოწმებთ წაკითხული შეტყობინებების ბაზას და ვუცვლით ფერს
           შესაბამის შეტყობინებას, პროგრამის გახსნისას """

        self.select_message_id_sqlite()

        # ვამოწმებთ არის თუ არა შეტყობინების ID წაკითხული შეტყობინებების ბაზაში,
        # არსებობის შემთხვევაში შეტყობინებას ეცვლება ფონტი
        for row_index, row in enumerate(self.message_data):
            for col_index, col_name in enumerate(self.mysql_table_col_names):
                if row['message_id'] in self.get_id:
                    font = QtGui.QFont()
                    font.setBold(False)
                    self.message_table.item(row_index, col_index).setFont(font)

    def connect_to_sqlite(self):
        """ ფუნქცია უკავშირდება წაკითხული შეტყობინებების ბაზას (sqlite) """

        # უკავშირდება არსებულ sqlite ბაზას
        self.conn = sqlite3.connect('ies_monitor.db')

        # მონაცემების ლისტად წამოღება
        self.conn.row_factory = lambda cursor, rows: rows[0]

        self.sqlite_cursor = self.conn.cursor()

    def select_message_id_sqlite(self):
        """ ვკითხულობთ შეტყობინების ID -ს წაკითხული შეტყობინებების ბაზიდან  """

        self.sqlite_cursor.execute("SELECT message_id FROM opened_messages")
        self.get_id = self.sqlite_cursor.fetchall()

    def insert_to_sqlite(self):
        """ ვწერთ გახსნილი შეტყობინების ID -ს sqlite ბაზაში,
            შეტყობინების ID -ები არ იწერება ხელმეორედ """

        self.select_message_id_sqlite()
        if self.load_message['message_id'] in self.get_id:
            pass
        else:
            self.sqlite_cursor.execute(
                """INSERT INTO "opened_messages" ("message_id","status")
                   VALUES ('{}','{}')""".format(self.load_message['message_id'], 1)
            )
            self.conn.commit()

        # self.sqlite_cursor.close()  # ???
        # self.conn.close()

    def connect_to_mysql(self):
        """ ფუნქცია უკავშირდება Mysql სერვერს"""

        try:
            self.mysql_connection = pymysql.connect(
                mysql_server_ip,
                mysql_server_user,
                mysql_user_pass,
                mysql_database_name,
                port=mysql_server_port
            )
            logger.info("მონაცემთა ბაზასთან კავშირი დამყარებულია")
            self.cursor = self.mysql_connection.cursor(pymysql.cursors.DictCursor)
        except Exception as ex:
            logger.warning("მონაცემთა ბაზასთან კავშირი წარუმატებელია\n" + str(ex))
            return False
        return self.cursor

    def set_qtablewidget_style(self):
        """ ფუნქცია აყენებს QTableWidgets -ის დიზაინის პარამეტრებს """

        # self.message_table.setStyleSheet("QTableView {selection-background-color: #D98605;}")
        # self.message_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # self.message_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # სვეტების რაოდენობა
        self.message_table.setColumnCount(len(self.mysql_table_col_names))

        # ვანიჭებთ სვეტებს შესაბამის სახელებს
        self.message_table.setHorizontalHeaderLabels(self.mysql_table_col_readable_names)
        self.message_table.setColumnHidden(4, True)
        self.message_table.setColumnHidden(0, True)
        # self.message_table.horizontalHeader().setStretchLastSection(True)
        self.message_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.message_table.horizontalHeader().setSectionsMovable(True)

    def load_messages_from_mysql(self):
        """ mysql ბაზიდან კითხულობს შეტყობინებებს და სვავს message_table -ის შესაბამის სტრიქონში """

        query = "SELECT " + ", ".join(self.mysql_table_col_names) + " FROM messages"
        self.cursor.execute(query)
        self.message_data = self.cursor.fetchall()
        self.mysql_connection.commit()
        self.message_table.setRowCount(0)
        for row_index, row in enumerate(self.message_data):
            self.message_table.insertRow(row_index)
            for col_index, col_name in enumerate(self.mysql_table_col_names):
                self.message_table.setItem(row_index, col_index,
                                           QtWidgets.QTableWidgetItem(str(row[col_name])))

    def message_table_double_click(self):
        """
            ფუნქცია გამოიძახება სტრიქონზე მაუსის ორჯერ დაჭერისას.
            იძახებს dialog ფანჯარას და ავსებს მონიშნული შეტყობინების მონაცემებით,
            მონიშნული შეტყობინების ID -ს წერს წაკითხული შეტყობინებების ბაზაში (sqlite),
            უცვლის წაკითხულ შეტყობინებას ფერს.
        """

        dialog = QtWidgets.QDialog()
        self.ui = Ui_Dialog()
        self.ui.setupUi(dialog)
        selected_row_index = []
        for idx in self.message_table.selectedIndexes():
            selected_row_index.append(idx.row())

        for row_index, row in enumerate(self.message_data):
            if row_index == selected_row_index[0]:
                self.load_message = row

        self.load_message_data()

        self.connect_to_sqlite()

        self.insert_to_sqlite()

        self.select_message_id_sqlite()

        font = QtGui.QFont()
        font.setBold(False)
        if self.load_message['message_id'] in self.get_id:
            for col_index, col_name in enumerate(self.mysql_table_col_names):
                self.message_table.item(selected_row_index[0], col_index).setFont(font)

        dialog.show()
        dialog.exec_()

    def load_message_data(self):
        """ ფუნქცია ავსებს dialog ფანჯარას შეტყობინების მონაცემებით """

        self.ui.message_title.setText(self.load_message['message_title'])
        self.ui.message_id.setText(self.load_message['message_id'])
        self.ui.message_type.setText(self.load_message['message_type'])
        self.ui.client_ip.setText(self.load_message['client_ip'])
        self.ui.message_time.setText(str(self.load_message['sent_message_datetime']))
        self.ui.script_name.setText(self.load_message['client_script_name'])
        self.ui.text.setPlainText(self.load_message['text'])

    def closeEvent(self, event):
        """ ფუნქცია გამოიძახება პროგრამის დახურვის დროს """

        close = QtWidgets.QMessageBox.question(
            self,
            "QUIT",
            "Sure?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if close == QtWidgets.QMessageBox.Yes:
            self.application_is_closing = True
            self.connection_close(self.listener_socket)
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    os._exit(app.exec_())  # ???!!!!!!!!!!!
