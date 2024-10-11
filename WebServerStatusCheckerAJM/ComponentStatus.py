from re import fullmatch
from abc import abstractmethod
import requests


class ComponentStatus:
    """
    Class ComponentStatus:
    Represents the status of various components including server, web page, machine,
     and local machine with network connectivity.

    Attributes:
    - _server_status: Status of the server.
    - _page_status: Status of the web page.
    - _machine_status: Status of the machine.
    - _local_machine_ping_host: Default IP address for pinging.
    - _local_machine_status: Status of the local machine.

    Methods:
    - ping: Abstract method for checking network connectivity.
    - server_full_address: Abstract method for getting the server address.

    Properties:
    - server_status: Property to get the server status based on connection to the server.
    - page_status: Property to get the web page status based on server status and web page availability.
    - machine_status: Property to get the machine status based on local machine status and network connectivity.
    - local_machine_ping_host: Property for getting the default ping host IP address or setting a new one.
    - local_machine_status: Property to get the local machine status based on the network connectivity to a specified host.
    """
    LOGGER = None

    def __init__(self):
        self._server_status = None
        self._page_status = None
        self._machine_status = None
        self._local_machine_ping_host = '8.8.8.8'
        self._local_machine_status = None

    @property
    @abstractmethod
    def ping(self):
        """
        @property
        @abstractmethod
        ping(self)
        Returns the status of the object, indicating if it is reachable or not.
        """

    @property
    @abstractmethod
    def server_full_address(self):
        """
        This method is an abstract property that represents the full address of a server.
        Subclasses must implement this property.
        """

    @property
    def server_status(self):
        """
        @property
        server_status(self)

        Represents the property for accessing the server status.
        """
        return self._server_status

    @server_status.getter
    def server_status(self):
        """
        Getter method for retrieving the status of the server by making a GET request to the server's full address.
        If the request is successful, the server status is set to True; otherwise,
         it is set to False in case of a ConnectionError.
         The status of the server is returned.
        """
        try:
            requests.get(self.server_full_address)
            self._server_status = True
        except requests.exceptions.ConnectionError:
            self._server_status = False

        return self._server_status

    @property
    def page_status(self):
        """
        Getter method for accessing the page_status property of the object.
        @return: The current value of the page_status property.
        """
        return self._page_status

    @page_status.getter
    def page_status(self):
        """
        Getter method for retrieving the current status of a web page.
        It checks the server status and attempts to make a GET request to the server's full address.
        If the request is successful (status code 200), the page status is set to True.
         If there is a connection error during the request, the page status is set to False.
          Finally, it returns the page status.
        """
        self._page_status = False
        if self.server_status:
            try:
                r = requests.get(self.server_full_address)
                if r.ok:
                    self._page_status = True
            except requests.exceptions.ConnectionError:
                self._page_status = False
        return self._page_status

    @property
    def machine_status(self):
        """
        Getter method to access the machine status attribute.
        """
        return self._machine_status

    @machine_status.getter
    def machine_status(self):
        """
        Getter method to determine the status of the machine based on local_machine_status and ping result.
        Returns True if machine is reachable, False otherwise.
        """
        self._machine_status = False
        if self.local_machine_status:
            if self.ping():
                self._machine_status = True
            else:
                self._machine_status = False
        return self._machine_status

    @property
    def local_machine_ping_host(self):
        """
        Method:
            local_machine_ping_host

        Description:
            This method retrieves the value of the _local_machine_ping_host property.

        Returns:
            The value of the _local_machine_ping_host property.
        """
        return self._local_machine_ping_host

    @local_machine_ping_host.setter
    def local_machine_ping_host(self, value):
        """
        Sets the local machine's host address for ping testing. Raises an AttributeError
        if the input value is not a valid plain IP address.

        Parameters:
            value (str): The new host address for ping testing.

        Raises:
            AttributeError: If the input value is not a valid plain IP address.
            TypeError: If the value type is not valid.
        """
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
        """
        @property
        def local_machine_status(self):
            Returns the current status of the local machine.
        """
        return self._local_machine_status

    @local_machine_status.getter
    def local_machine_status(self):
        """
        Getter method to retrieve the status of the local machine by pinging a specified host.
        Returns True if the ping is successful, False otherwise.
        """
        if self.ping(host=self.local_machine_ping_host):
            self._local_machine_status = True
        else:
            self._local_machine_status = False
        return self._local_machine_status
