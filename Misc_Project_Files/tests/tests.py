import unittest
from WebServerStatusCheckerAJM.WebServerStatusCheckerAJM import WebServerStatusCheck


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
        raise NotImplementedError("still working on this")


if __name__ == '__main__':
    unittest.main()
