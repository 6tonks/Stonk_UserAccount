from enum import Enum

class SNS_TOPICS(Enum):
    USER_ACTIVITY = "user_activity"

    @property
    def str(self):
        return self.value

ENABLE_USER_ACTIVITY = True
SNS_ARNS = {
    SNS_TOPICS.USER_ACTIVITY: 'arn:aws:sns:us-east-1:113471254581:user_activity'
}