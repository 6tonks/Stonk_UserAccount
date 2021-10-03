import database_services.RDBService as db_service

try:
    db_service.add_new_user(
        {
            "email": "teset@gg.com",
            "password_hash": "sdgbfsgbdf",
            "name_last": "Leo",
            "name_first": "FASD",
            "address_first_line": "ASDW",
            "address_second_line": "ASD",
            "address_city": "ASD",
            "address_state": "ASD",
            "address_zip_code": "ASD",
            "address_country_code": "ASD"
        }
    )
except db_service.email_already_exist as e:
    print("exception raised: ",e)
