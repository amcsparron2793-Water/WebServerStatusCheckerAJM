from datetime import timedelta
import unittest
from time import sleep

from WebServerStatusCheckerAJM.WebServerStatusCheckerAJM import WebServerStatusCheck, __version__


class WSSCTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bad_port_WSSC = WebServerStatusCheck('http://10.56.211.116/', [80, 8010],
                                                  silent_run=True)
        self.good_ports_WSSC = WebServerStatusCheck('http://10.56.211.116/', [80, 8000],
                                                    silent_run=True)
        self.no_box_WSSC = WebServerStatusCheck('http://10.56.211.116/', [80, 8000],
                                                use_msg_box_on_error=False, silent_run=True)

    def test_server_ports_not_int_fail(self):
        with self.assertRaises(TypeError):
            WebServerStatusCheck('http://10.56.211.116/', [80, 'teta'])

    def test_server_ports_not_list_fail(self):
        with self.assertRaises(TypeError):
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
        self.bad_port_WSSC.active_server_port = self.bad_port_WSSC.server_ports[1]
        print(self.bad_port_WSSC.full_status_string)

        s_time = 5
        print(f"sleeping for {s_time} secs")
        sleep(s_time)
        self.assertGreaterEqual(self.bad_port_WSSC.length_of_time_down, timedelta(seconds=s_time))

    def test_not_down_length_of_time_down_is_none(self):
        print(self.good_ports_WSSC.full_status_string)
        self.assertEqual(self.good_ports_WSSC.length_of_time_down, 0)
        self.assertIsNone(self.good_ports_WSSC.down_timestamp)


if __name__ == '__main__':
    unittest.main()
