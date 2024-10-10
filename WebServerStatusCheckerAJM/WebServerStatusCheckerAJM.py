"""
WebServerStatusCheckerAJM.py

Pings a machine to see if it is up, then checks for the presence of a given http server
 (originally conceived for use with Django and Apache).

"""
import datetime

import requests
from time import sleep
import platform
import subprocess

from typing import List, Dict
from EasyLoggerAJM import EasyLogger
from os.path import isdir

import ctypes
import winsound
from WebServerStatusCheckerAJM._version import __version__
from WebServerStatusCheckerAJM.ServerAddressPort import ServerAddressPort
from WebServerStatusCheckerAJM.ComponentStatus import ComponentStatus


class WebServerEasyLogger(EasyLogger):
    @classmethod
    def smart_default_log_location(cls):
        if isdir('../Misc_Project_Files'):
            ...
        raise NotImplementedError("not implemented yet.")


class WebServerStatusCheck(ServerAddressPort, ComponentStatus):
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

    def show_message_box(self, title: str, text: str, style: int):
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

    @property
    def silent_run(self):
        return self._silent_run

    @property
    def print_status(self):
        return self._print_status

    @print_status.getter
    def print_status(self):
        if self.silent_run:
            self._print_status = False
        else:
            pass
        return self._print_status

    @print_status.setter
    def print_status(self, value):
        self._print_status = value

    @property
    def page_name(self):
        return self._page_name

    @page_name.getter
    def page_name(self):
        if self.server_web_page == '' or not self.server_web_page:
            if self.server_status:
                try:
                    r = requests.get(self.server_full_address)
                    if r.ok:
                        self.html_title = r.content
                    else:
                        pass
                except requests.exceptions.ConnectionError as e:
                    self.html_title = None

            if self.html_title:
                self._page_name = self.html_title
            else:
                self._page_name = 'Homepage'
        return self._page_name

    @property
    def just_started(self):
        return self._just_started

    @just_started.setter
    def just_started(self, value: bool):
        self._just_started = value

    @property
    def full_status_string(self):
        return self._full_status_string

    @full_status_string.getter
    def full_status_string(self):
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

    # TODO: TitlesNames subclass?
    @property
    def html_title(self):
        return self._html_title

    @property
    def server_titles(self):
        return self._server_titles

    @property
    def use_friendly_server_names(self):
        return self._use_friendly_server_names

    @use_friendly_server_names.setter
    def use_friendly_server_names(self, value: bool):
        if value and self.server_titles and self.active_server_port in self.server_titles:
            self._use_friendly_server_names = value
        else:
            self._use_friendly_server_names = False

    @property
    def current_server_name(self):
        return self._current_server_name

    @current_server_name.getter
    def current_server_name(self):
        self._current_server_name = False
        if self.use_friendly_server_names:
            try:
                self._current_server_name = self.server_titles[self.active_server_port]
            except TypeError:
                self.LOGGER.warning("defaulting to non-friendly server_names due to error")
                pass
            except KeyError:
                self.LOGGER.warning("defaulting to non-friendly server_names due to error")
                pass
            except Exception:
                self.LOGGER.warning("defaulting to non-friendly server_names due to error")
                pass
        if not self._current_server_name:
            self._current_server_name = self.server_web_address
        return self._current_server_name

    @html_title.setter
    def html_title(self, req_content):
        req_content = str(req_content)
        if '<title>' in req_content:
            x = req_content.split('<title>')[-1]
            if '</title>' in x:
                self._html_title = x.split('</title>')[0]

    @property
    def is_down(self):
        return self._is_down

    @is_down.getter
    def is_down(self):
        if not self.local_machine_status or not self.machine_status or not self.server_status or not self.page_status:
            self._is_down = True
        else:
            self._is_down = False
        return self._is_down

    @property
    def down_timestamp(self):
        return self._down_timestamp

    @down_timestamp.getter
    def down_timestamp(self):
        if self.is_down and not self._down_timestamp:
            self._down_timestamp = datetime.datetime.now().timestamp()
        elif not self.is_down:
            self._down_timestamp = None
        return self._down_timestamp

    @property
    def length_of_time_down(self) -> datetime.timedelta:
        return self._length_of_time_down

    @length_of_time_down.getter
    def length_of_time_down(self) -> datetime.timedelta:
        if not self.is_down:
            pass
        else:
            self._length_of_time_down = (datetime.timedelta(seconds=datetime.datetime.now().timestamp())
                                         - datetime.timedelta(seconds=self.down_timestamp))
        return self._length_of_time_down

    def log_status(self) -> None:
        if self.server_status:
            if self.page_status:
                self.LOGGER.info(self.full_status_string)
            else:
                self.LOGGER.warning(self.full_status_string)
        else:
            self.LOGGER.critical(self.full_status_string)

    @staticmethod
    def get_status_string(status_bool: bool) -> str:
        if status_bool:
            return "UP"
        else:
            return "DOWN"

    def ping(self, **kwargs) -> bool:
        """
        Returns True if host (str) responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
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
