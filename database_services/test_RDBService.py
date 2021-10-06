import database_services.RDBService as db_service

def test_insert():
    try:
        db_service.insert_new_record("Stonk","User",
            {
                "userID": 'DEFAULT',
                "email": "teset2ss33@gg.com",
                "pwHash": "sdgbfsgbdf",
                "nameLast": "Leo233",
                "nameFirst": "FASD",
                "addressID": "DEFAULT"
            }
        )
    except Exception as e:
        print("exception raised: ", e)

def test_update_record_with_keys():
    db_service.update_record_with_keys("Stonk", "User",
                                              {"userID": "2"},
                                              {"nameFirst": "mrUpdated", "nameLast": "updatedlastName"}
    )

def test_get_by_key():
    r = db_service.get_by_template("Stonk", "User",
                                   {"userID": "4"},
                                   ["nameFirst", "nameLast"]
                                   )
    print(r)

    r = db_service.get_by_template("Stonk", "User",
                                   {"userID": "4"},
                                   None
                                   )
    print(r)

#test_insert();
#test_update_record_with_keys()
#test_get_by_key()


