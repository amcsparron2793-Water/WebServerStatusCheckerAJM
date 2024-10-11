from abc import abstractmethod
from typing import Dict

import requests


class TitlesNames:
    """
    Class representing server titles and names for a web page.

    Attributes:
        LOGGER: Logger object for logging messages.

    Methods:
        __init__(server_titles: Dict[int, str] = None, use_friendly_server_names: bool = True):
            Initialize the TitlesNames object with server titles and use of friendly server names.

    Properties:
        page_name:
            Retrieve the page name associated with the server web page.

        html_title:
            Retrieve the HTML title of the web page.

        server_titles:
            Retrieve the server titles dictionary.

        use_friendly_server_names:
            Retrieve the flag indicating the use of friendly server names.

        current_server_name:
            Retrieve the current server name based on configuration.

    Setter Methods:
        html_title(req_content):
            Set the HTML title based on the given request content.

        use_friendly_server_names(value: bool):
            Set the flag to indicate the use of friendly server names.
    """
    LOGGER = None

    def __init__(self, server_titles: Dict[int, str] = None, use_friendly_server_names: bool = True):
        self._html_title = None
        self._server_titles = server_titles
        self._use_friendly_server_names = use_friendly_server_names
        self._current_server_name = None
        self._page_name = None

    @property
    @abstractmethod
    def server_web_page(self):
        """
        Decorator indicating an abstract method that must be overridden in a subclass.

        Returns the server web page.
        """

    @property
    @abstractmethod
    def server_status(self):
        """
        This method is an abstract property that represents the status of the server.
        Any class that inherits this method must implement its getter method to return
        the server status information.
        """

    @property
    @abstractmethod
    def server_full_address(self):
        """
           This method is an abstract property that returns the full address of the server.
           Subclasses must implement this property with the appropriate logic to return the
           server's full address.
        """
    @property
    @abstractmethod
    def active_server_port(self):
        """
            @abstractmethod
            @property
            def active_server_port(self):
            This method is an abstract property that should be implemented by subclasses.
            It is used to retrieve the port number of the active server.
        """
    @property
    @abstractmethod
    def server_web_address(self):
        """
        This method defines an abstract property named server_web_address.
        Subclasses must implement this property by returning the web address of the server.
        """

    @property
    def page_name(self):
        """
        This property returns the name of the web page.
        If the 'server_web_page' attribute is empty or not present,
        it makes a request to the server using the 'server_full_address' attribute to fetch the HTML content.
         If the request is successful, it sets the 'html_title' attribute to the content,
         otherwise it does nothing.
         If a ConnectionError occurs during the request, it sets the 'html_title' attribute to None.
         Finally, it returns the page name based on the 'html_title' attribute or
          defaults to 'Homepage' if 'html_title' is empty.
        """
        if self.server_web_page == '' or not self.server_web_page:
            if self.server_status:
                try:
                    r = requests.get(self.server_full_address)
                    if r.ok:
                        self.html_title = r.content
                    else:
                        pass
                except requests.exceptions.ConnectionError:
                    self.html_title = None

            if self.html_title:
                self._page_name = self.html_title
            else:
                self._page_name = 'Homepage'
        return self._page_name

    @property
    def html_title(self):
        """
        Property to access the HTML title of the document.

        @return: The HTML title of the document.
        """
        return self._html_title

    @html_title.setter
    def html_title(self, req_content):
        """
        Sets the HTML title of the object based on the provided HTML content.
        If the provided content contains a <title> tag, it extracts the text
        between the opening and closing tags to set as the HTML title.
        """
        req_content = str(req_content)
        if '<title>' in req_content:
            x = req_content.rsplit('<title>', maxsplit=1)[-1]
            if '</title>' in x:
                self._html_title = x.split('</title>')[0]

    @property
    def server_titles(self):
        """
        @property
        This property returns the value of the _server_titles attribute.
        """
        return self._server_titles

    @property
    def use_friendly_server_names(self):
        """
        Getter method for the use_friendly_server_names property.
        Returns the value of the _use_friendly_server_names attribute.
        """
        return self._use_friendly_server_names

    @use_friendly_server_names.setter
    def use_friendly_server_names(self, value: bool):
        """
        Set whether to use friendly server names when displaying server information.

        Parameters:
            value (bool): The value to set for using friendly server names.

        Returns:
            None.

        Raises:
            None.
        """
        if value and self.server_titles and self.active_server_port in self.server_titles:
            self._use_friendly_server_names = value
        else:
            self._use_friendly_server_names = False

    @property
    def current_server_name(self):
        """
        Gets the current server name based on the active server port.
        If `use_friendly_server_names` attribute is True,
        it tries to fetch the friendly server name from `server_titles`
         based on the active server port. If there are any exceptions or errors,
         it logs a warning and defaults to `server_web_address`.

         Returns the current server name.
        """
        self._current_server_name = False
        if self.use_friendly_server_names:
            try:
                self._current_server_name = self.server_titles[self.active_server_port]
            except TypeError:
                self.LOGGER.warning("defaulting to non-friendly server_names due to error")
            except KeyError:
                self.LOGGER.warning("defaulting to non-friendly server_names due to error")
            except Exception:
                self.LOGGER.warning("defaulting to non-friendly server_names due to error")
        if not self._current_server_name:
            self._current_server_name = self.server_web_address
        return self._current_server_name
