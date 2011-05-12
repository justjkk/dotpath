import psycopg2

def connect_to_DB(connection_settings):
    connstr = "host=" + connection_settings["host"] + " "
    if connection_settings["port"] != "":
        connstr += "port=" + connection_settings["port"] + " "
    connstr += "dbname=" + connection_settings["dbname"] + " "
    connstr += "user=" + connection_settings["user"] + " "
    connstr += "password=" + connection_settings["password"]

    conn = psycopg2.connect(connstr)
    conn.set_isolation_level(0)
    return conn

