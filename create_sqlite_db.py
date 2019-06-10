#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3

conn = sqlite3.connect('ies_monitor.db')
c = conn.cursor()
c.execute("""CREATE TABLE 'opened_messages' (
          'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
          'message_id' TEXT DEFAULT NULL,
          'status' INTEGER NOT NULL DEFAULT 0
          )""")
# c.execute("""DROP TABLE 'opened_messages'""")
conn.commit()
conn.close()
