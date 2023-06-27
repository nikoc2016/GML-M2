from datetime import datetime


class GML_Datetime:
    DT_FORMAT = '%Y-%m-%d_%H:%M:%S'

    @staticmethod
    def now():
        return datetime.now()

    @staticmethod
    def datetime_to_str(target_datetime):
        return target_datetime.strftime(GML_Datetime.DT_FORMAT)

    @staticmethod
    def str_to_datetime(target_datetime_str):
        return datetime.strptime(target_datetime_str, GML_Datetime.DT_FORMAT)

    @staticmethod
    def if_datetime_expired(target_datetime, expiration_seconds):
        now_datetime = GML_Datetime.now()
        if now_datetime < target_datetime or (now_datetime - target_datetime).seconds < expiration_seconds:
            return True
        return False
