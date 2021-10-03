import pymysql
import json
import logging
import database_services.RDBService as d_service
import secrets
import datetime

# region logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# endregion

LOG_PREFIX = "USER_SERVICE_DB_OPT: "

# region Adding User
Duplicate_Entry_ErrorCode = 1062
class email_already_exist(Exception):
    pass
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

    user_PK = None
    # Try to add user to DB
    try:
        user_PK = d_service.insert_new_record("Stonk","User",
            {
                "userID": 'DEFAULT',
                "email": reg_info['email'],
                "pwHash": reg_info['password_hash'],
                "nameLast": reg_info['name_last'],
                "nameFirst": reg_info['name_first'],
                "addressID": "NULL"
            },
            True
        )
    except pymysql.Error as e:
        print(LOG_PREFIX, "SQL exception: ", e)
        if e.args[0] == Duplicate_Entry_ErrorCode:
            print(LOG_PREFIX,"Duplicate entry (probably email)")
            raise email_already_exist("email_already_exist")
            return None

    print(LOG_PREFIX,"New User Added Success, UserPK: ", user_PK)
    #New user add success

    address_pk = d_service.insert_new_record("Stonk", "Address",
                                {
                                    "addressID": 'DEFAULT',
                                    "countryCode": reg_info['address_country_code'],
                                    "zipCode": reg_info['address_zip_code'],
                                    "state": reg_info['address_state'],
                                    "city": reg_info['address_city'],
                                    "firstLine": reg_info['address_first_line'],
                                    "secondLine": reg_info['address_second_line']
                                },
                                True
    )
    print(LOG_PREFIX,"Address PK: ", address_pk)
    #Update user address
    d_service.update_record_with_keys("Stonk", "User",
          {
              "userID" : str(user_PK)
          },
          {
            "addressID": str(address_pk)
          }
    )

    print(LOG_PREFIX, "User Address Link Success")
    print(LOG_PREFIX, "Returning User Record")
    user_record = d_service.get_by_key("Stonk", "User", {"userID": str(user_PK)})

    token = refresh_token(str(user_PK))

    return user_record[0], token

#endregion

class incorrect_password(Exception):
    pass
class email_not_found(Exception):
    pass

def validate_existing_user(email, password_hash):
    r = d_service.get_by_key("Stonk", "User",{"email": email})

    if(len(r) == 0):
        raise email_not_found("email_not_found")
        return

    if(r[0]['pwHash'] != password_hash):
        raise incorrect_password("incorrect_password")
        return

    print(LOG_PREFIX, "validate_existing_user PASS!")
    user_table_record = r[0]
    token = refresh_token(str(r[0]['userID']));

    return user_table_record, token;

def generate_new_token():
    return  secrets.token_urlsafe(64)

def refresh_token(user_id, exp_time_in_seconds = 7200):
    print(LOG_PREFIX, "Refreshing token for: ", user_id)
    r = d_service.get_by_key("Stonk", "Token", {"userID": user_id})
    new_token = generate_new_token()

    exp_date_time = datetime.datetime.now() + datetime.timedelta(seconds=exp_time_in_seconds)
    exp_date_time_str = exp_date_time.strftime('%Y-%m-%d %H:%M:%S')
    #print(exp_date_time_str)

    if len(r) == 0:
       print(LOG_PREFIX, "No token record found, creating a new one")
       d_service.insert_new_record("Stonk", "Token",
          {
              "userID": user_id,
              "token": new_token,
              "expireDateTime" : exp_date_time_str
          }
      )
    else:
        print(LOG_PREFIX, "Token record found, Updating token")
        d_service.update_record_with_keys("Stonk", "Token",
            {"userID": user_id},
            {"token": new_token, "expireDateTime" : exp_date_time_str}
        )

    print(LOG_PREFIX, "new token: ", new_token , "expDateTime: ", exp_date_time_str)
    return new_token

