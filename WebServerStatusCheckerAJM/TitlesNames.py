import requests
from typing import Dict


# noinspection PyUnresolvedReferences
class TitlesNames:
    LOGGER = None

    def __init__(self, server_titles: Dict[int, str] = None, use_friendly_server_names: bool = True):
        self._html_title = None
        self._server_titles = server_titles
        self._use_friendly_server_names = use_friendly_server_names
        self._current_server_name = None
        self._page_name = None

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
    def html_title(self):
        return self._html_title

    @html_title.setter
    def html_title(self, req_content):
        req_content = str(req_content)
        if '<title>' in req_content:
            x = req_content.split('<title>')[-1]
            if '</title>' in x:
                self._html_title = x.split('</title>')[0]

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
