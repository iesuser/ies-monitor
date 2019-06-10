#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import pymysql
import sqlite3

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from message_dialog import Ui_Dialog

# class MessageDialog(object):
#     def __init__(self):
#         super(MessageDialog, self).__init__()
#         uic.loadUi('message_dialog.ui', self)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        uic.loadUi('main_window.ui', self)

        self.message_table.doubleClicked.connect(self.row_double_clicked)

        self.mysql_server_ip = "localhost"

        self.mysql_server_user = "root"

        self.mysql_user_pass = "teqnikuri123"

        self.mysql_database_name = "ies_monitoring_server"

        self.mysql_server_port = 3306

        self.mysql_table_col_names = ["message_id", "sent_message_datetime", "message_type", "message_title", "text", "client_ip", "client_script_name"]

        self.mysql_table_col_readable_names = ["ID", "Time", "Message Type", "Message Title", "Message", "Client IP", "Script Name"]

        self.set_qtablewidget_style()

        self.connect_to_mysql()

        self.get_message_data()

        self.connect_to_sqlite()

        self.check_opened_messages()

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
        return self.get_id

    def insert_to_sqlite(self):
        """ ვწერთ გახსნილი შეტყობინების ID -ს sqlite ბაზაში,
            შეტყობინების ID -ები არ იწერება ხელმეორედ """

        self.select_message_id_sqlite()
        if self.load_message['message_id'] in self.get_id:
            pass
        else:
            print(self.load_message['message_id'])
            self.sqlite_cursor.execute("""INSERT INTO "opened_messages" ("message_id","status") VALUES ('{}','{}')
                           """.format(self.load_message['message_id'], 1))
            self.conn.commit()

        # self.sqlite_cursor.close()
        # self.conn.close()

    def connect_to_mysql(self):
        """ ფუნქცია უკავშირდება Mysql სერვერს"""

        try:
            mysql_connection = pymysql.connect(self.mysql_server_ip,
                                               self.mysql_server_user,
                                               self.mysql_user_pass,
                                               self.mysql_database_name,
                                               port=self.mysql_server_port)
            print("მონაცემთა ბაზასთან კავშირი დამყარებულია")
            self.cursor = mysql_connection.cursor(pymysql.cursors.DictCursor)
        except Exception as ex:
            print("მონაცემთა ბაზასთან კავშირი წარუმატებელია\n" + str(ex))
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

    def get_message_data(self):
        """ mysql ბაზიდან კითხულობს შეტყობინებებს და სვავს message_table -ის შესაბამის სტრიქონში """

        # წაკითხული შეტყობინებები
        # global message_data

        query = "SELECT " + ", ".join(self.mysql_table_col_names) + " FROM messages LIMIT 30"
        self.cursor.execute(query)
        self.message_data = self.cursor.fetchall()
        self.message_table.setRowCount(0)
        for row_index, row in enumerate(self.message_data):
            self.message_table.insertRow(row_index)
            for col_index, col_name in enumerate(self.mysql_table_col_names):
                self.message_table.setItem(row_index, col_index, QtWidgets.QTableWidgetItem(str(row[col_name])))

    def row_double_clicked(self):
        """ ფუნქცია გამოიძახება სტრიქონზე მაუსის ორჯერ დაჭერისას.
            იძახებს dialog ფანჯარას და ავსებს მონიშნული შეტყობინების მონაცემებით,
            მონიშნული შეტყობინების ID -ს წერს წაკითხული შეტყობინებების ბაზაში (sqlite),
            უცვლის წაკითხულ შეტყობინებას ფერს.
        """

        Dialog = QtWidgets.QDialog()
        self.ui = Ui_Dialog()
        self.ui.setupUi(Dialog)
        selected_row_index = []
        for idx in self.message_table.selectedIndexes():
            selected_row_index.append(idx.row())

        for row_index, row in enumerate(self.message_data):
            if row_index == selected_row_index[0]:
                self.load_message = row
        self.load_message_data()
        self.insert_to_sqlite()
        self.select_message_id_sqlite()
        font = QtGui.QFont()
        font.setBold(False)
        if self.load_message['message_id'] in self.get_id:
            for col_index, col_name in enumerate(self.mysql_table_col_names):
                self.message_table.item(selected_row_index[0], col_index).setFont(font)

        Dialog.show()
        Dialog.exec_()

    def load_message_data(self):
        """ ფუნქცია ავსებს dialog ფანჯარას შეტყობინების მონაცემებით """

        self.ui.message_title.setText(self.load_message['message_title'])
        self.ui.message_id.setText(self.load_message['message_id'])
        self.ui.message_type.setText(self.load_message['message_type'])
        self.ui.client_ip.setText(self.load_message['client_ip'])
        self.ui.message_time.setText(str(self.load_message['sent_message_datetime']))
        self.ui.script_name.setText(self.load_message['client_script_name'])
        self.ui.text.setPlainText(self.load_message['text'])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
