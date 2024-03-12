"""
WebServerStatusCheckerAJM.py

Pings a machine to see if it is up, then checks for the presence of a given http server
 (originally conceived for use with Django and Apache).

"""

import requests
from time import sleep
import platform
import subprocess

from typing import List, Dict
from datetime import datetime
from EasyLoggerAJM import EasyLogger
from os.path import isdir

import ctypes
import winsound
import tkinter.messagebox



class WebServerEasyLogger(EasyLogger):
    @classmethod
    def smart_default_log_location(cls):
        if isdir('../Misc_Project_Files'):
            ...
        raise NotImplementedError("not implemented yet.")


class WebServerStatusCheck:
    logger = EasyLogger.UseLogger().logger

    def __init__(self, server_web_address: str, server_ports: List[int] = None,
                 server_titles: Dict[int, str] = None, use_friendly_server_names: bool = True,
                 server_web_page: str or None = None, silent_run: bool = False, use_msg_box_on_error: bool = True):
        self._machine_status = None
        self._silent_run = silent_run
        self._print_status = True
        self._msgbox_defaulting_to_win = False
        self._tk_msgbox_attempted = False

        self.use_msg_box_on_error = use_msg_box_on_error

        self.winapi_msg_box_styles = {
            'OK': 0,
            'OK_Cancel': 1,
            'Abort_Retry _Ignore': 2,
            'Yes_No_Cancel': 3,
            'Yes_No': 4,
            'Retry_Cancel': 5,
            'Cancel_Try Again_Continue': 6,
            'Above_All_OK': 0x1000}

        if not self.silent_run:
            print('initializing server status checker...')

        self._server_ports = server_ports
        self._server_titles = server_titles
        self._use_friendly_server_names = use_friendly_server_names
        self._active_server_port = self.server_ports[0]

        self._server_web_address = server_web_address
        self._server_web_page = server_web_page

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
        if style not in self.winapi_msg_box_styles.values():
            try:
                raise AttributeError("given style is not valid! No message box will be displayed.")
            except AttributeError as e:
                print(self.logger.warning(e))
                self.logger.warning(e)
        winsound.MessageBeep(winsound.MB_ICONHAND)
        # 0 == no parent window
        return ctypes.windll.user32.MessageBoxW(0, text, title, style)

    @property
    def server_ports(self):
        return self._server_ports

    @server_ports.getter
    def server_ports(self):
        if not self._server_ports:
            self._server_ports = [8000, 80]
        elif not isinstance(self._server_ports, list):
            raise TypeError("server_ports must be a list of integers")
        return self._server_ports

    @property
    def active_server_port(self):
        return self._active_server_port

    @active_server_port.setter
    def active_server_port(self, value):
        if value in self.server_ports:
            self._active_server_port = value
        else:
            raise ValueError("not a valid port!")

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
    def server_web_address(self):
        return self._server_web_address

    @server_web_address.getter
    def server_web_address(self):
        if isinstance(self._server_web_address, str):
            if self._server_web_address.endswith('/'):
                pass
            elif self._server_web_address.endswith('\\'):
                self._server_web_address.replace('\\', '/')
            else:
                self._server_web_address = self._server_web_address + '/'
        else:
            raise TypeError("self._server_web_address must be a string")
        return self._server_web_address

    @property
    def server_web_page(self):
        return self._server_web_page

    @server_web_page.getter
    def server_web_page(self):
        if self._server_web_page:
            pass
        else:
            self._server_web_page = self.server_web_address.split('/')[-1]
        return self._server_web_page

    @property
    def server_full_address(self):
        return self._server_full_address

    @server_full_address.getter
    def server_full_address(self):
        self._server_full_address = ('/'.join(self.server_web_address.rsplit('/', maxsplit=1)[:-1])
                                     + f':{self.active_server_port}/' + self.server_web_page)
        if self._server_full_address.endswith('/'):
            pass
        else:
            self._server_full_address = self._server_full_address + '/'
        return self._server_full_address

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
    def server_status(self):
        return self._server_status

    @server_status.getter
    def server_status(self):
        try:
            r = requests.get(self.server_full_address)
            self._server_status = True
        except requests.exceptions.ConnectionError as e:
            self._server_status = False

        return self._server_status

    @property
    def page_status(self):
        return self._page_status

    @page_status.getter
    def page_status(self):
        self._page_status = False
        if self.server_status:
            try:
                r = requests.get(self.server_full_address)
                if r.ok:
                    self._page_status = True
            except requests.exceptions.ConnectionError as e:
                self._page_status = False
        return self._page_status

    @property
    def machine_status(self):
        return self._machine_status

    @machine_status.getter
    def machine_status(self):
        if self.ping():
            self._machine_status = True
        else:
            self._machine_status = False
        return self._machine_status

    @property
    def full_status_string(self):
        return self._full_status_string

    @full_status_string.getter
    def full_status_string(self):
        self._full_status_string = (f"\t{datetime.now().ctime()}: System Status on port {self.active_server_port} is:"
                                    f"\n\t\tMachine is: {self.get_status_string(self.machine_status)}"
                                    f"\n\t\tServer: \'{self.current_server_name}\' on "
                                    f"\n\t\tPort: {self.active_server_port} is "
                                    f"{self.get_status_string(self.server_status)}. "
                                    f"\n\t\tPage: \'{self.server_web_page or self.page_name}\' is "
                                    f"{self.get_status_string(self.page_status)}")
        
        if self.use_msg_box_on_error:
            if not self.machine_status or not self.server_status or not self.page_status:
                try:
                    tkinter.messagebox.showerror(title="PART OR ALL OF SERVER DOWN",
                                                 message=self._full_status_string.replace('\t', ''))
                    self._tk_msgbox_attempted = True

                except Exception as e:
                    self.logger.warning(e)
                    self._msgbox_defaulting_to_win = True
                    self.show_message_box("PART OR ALL OF SERVER DOWN",
                                          self._full_status_string.replace('\t', ''),
                                          self.winapi_msg_box_styles['Above_All_OK'])

        return self._full_status_string

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
                self.logger.warning("defaulting to non-friendly server_names due to error")
                pass
            except KeyError:
                self.logger.warning("defaulting to non-friendly server_names due to error")
                pass
            except Exception:
                self.logger.warning("defaulting to non-friendly server_names due to error")
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

    def log_status(self) -> None:
        if self.server_status:
            if self.page_status:
                self.logger.info(self.full_status_string)
            else:
                self.logger.warning(self.full_status_string)
        else:
            self.logger.critical(self.full_status_string)

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
            self.logger.error(e, exc_info=True)
            raise e


if __name__ == '__main__':
    WebServerStatusCheck('10.56.211.116', [80])
