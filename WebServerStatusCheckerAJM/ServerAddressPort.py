from abc import abstractmethod
from typing import List


class ServerAddressPort:
    """
    ServerAddressPort class represents a server address and port configuration.

    Parameters:
    - server_web_address (str): The web address of the server.
    - server_ports (List[int], optional): The list of available server ports. Defaults to [8000, 80].
    - server_web_page (str or None, optional): The specific webpage on the server. Defaults to None.

    Attributes:
    - _server_ports (List[int]): List of available server ports.
    - _active_server_port (int): The currently active server port.
    - _server_web_address (str): The web address of the server.
    - _server_web_page (str): The specific webpage on the server.
    - _server_full_address (str): Full address including server web address, port, and webpage.
    - _page_name (str): Name of the webpage derived from the server web address.

    Properties:
    - server_ports: Getter property to retrieve the list of server ports ensuring they are integers.
    - active_server_port: Getter and setter property to manage the active server port.
    - server_web_address: Getter property to handle the server web address ensuring it is formatted correctly.
    - server_web_page: Getter property to retrieve the server webpage.
    - server_full_address: Getter property to construct the full server address with port and webpage.

    Note:
    - The class provides validation and handling of server address, ports, and web page for server communication.
    """
    LOGGER = None

    def __init__(self,  server_web_address: str, server_ports: List[int] = None, server_web_page: str or None = None):
        self._server_ports = server_ports
        self._active_server_port = self.server_ports[0]
        self._server_web_address = server_web_address
        self._server_web_page = server_web_page
        self._server_full_address = None
        self._page_name = None

    @property
    @abstractmethod
    def silent_run(self):
        """
        This method defines the silent_run property for a class.
        It is a read-only property that can be accessed but not modified directly.
        """

    @property
    def server_ports(self):
        """
        Property: server_ports

        This property returns a list of server ports. If the property is not set, it defaults to [8000, 80].
        In case the property is set with a value that is not a list, a TypeError is raised with a corresponding error message.
        Additionally, if any element of the list is not an integer, a TypeError is raised with an error message.
        """
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
        """
        Gets the value of the active server port.
        """
        return self._active_server_port

    @active_server_port.setter
    def active_server_port(self, value):
        """
        Set the active server port to the specified value if it is present in the list of server ports.
        If the value is not valid (not in the server ports list), a ValueError is raised.
        """
        if value in self.server_ports:
            self._active_server_port = value
        else:
            raise ValueError("not a valid port!")

    @property
    def server_web_address(self):
        """
        This method returns the server web address after performing necessary validation and formatting checks.
        It ensures that the address starts with either 'http://' or 'https://', warns about potential issues
        with other protocols, defaults to 'http://' if no scheme is detected, and ensures that the address ends
        with a slash '/' for consistency. If the input address is not a string, a TypeError is raised.
        """
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
        """
        Property to retrieve the web page from the server web address. If the web page has not been previously fetched,
        it extracts the last segment of the address as the web page and caches it for future use.
        """
        if self._server_web_page:
            pass
        else:
            self._server_web_page = self.server_web_address.split('/')[-1]
        return self._server_web_page

    @property
    def server_full_address(self):
        """
        Property to return the full address of the server, including the web address, active port, and web page.
         The function constructs the full address using the server's web address, active port, and web page information.
          If the constructed address does not end with a '/', a trailing '/' is added.

        Returns the server's full address.
        """
        self._server_full_address = ('/'.join(self.server_web_address.rsplit('/', maxsplit=1)[:-1])
                                     + f':{self.active_server_port}/' + self.server_web_page)
        if self._server_full_address.endswith('/'):
            pass
        else:
            self._server_full_address = self._server_full_address + '/'
        return self._server_full_address
