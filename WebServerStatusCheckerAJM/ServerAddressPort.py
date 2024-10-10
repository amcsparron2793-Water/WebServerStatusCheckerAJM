import requests


class ServerAddressPort:
    LOGGER = None

    def __init__(self):
        self._server_ports = None
        self._active_server_port = None
        self._server_web_address = None
        self._silent_run = False
        self._server_web_page = None
        self._server_full_address = None
        self._page_name = None

    @property
    def server_ports(self):
        return self._server_ports

    @server_ports.getter
    def server_ports(self):
        if not self._server_ports:
            self._server_ports = [8000, 80]
        elif not isinstance(self._server_ports, list):
            try:
                raise TypeError("server_ports must be a list of integers")
            except TypeError as e:
                self.LOGGER.error(e, exc_info=True)
                raise e
        for x in self._server_ports:
            if not isinstance(x, int):
                try:
                    raise TypeError("server_ports must be a list of integers")
                except TypeError as e:
                    self.LOGGER.error(e, exc_info=True)
                    raise e
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
    def server_web_address(self):
        return self._server_web_address

    # noinspection HttpUrlsUsage
    @server_web_address.getter
    def server_web_address(self):
        if isinstance(self._server_web_address, str):
            if self._server_web_address.startswith('http://') or self._server_web_address.startswith('https://'):
                pass
            elif '://' in self._server_web_address:
                warn_string = "non-http or https requests may not work"
                self.LOGGER.warning(warn_string)
                if not self.silent_run:
                    print(warn_string)
            else:
                warn_string = "no url scheme detected, defaulting to http."
                self.LOGGER.warning(warn_string)
                if not self.silent_run:
                    print(warn_string)
                self._server_web_address = 'http://' + self._server_web_address

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
