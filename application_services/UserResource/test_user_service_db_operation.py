import user_service_db_operation as user_service_db
import string
import random
import logging

# For setting logging level
logging.basicConfig(level=logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)

# region utilities
def rnd_str_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
#endregion

def test_add_new_user_sucess():
    try:
        user_record,token = user_service_db.add_new_user(
            {
                "email": rnd_str_generator() + "@columbia.edu",
                "password_hash": "kasf12jlaj32fdl5sjearlkfa123",
                "name_last": "Freeman",
                "name_first": "Leo",
                "address_first_line": "AddressFirstLine",
                "address_second_line": "AddresSecondLine",
                "address_city": "NewYork",
                "address_state": "NY",
                "address_zip_code": "10027",
                "address_country_code": "US"
            }
        )
        print("test_add_new_user_sucess() SUCCESS")
        print("new user record:", user_record)
        print("user token:", token)
    except user_service_db.email_already_exist as e:
        print("---> handle email_already_exist exception here: ", e, " <---")


def test_add_new_user_fail_duplicated_email():
    try:
        user_record, token = user_service_db.add_new_user(
            {
                "email" : "IWillDuplicate@columbia.edu.tw",
                "password_hash" : "kasf12jlaj32fdl5sjearlkfa123",
                "name_last" : "Freeman",
                "name_first" : "Leo",
                "address_first_line" : "AddressFirstLine",
                "address_second_line"  : "AddresSecondLine",
                "address_city" : "NewYork",
                "address_state" : "NY",
                "address_zip_code" : "10027",
                "address_country_code" : "US"
            }
        )
        print(user_record, token)
    except user_service_db.email_already_exist as e:
        print("---> handle email_already_exist exception here: ", e," <---")

def test_validate_existing_user_success():
    try:
        user_table_record, token = user_service_db.validate_existing_user("xvzs22vdf@gmail.com","ZXCASDAW")
        print("test_validate_existing_user_success() SUCCESS")
        print("user_table_record: ", user_table_record)
        print("token: ", token)

    except user_service_db.email_not_found as e:
        print("---> handle email_not_found exception here: ", e, " <---")
    except user_service_db.incorrect_password as e:
        print("---> handle incorrect_password exception here: ", e," <---")

def test_validate_existing_user_fail():
    try:
        user_table_record, token = user_service_db.validate_existing_user("xvzs22vdf@gmail.com","Wrong_PW_Hash")
        print("user_table_record: ", user_table_record)
        print("token: ", token)

    except user_service_db.email_not_found as e:
        print("---> handle email_not_found exception here: ", e, " <---")
    except user_service_db.incorrect_password as e:
        print("---> handle incorrect_password exception here: ", e," <---")

print("------------------test_add_new_user_sucess()--------------")
test_add_new_user_sucess()
print("------------------test_add_new_user_duplicated_email()--------------")
test_add_new_user_fail_duplicated_email()

print("------------------test_validate_existing_user_success()--------------")
test_validate_existing_user_success()
print("------------------test_validate_existing_user_fail()--------------")
test_validate_existing_user_fail()