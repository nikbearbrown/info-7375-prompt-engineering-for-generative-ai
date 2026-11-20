"""CONTRACT.md section 4: never access a host outside boards-api.greenhouse.io,
including through redirects. No test here touches the network."""
import unittest
import urllib.error
import urllib.request

from jsagent import fetch


class AllowList(unittest.TestCase):
    def test_board_url_is_on_list(self):
        url = fetch.board_url("oscar")
        self.assertEqual(url, "https://boards-api.greenhouse.io/v1/boards/oscar/jobs?content=true")
        fetch.check_url(url)

    def test_other_hosts_refused(self):
        for url in ("https://evil.example.com/v1/boards/oscar/jobs",
                    "https://boards-api.greenhouse.io.evil.com/x",
                    "https://boards.greenhouse.io/oscar",
                    "https://api.lever.co/v0/postings/x"):
            with self.assertRaises(fetch.HostNotAllowed, msg=url):
                fetch.check_url(url)

    def test_plain_http_refused(self):
        with self.assertRaises(fetch.HostNotAllowed):
            fetch.check_url("http://boards-api.greenhouse.io/v1/boards/oscar/jobs")

    def test_userinfo_trick_refused(self):
        with self.assertRaises(fetch.HostNotAllowed):
            fetch.check_url("https://boards-api.greenhouse.io@evil.example.com/x")

    def test_bad_board_token_refused(self):
        for token in ("../etc", "oscar/jobs?x=", "", "a b"):
            with self.assertRaises(ValueError, msg=token):
                fetch.board_url(token)

    def test_redirect_off_list_refused(self):
        handler = fetch.AllowListRedirectHandler()
        req = urllib.request.Request(fetch.board_url("oscar"))
        with self.assertRaises(fetch.HostNotAllowed):
            handler.redirect_request(req, None, 302, "Found", {}, "https://evil.example.com/jobs")

    def test_redirect_on_list_allowed(self):
        handler = fetch.AllowListRedirectHandler()
        req = urllib.request.Request(fetch.board_url("oscar"))
        new = handler.redirect_request(req, None, 301, "Moved", {},
                                       "https://boards-api.greenhouse.io/v1/boards/oscar/jobs")
        self.assertIsNotNone(new)


if __name__ == "__main__":
    unittest.main()
