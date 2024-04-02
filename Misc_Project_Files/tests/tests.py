from datetime import timedelta
import unittest
from time import sleep

from WebServerStatusCheckerAJM.WebServerStatusCheckerAJM import WebServerStatusCheck, __version__


class WSSCTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bad_port_WSSC = WebServerStatusCheck('http://10.56.211.116/', [80, 8010],
                                                  silent_run=True)
        self.bad_port_WSSC.active_server_port = self.bad_port_WSSC.server_ports[1]
        self.good_ports_WSSC = WebServerStatusCheck('http://10.56.211.116/', [80, 8000],
                                                    silent_run=True)
        self.no_box_WSSC = WebServerStatusCheck('http://10.56.211.116/', [80, 8010],
                                                use_msg_box_on_error=False, silent_run=True)
        self.no_box_WSSC.active_server_port = self.no_box_WSSC.server_ports[1]

    def test_server_ports_not_int_fail(self):
        with self.assertRaises(TypeError):
            WebServerStatusCheck('http://10.56.211.116/', [80, 'teta'])

    def test_server_ports_not_list_fail(self):
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            WebServerStatusCheck('http://10.56.211.116/', (80, 'teta'))

    def test_no_init_msg_true(self):
        init_msg_False_WSSC = WebServerStatusCheck('http://10.56.211.116/', [80, 8000],
                                                   init_msg=False)
        init_msg_True_WSSC = WebServerStatusCheck('http://10.56.211.116/', [80, 8000],
                                                  init_msg=True)
        init_msg_default_WSSC = WebServerStatusCheck('http://10.56.211.116/', [80, 8000])

        self.assertIs(init_msg_False_WSSC.init_msg, False)
        self.assertIs(init_msg_True_WSSC.init_msg, True)
        self.assertIs(init_msg_default_WSSC.init_msg, True)

    def test_silent_run_silences_init_msg(self):
        silent_run_silences_init_WSSC = WebServerStatusCheck('http://10.56.211.116/', [80, 8000],
                                                             silent_run=True)
        try:
            raise NotImplementedError("still working on this")
        except NotImplementedError as e:
            print(e)
            pass

    def test_can_import_version(self):
        from sys import modules
        self.assertIn('WebServerStatusCheckerAJM._version', modules)
        self.assertIsNotNone(__version__)

    def test_online_local_machine_status_returns_true(self):
        self.assertIs(self.good_ports_WSSC.local_machine_status, True)

    def test_bad_host_for_local_machine_host_returns_false(self):
        self.good_ports_WSSC.local_machine_ping_host = '999.898.999.111'
        self.assertIs(self.good_ports_WSSC.local_machine_status, False)

    def test_local_machine_status_shows_in_popup(self):
        self.assertIn('local machine is:',
                      self.good_ports_WSSC.full_status_string.lower())

    def test_local_machine_status_port_defaults_to_eight_dot(self):
        WSSC = WebServerStatusCheck('http://10.56.211.116/', [80, 8000],
                                    silent_run=True)
        self.assertEqual(WSSC.local_machine_ping_host, '8.8.8.8')

    def test_local_machine_status_port_fails_on_invalid_ip_too_long(self):
        with self.assertRaises(AttributeError):
            self.good_ports_WSSC.local_machine_ping_host = '1234.1234.1234.1234'

    def test_local_machine_status_port_fails_on_invalid_ip_not_numeric(self):
        with self.assertRaises(AttributeError):
            self.good_ports_WSSC.local_machine_ping_host = 'asd.asd.asd.asd'

    def test_local_machine_status_port_fails_on_invalid_ip_str(self):
        with self.assertRaises(AttributeError):
            self.good_ports_WSSC.local_machine_ping_host = 'http://8.8.8.8'

    def test_local_machine_status_port_raises_TypeError_on_no_ip_str(self):
        with self.assertRaises(TypeError):
            self.good_ports_WSSC.local_machine_ping_host = None

    def test_local_machine_status_port_raises_TypeError_on_int_ip_str(self):
        with self.assertRaises(TypeError):
            self.good_ports_WSSC.local_machine_ping_host = 1234

    def test_downtime_makes_sense(self):
        self.bad_port_WSSC.use_msg_box_on_error = False
        for p in self.bad_port_WSSC.server_ports:
            self.bad_port_WSSC.active_server_port = p
            print(self.bad_port_WSSC.full_status_string)

            s_time = timedelta(seconds=5)
            sleep_time_plus_deadzone = timedelta(seconds=(s_time.seconds + 3)*2)
            # {chr(177)} can also be used for +-
            print(f"Sleeping for {s_time}. \nAssertion time with dead-zone is \xB1 {sleep_time_plus_deadzone}")
            sleep(s_time.total_seconds())
            if self.bad_port_WSSC.is_down:
                # make sure it actually slept for at least s_time if not more,
                # but not more than sleep_time_plus_deadzone
                self.assertGreaterEqual(self.bad_port_WSSC.length_of_time_down, timedelta(seconds=s_time.total_seconds()))
                self.assertLessEqual(self.bad_port_WSSC.length_of_time_down, timedelta(seconds=sleep_time_plus_deadzone.total_seconds()))
                print(f"actual downtime was {self.bad_port_WSSC.length_of_time_down}")
            else:
                print(timedelta(seconds=0), self.bad_port_WSSC.length_of_time_down)
                self.assertEqual(timedelta(seconds=0), self.bad_port_WSSC.length_of_time_down)
            print(f"Port {p} test complete.\n")

    def test_not_down_length_of_time_down_is_none(self):
        print(self.good_ports_WSSC.full_status_string)
        self.assertEqual(self.good_ports_WSSC.length_of_time_down, timedelta(seconds=0))
        self.assertIsNone(self.good_ports_WSSC.down_timestamp)

    @staticmethod
    def _get_window_list():
        # this comes as part of pywin32
        from win32gui import IsWindowVisible, GetWindowText, EnumWindows
        window_list = []

        def winEnumHandler(hwnd, ctx):
            if IsWindowVisible(hwnd) and GetWindowText(hwnd):
                #print(hex(hwnd), win32gui.GetWindowText(hwnd))
                window_list.append(GetWindowText(hwnd))

        EnumWindows(winEnumHandler, None)
        return window_list


if __name__ == '__main__':
    unittest.main()
