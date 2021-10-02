import pymysql
import json
import logging
import middleware.context as context

# region logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# endregion

# region DB name
DB_SCHEMA = "Stonk"
DB_USER_TABLE = "User"
# region

def _get_db_connection():
    db_connect_info = context.get_db_info()

    logger.info("RDBService._get_db_connection:")
    logger.info("\t HOST = " + db_connect_info['host'])

    db_info = context.get_db_info()
    db_connection = pymysql.connect(
        **db_info
    )
    return db_connection


def generate_new_token(user_id):
    return None

Duplicate_Entry_ErrorCode = 1062
def add_new_user(reg_info):
    """Add a new user to the DB

           :param dict reg_info: dictionary contained all info need to reg, which are:
            email
            password_hash
            name_last
            name_first
            address_first_line
            address_second_line
            address_city
            address_state
            address_zip_code
            address_country_code
   """

    conn = _get_db_connection()
    cur = conn.cursor()

    sql = "INSERT INTO " + DB_SCHEMA +"."+ DB_USER_TABLE + " (userID, pwHash, nameLast, nameFirst, email, addressID) " \
          "VALUES ('DEFAULT', 'ASDASWQWE', 'Skagen', 'Stavang', 'test233@gmail.com', '987');"
    print("SQL Statement = " + cur.mogrify(sql, None))
    try:
        res = cur.execute(sql)
        #res = cur.fetchall()
        conn.commit()
        print(res)
    except pymysql.Error as e:
        print("SQL exception: ", e)
        if e.args[0] == Duplicate_Entry_ErrorCode:
            print("Duplicate entry (probably email)")
            pass

    finally:
        conn.close()

    return False
