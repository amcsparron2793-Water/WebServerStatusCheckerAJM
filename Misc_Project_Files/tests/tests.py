import unittest
from WebServerStatusCheckerAJM.WebServerStatusCheckerAJM import WebServerStatusCheck


class WSSCTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bad_port_WSSC = WebServerStatusCheck('http://10.56.211.116/', [80, 8010])
        self.good_ports_WSSC = WebServerStatusCheck('http://10.56.211.116/', [80, 8000])
        self.no_box_WSSC = WebServerStatusCheck('http://10.56.211.116/', [80, 8000], use_msg_box_on_error=False)

    def test_msg_box_on_down_no_error(self):
        self.bad_port_WSSC.active_server_port = self.bad_port_WSSC.server_ports[1]
        print(self.bad_port_WSSC.full_status_string)
        try:
            self.assertIs(self.bad_port_WSSC._tk_msgbox_attempted, True)
            return
        except AssertionError:
            print('first condition not met, trying second.')
            pass
        self.assertIs(self.bad_port_WSSC._msgbox_defaulting_to_win, True)

    def test_no_down_no_msgbox(self):
        print(self.good_ports_WSSC.full_status_string)
        self.assertIs(self.good_ports_WSSC._tk_msgbox_attempted, False)
        self.assertIs(self.good_ports_WSSC._msgbox_defaulting_to_win, False)

    def test_no_msg_box_if_attr(self):
        print(self.no_box_WSSC.full_status_string)
        self.assertIs(self.no_box_WSSC._tk_msgbox_attempted, False)
        self.assertIs(self.no_box_WSSC._msgbox_defaulting_to_win, False)


if __name__ == '__main__':
    unittest.main()
