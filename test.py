#!/usr/bin/python3

# import netifaces as ni

# print (ni.interfaces()[1])  # should print "192.168.100.37"
# ni.ifaddresses('enp3s0')

# ip = ni.ifaddresses('enp3s0')[ni.AF_INET][0]['addr']
# print(ip)

# a = "asdasdadassda"
# print(id(a))
# a = "56465464876"
# print(id(a))
# a = "asdasdadassda"
# print(id(a))


# d = 1
# d = 12

# "0000001"

# f_left("0", 10, d)



# x = 4
# y = 4
# w = 9999
# v = 9999
# a = 12345678
# b = 12345678
# print (hex(id(x)))
# print (hex(id(y)))
# print (hex(id(w)))
# print (hex(id(v)))
# print (hex(id(a)))
# print (hex(id(b)))




# def test(a, b):
#     print(a, b)



# def run(func_name, *args):
#     func_name(*args)



# def run(func_name, args = ()):
#     func_name(*args)




# run(func_name, (64, 48))
# run(func_name, 64, 48)


# def wait(category_name, time, func_name, args=())
    



# wait("registration_verified", 30, function, args = ())


# run(func_name = test, args = (3, 5))



# def foo(a, b, c, *args, **params):
#     print ("a = %s" % (a,))
#     print ("b = %s" % (b,))
#     print ("c = %s" % (c,))
#     print (args)
#     print (params)

# foo("testa", "excess", "testc", "testb", d="another_excess")





# def test(a, b):
#     print(a)
#     print(b)

# test(a = 3, 6)


# def foo(a, b, c, *args):
#     print ("a = %s" % (a,))
#     print ("b = %s" % (b,))
#     print ("c = %s" % (c,))
#     print (args)

# foo("testa", "testb", "testc", "excess", "another_excess")


import pymysql

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
mysql_table_col_names = [
            "message_id", "sent_message_datetime", "message_type",
            "message_title", "text", "client_ip", "client_script_name"
        ]

def connect_to_mysql():
    """ ფუნქცია უკავშირდება Mysql სერვერს"""

    try:
        mysql_connection = pymysql.connect(
            mysql_server_ip,
            mysql_server_user,
            mysql_user_pass,
            mysql_database_name,
            port=mysql_server_port
        )
        # logger.info("მონაცემთა ბაზასთან კავშირი დამყარებულია")
        cursor = mysql_connection.cursor(pymysql.cursors.DictCursor)
    except Exception as ex:
        # logger.warning("მონაცემთა ბაზასთან კავშირი წარუმატებელია\n" + str(ex))
        return False
    return cursor

connect_to_mysql()

def load_messages_from_mysql():
    """ mysql ბაზიდან კითხულობს შეტყობინებებს და სვავს message_table -ის შესაბამის სტრიქონში """

    cursor = connect_to_mysql()

    query = "SELECT " + ", ".join(mysql_table_col_names) + " FROM messages"
    cursor.execute(query)
    message_data = cursor.fetchall()
    print(message_data)

load_messages_from_mysql()