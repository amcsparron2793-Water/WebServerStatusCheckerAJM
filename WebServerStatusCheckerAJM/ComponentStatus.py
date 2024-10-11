from re import fullmatch

import requests


class ComponentStatus:
    LOGGER = None

    def __init__(self):
        self._server_status = None
        self._page_status = None
        self._machine_status = None
        self._local_machine_ping_host = '8.8.8.8'
        self._local_machine_status = None

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
        self._machine_status = False
        if self.local_machine_status:
            if self.ping():
                self._machine_status = True
            else:
                self._machine_status = False
        return self._machine_status

    @property
    def local_machine_ping_host(self):
        return self._local_machine_ping_host

    @local_machine_ping_host.setter
    def local_machine_ping_host(self, value):
        try:
            if fullmatch(r'^((\d{1,3}\.){3}(\d{1,3}))', value):
                self._local_machine_ping_host = value
            else:
                try:
                    raise AttributeError('must be a valid PLAIN IP address in the form of ddd.ddd.ddd'
                                         ' or any other valid octet')
                except AttributeError as e:
                    self.LOGGER.error(e, exc_info=True)
                    raise e
        except TypeError as e:
            self.LOGGER.error(e, exc_info=True)
            raise e

    @property
    def local_machine_status(self):
        return self._local_machine_status

    @local_machine_status.getter
    def local_machine_status(self):
        """ pings a very high uptime server (one of googles public DNS servers,
         or a given server through self.local_machine_ping_host)
        to see if the machine on which the code is running, has any network connectivity at all."""
        if self.ping(host=self.local_machine_ping_host):
            self._local_machine_status = True
        else:
            self._local_machine_status = False
        return self._local_machine_status
