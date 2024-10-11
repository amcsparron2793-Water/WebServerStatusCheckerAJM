import datetime


# noinspection PyUnresolvedReferences
class DownTimeCalculation:
    def __init__(self):
        self._length_of_time_down = datetime.timedelta()
        self._down_timestamp: datetime.datetime or None = None

    @property
    def down_timestamp(self):
        """
        Property method to get the timestamp when the instance was last marked as down.
        It sets the timestamp when the instance is down and the timestamp is not already set.
        If the instance is not marked as down, it sets the timestamp value to None.

        Returns the last down timestamp value.
        """
        if self.is_down and not self._down_timestamp:
            self._down_timestamp = datetime.datetime.now().timestamp()
        elif not self.is_down:
            self._down_timestamp = None
        return self._down_timestamp

    @property
    def length_of_time_down(self) -> datetime.timedelta:
        """
        Return the length of time the system has been down. If the system is currently not down, returns None.
        Calculated by subtracting the down timestamp from the current timestamp.
        """
        if not self.is_down:
            pass
        else:
            self._length_of_time_down = (datetime.timedelta(seconds=datetime.datetime.now().timestamp())
                                         - datetime.timedelta(seconds=self.down_timestamp))
        return self._length_of_time_down
