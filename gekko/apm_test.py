"""Remote transport regressions; run with python -m unittest gekko.apm_test."""
import io
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs

from gekko import GEKKO, apm


class RemoteTransportTests(unittest.TestCase):
    def test_default_server_uses_https(self):
        with patch('gekko.gekko.cmd') as cmd:
            model = GEKKO(remote=True)
        self.addCleanup(model.cleanup)
        self.assertEqual(model._server, 'https://byu.apmonitor.com')
        cmd.assert_called_once_with(model._server, model._model_name, 'clear all')

    def test_explicit_http_server_is_preserved(self):
        with patch('gekko.gekko.cmd'):
            model = GEKKO(remote=True, server='http://localhost:8080')
        self.addCleanup(model.cleanup)
        self.assertEqual(model._server, 'http://localhost:8080')

    def assert_request(self, request, path):
        self.assertEqual(request.full_url, 'https://byu.apmonitor.com' + path)
        self.assertTrue(request.get_header('User-agent').startswith('GEKKO'))

    def test_upload_preserves_form_data_and_identifies_client(self):
        line = 'Model\n! temperature \u00b0C & x+y=2\nEnd Model'
        with patch('urllib.request.urlopen', return_value=io.BytesIO(b'OK')) as open_url:
            self.assertEqual(apm.cmd('https://byu.apmonitor.com', 'Model', line), 'OK')
        request = open_url.call_args[0][0]
        self.assert_request(request, '/online/apm_line.php')
        self.assertEqual(request.get_method(), 'POST')
        self.assertEqual(parse_qs(request.data.decode()), {'p': ['model'], 'a': [line]})

    def test_ip_lookup_and_download_identify_client(self):
        with patch('urllib.request.urlopen', side_effect=[
            io.BytesIO(b'192.0.2.1 \r\n'), io.BytesIO(b'{"x": [2]}')
        ]) as open_url:
            result = apm.get_file('https://byu.apmonitor.com', 'Model', 'results.json')
        self.assertEqual(result, b'{"x": [2]}')
        self.assert_request(open_url.call_args_list[0][0][0], '/ip.php')
        request = open_url.call_args_list[1][0][0]
        self.assert_request(request, '/online/192.0.2.1_model/results.json')
        self.assertEqual(request.get_method(), 'GET')

    def test_solve_stream_still_reports_solver_errors(self):
        with patch('urllib.request.urlopen', return_value=io.BytesIO(
            b'APMonitor\n@error: infeasible\nNo solution\n'
        )):
            response = apm.cmd('https://byu.apmonitor.com', 'model', 'solve', disp=False)
        self.assertEqual(response, '@error: infeasible\nNo solution\n')

    def test_http_error_is_not_silently_ignored(self):
        error = HTTPError('https://byu.apmonitor.com/online/apm_line.php',
                          403, 'Forbidden', {}, io.BytesIO(b'error code: 1010'))
        with patch('urllib.request.urlopen', side_effect=error) as open_url:
            with self.assertRaisesRegex(IOError, '403.*Forbidden'):
                apm.cmd('https://byu.apmonitor.com', 'model', 'clear all')
        self.assertEqual(open_url.call_count, 1)

    def test_tls_failure_is_reported_without_insecure_retry(self):
        error = URLError('CERTIFICATE_VERIFY_FAILED')
        with patch('urllib.request.urlopen', side_effect=error) as open_url:
            with self.assertRaisesRegex(IOError, 'CERTIFICATE_VERIFY_FAILED'):
                apm.cmd('https://byu.apmonitor.com', 'model', 'clear all')
        self.assertEqual(open_url.call_count, 1)
        self.assertEqual(open_url.call_args.kwargs, {})

    def test_download_error_is_retained_by_solve(self):
        with patch('gekko.gekko.cmd'):
            model = GEKKO(remote=True)
            self.addCleanup(model.cleanup)
            x = model.Var()
            model.Equation(x == 2)
            with patch('gekko.gekko.get_file', side_effect=URLError('TLS diagnostic')):
                with self.assertRaisesRegex(ImportError, 'TLS diagnostic'):
                    model.solve(disp=False)


if __name__ == '__main__':
    unittest.main()
