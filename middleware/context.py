import json
import os

# This is a bad place for this import
import pymysql


def get_db_info():
    """
    This is crappy code.

    :return: A dictionary with connect info for MySQL
    """
    db_host = None
    db_user = None
    db_password = None

    with open('../config/db_config.json', ) as f:
        data = json.load(f)
        db_host = data['DBHOST']
        db_user = data['DBUSER']
        db_password = data['DBPASSWORD']

    """
    db_host = os.environ.get("DBHOST", None)
    db_user = os.environ.get("DBUSER", None)
    db_password = os.environ.get("DBPASSWORD", None)
    """

    #Debug info
    print("get_db_info(), ",
          "db_host: ", db_host,
          ", db_user: ", db_user,
          ", db_password: ", "****** (censored, source code mod req) ",
          #"db_password: ", db_password
          )

    if db_host is not None:
        db_info = {
            "host": db_host,
            "user": db_user,
            "password": db_password,
            "cursorclass": pymysql.cursors.DictCursor
        }
    else:
        db_info = {
            "host": "localhost",
            "user": "dbuser",
            "password": "dbuserdbuser",
            "cursorclass": pymysql.cursors.DictCursor
        }

    return db_info

#get_db_info()