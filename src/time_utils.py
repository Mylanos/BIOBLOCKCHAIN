from datetime import datetime


class TimeUtils:
    """
     TimeUtils contains static methods for time operations
    """
    @staticmethod
    def my_date():
        """
        my_date returns current date in given format

        Returns:
            _type_: _description_
        """
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
