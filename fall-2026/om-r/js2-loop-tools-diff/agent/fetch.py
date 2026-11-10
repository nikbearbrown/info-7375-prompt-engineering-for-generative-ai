"""The only network access in this codebase (JS1 pattern, extended).
Allow-listed via agent.permissions.check_url, HTTPS only, and redirects off
the allow-list are refused (urllib would otherwise follow them)."""
import urllib.request

from agent.permissions import check_url

TIMEOUT_S = 30


class _AllowListRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_opener = urllib.request.build_opener(_AllowListRedirects)


def fetch(url, timeout=TIMEOUT_S):
    """Return the raw response bytes. Raises urllib.error.HTTPError on 4xx/5xx."""
    check_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": "js2-loop-tools-diff (INFO7375 coursework)"})
    with _opener.open(req, timeout=timeout) as resp:
        check_url(resp.geturl())
        return resp.read()
