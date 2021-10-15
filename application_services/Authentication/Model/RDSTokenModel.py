import secrets
import datetime

from application_services.Authentication.Model.BaseTokenModel import BaseTokenModel
import database_services.RDBService as d_service

# or just name it TokenModel?
class RDSTokenModel(BaseTokenModel):


    @classmethod
    def create(cls, id):
        return cls.refresh_token(cls, str(id))

    def generate_new_token(self):
        return secrets.token_urlsafe(64)

    def refresh_token(self,user_id, exp_time_in_seconds=7200):
        LOG_PREFIX = "RDSTokenModel"
        print(LOG_PREFIX, "Refreshing token for: ", user_id)
        r = d_service.get_by_template("Stonk", "Token", {"userID": user_id})
        new_token = self.generate_new_token(self)

        exp_date_time = datetime.datetime.now() + datetime.timedelta(seconds=exp_time_in_seconds)
        exp_date_time_str = exp_date_time.strftime('%Y-%m-%d %H:%M:%S')
        # print(exp_date_time_str)

        if len(r) == 0:
            print(LOG_PREFIX, "No token record found, creating a new one")
            d_service.insert_new_record("Stonk", "Token",
                                        {
                                            "userID": user_id,
                                            "token": new_token,
                                            "expireDateTime": exp_date_time_str
                                        }
                                        )
        else:
            print(LOG_PREFIX, "Token record found, Updating token")
            d_service.update_record_with_keys("Stonk", "Token",
                                              {"userID": user_id},
                                              {"token": new_token, "expireDateTime": exp_date_time_str}
                                              )

        print(LOG_PREFIX, "new token: ", new_token, "expDateTime: ", exp_date_time_str)
        return new_token

    @classmethod
    def validate(cls, token, user_id):
        rec = d_service.get_by_template("Stonk", "Token", 
        {
            "userID": user_id, 
            'token': token
        })

        print("validate: ", rec)
        return rec is not None and list(rec) != []

    @classmethod
    def delete(cls, token):
        d_service.remove_old_record("Stonk", "Token", "token", token)
        return d_service.get_by_template("Stonk", "Token", {"token": token})