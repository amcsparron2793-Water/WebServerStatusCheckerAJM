"""
WebServerStatusCheckerAJM.py

Pings a machine to see if it is up, then checks for the presence of a given http server
 (originally conceived for use with Django and Apache).

"""
import datetime

from time import sleep
import platform
import subprocess

from typing import List, Dict
from os.path import isdir

import ctypes
import winsound
try:
    from WebServerStatusCheckerAJM._version import __version__
    from WebServerStatusCheckerAJM.ServerAddressPort import ServerAddressPort
    from WebServerStatusCheckerAJM.ComponentStatus import ComponentStatus
    from WebServerStatusCheckerAJM.TitlesNames import TitlesNames
except (ModuleNotFoundError, ImportError):
    from _version import __version__
    from ServerAddressPort import ServerAddressPort
    from ComponentStatus import ComponentStatus
    from TitlesNames import TitlesNames
from EasyLoggerAJM import EasyLogger


class WebServerEasyLogger(EasyLogger):
    @classmethod
    def smart_default_log_location(cls):
        if isdir('../Misc_Project_Files'):
            ...
        raise NotImplementedError("not implemented yet.")


class WebServerStatusCheck(ServerAddressPort, ComponentStatus, TitlesNames):
    """
    This class is responsible for checking the status of a web server.
    It can ping a server to check if it is up and running.
    The class initializes with server details and settings.
    It provides methods to display status, log status,
    and show message boxes if errors occur.
    The class also contains utility functions to handle
    server status checks and time calculations.
    The main loop continuously checks and logs the server status.
    """
    LOGGER = EasyLogger.UseLogger().logger
    WINAPI_MSG_BOX_STYLES = {
        'OK': 0,
        'OK_Cancel': 1,
        'Abort_Retry _Ignore': 2,
        'Yes_No_Cancel': 3,
        'Yes_No': 4,
        'Retry_Cancel': 5,
        'Cancel_Try Again_Continue': 6,
        'Above_All_OK': 0x1000,
        'Error_Above_All_OK': 0x00000010}
    INITIALIZATION_STRING = f'Initializing server status checker v{__version__}...'

    def __init__(self, server_web_address: str, server_ports: List[int] = None, server_titles: Dict[int, str] = None,
                 use_friendly_server_names: bool = True, server_web_page: str or None = None, silent_run: bool = False,
                 use_msg_box_on_error: bool = True, **kwargs):

        super().__init__()
        self.init_msg: bool = kwargs.get('init_msg', True)
        self._silent_run = silent_run

        self.use_msg_box_on_error = use_msg_box_on_error

        if not self.silent_run and self.init_msg:
            print(self.INITIALIZATION_STRING)

        self._initialize_property_vars()

        self._server_ports = server_ports
        self._server_titles = server_titles
        self._use_friendly_server_names = use_friendly_server_names
        self._active_server_port = self.server_ports[0]

        self._server_web_address = server_web_address
        self._server_web_page = server_web_page

    def _initialize_property_vars(self):
        self._is_down = False
        self._length_of_time_down = datetime.timedelta()
        self._down_timestamp: datetime.datetime or None = None

        self._machine_status = None
        self._local_machine_ping_host = '8.8.8.8'
        self._local_machine_status = None
        self._print_status = True

        self._html_title = None
        self._page_name = None
        self._current_server_name = None
        self._server_full_address = None
        self._just_started = True
        self._server_status = None
        self._page_status = None
        self._full_status_string = None
        self._server_status_string = None
        self._page_status_string = None

    @property
    def silent_run(self):
        """
        @property
        Represents a boolean flag indicating whether the software should run silently
         without displaying any output or not. By accessing this property, the value of the
         _silent_run attribute is retrieved. This property is read-only and cannot be modified directly.
        """
        return self._silent_run

    @property
    def print_status(self):
        """
        Getter method for the "print_status" property.
        Returns the value of the "_print_status" attribute if silent_run is False, otherwise returns False.
        """
        if self.silent_run:
            self._print_status = False
        else:
            pass
        return self._print_status

    @print_status.setter
    def print_status(self, value):
        """
        Setter method for updating the print_status attribute of an object.
        This property allows control over whether the object should print its status or not.
        """
        self._print_status = value

    @property
    def just_started(self):
        """
        @property
        Get the value of the just_started property.
        This property indicates whether the software has just started or not.
        """
        return self._just_started

    @just_started.setter
    def just_started(self, value: bool):
        """
        Set the value of the boolean attribute '_just_started' to the provided value.
        """
        self._just_started = value

    @property
    def full_status_string(self):
        """
        This method returns a formatted system status string containing current date and time, active server port, machine status, server name, server status, page name, and page status. If the server is down, it also handles displaying an error message using the specified styles. It ensures that down_timestamp is set when the page goes down.
        """
        # this was made a variable purely to make the full_status_string declaration more readable.
        cur_datetime = datetime.datetime.now().ctime()
        self._full_status_string = (f"\t{cur_datetime}: System Status on port {self.active_server_port} is:"
                                    f"\n\t\tLocal machine is: {self.get_status_string(self.local_machine_status)}"
                                    f"\n\t\tMachine is: {self.get_status_string(self.machine_status)}"
                                    f"\n\t\tServer: \'{self.current_server_name}\' on "
                                    f"\n\t\tPort: {self.active_server_port} is "
                                    f"{self.get_status_string(self.server_status)}. "
                                    f"\n\t\tPage: \'{self.server_web_page or self.page_name}\' is "
                                    f"{self.get_status_string(self.page_status)}")
        if self.is_down:
            if self.use_msg_box_on_error:
                try:
                    self.show_message_box("PART OR ALL OF SERVER DOWN",
                                          self._full_status_string.replace('\t', ''),
                                          self.WINAPI_MSG_BOX_STYLES['Error_Above_All_OK'])

                except Exception as e:
                    self.LOGGER.warning(f"could not show msgbox due to - {e}")
                    print(f"could not show msgbox due to - {e}")

            # this is here purely to make sure down_timestamp is set when the page goes down.
            x = self.down_timestamp
            del x

        return self._full_status_string

    @property
    def is_down(self):
        """
        This is a property method that checks the status of multiple components (local_machine_status, machine_status,
        server_status, page_status) to determine if the overall status is down.
        It returns a boolean value indicating whether the components are in a down state.
        """
        if not self.local_machine_status or not self.machine_status or not self.server_status or not self.page_status:
            self._is_down = True
        else:
            self._is_down = False
        return self._is_down

    # TODO: DownTimeCalculation class?
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

    def show_message_box(self, title: str, text: str, style: int):
        """
        Displays a message box with the given title and text using the specified style.
         If the provided style is not valid, it falls back to a default style ('Error_Above_All_OK').
         If the style is still invalid, a warning message is logged and the default Windows message box is displayed.
         Finally, an error sound is played using MessageBeep if the 'MB_ICONHAND' style is encountered.
         The function returns the result of the MessageBoxW call from the user32 library.
        """
        if style not in self.WINAPI_MSG_BOX_STYLES.values():
            try:
                style = self.WINAPI_MSG_BOX_STYLES['Error_Above_All_OK']
            except KeyError as e:
                print(f'Key Error: {e} is not a valid key for winapi_msg_box_styles')
                self.LOGGER.warning(f'Key Error: {e} is not a valid key for winapi_msg_box_styles')
                style = None
            try:
                if not style:
                    raise AttributeError("Given style is not valid and default failed!"
                                         " Windows default message box will be displayed.")
            except AttributeError as e:
                print("Given style is not valid and default failed!"
                      " Windows default message box will be displayed.")
                self.LOGGER.warning(e)
        try:
            winsound.MessageBeep(winsound.MB_ICONHAND)
        except Exception as e:
            self.LOGGER.error(e, exc_info=True)
        # 0 == no parent window
        return ctypes.windll.user32.MessageBoxW(0, text, title, style)

    def log_status(self) -> None:
        """
        Logs the status based on the server status and page status. If the server status is true and
        the page status is true, it logs the full status string at info level. If the server status is true but
        the page status is false, it logs the full status string at warning level. If the server status is false,
        it logs the full status string at critical level.
        """
        if self.server_status:
            if self.page_status:
                self.LOGGER.info(self.full_status_string)
            else:
                self.LOGGER.warning(self.full_status_string)
        else:
            self.LOGGER.critical(self.full_status_string)

    @staticmethod
    def get_status_string(status_bool: bool) -> str:
        """
        Converts a boolean status into a string representation.
        Returns "UP" if the status is True, and "DOWN" if the status is False.
        """
        if status_bool:
            return "UP"
        else:
            return "DOWN"

    def ping(self, **kwargs) -> bool:
        """
        Ping the specified host to check for connectivity.
        Returns True if the ping was successful, otherwise returns False.
        """
        host = None
        if kwargs:
            if 'host' in kwargs:
                host = kwargs['host']
        # Option for the number of packets as a function of
        param = '-n' if platform.system().lower() == 'windows' else '-c'

        # Building the command. Ex: "ping -c 1 google.com"
        if not host:
            command = ['ping', param, '1', self.server_web_address.split('/')[2]]
        else:
            command = ['ping', param, '1', host]

        # this pings the target while also hiding the output
        ping_result = subprocess.call(command, stdout=subprocess.DEVNULL) == 0
        return ping_result

    def MainLoop(self, sleep_time: int = 120):
        """
        MainLoop method runs an infinite loop that periodically checks the status of server ports.
        It first sets up necessary variables and prints messages if required. It then iterates through all server ports,
         updating the active server port and printing the full status string. The method logs the status after each
         iteration and sleeps for the specified time interval. If a KeyboardInterrupt is caught,
         it prints a termination message and exits. Any other exceptions are logged as errors and re-raised.
        """
        sleep(1)
        try:
            while True:
                subprocess.call(['cls'], shell=True)
                if self.just_started:
                    self.just_started = False
                    if not self.silent_run:
                        print("Checking for initial server availability.\n")
                for x in self.server_ports:
                    self.active_server_port = x
                    if not self.silent_run and self.print_status:
                        print(self.full_status_string)
                    self.log_status()
                sleep(sleep_time)
        except KeyboardInterrupt as e:
            print("CTRL-C detected, quitting...")
            sleep(1)
            exit(-1)
        except Exception as e:
            self.LOGGER.error(e, exc_info=True)
            raise e


if __name__ == '__main__':
    sp = [8100]
    print(f'ports are set to {sp}')
    WSSC = WebServerStatusCheck('http://10.56.211.116', server_ports=sp)
    WSSC.MainLoop()
