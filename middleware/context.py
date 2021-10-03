import json
import os
import logging

# This is a bad place for this import
import pymysql
import config.db_config as config


# region logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# endregion

def get_db_info():
    """
    This is crappy code.

    :return: A dictionary with connect info for MySQL
    """

    db_host = config.db_connect_info['DBHOST']
    db_user = config.db_connect_info['DBUSER']
    db_password = config.db_connect_info['DBPASSWORD']

    """
    db_host = os.environ.get("DBHOST", None)
    db_user = os.environ.get("DBUSER", None)
    db_password = os.environ.get("DBPASSWORD", None)
    """

    #Debug info
    logger.debug("get_db_info(), " +
          "db_host: " + db_host+
          ", db_user: "+ db_user+
          ", db_password: "+ "****** (censored, source code mod req) "
          #"db_password: "+ db_password
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

get_db_info()