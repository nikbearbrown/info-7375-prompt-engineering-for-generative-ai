"""The only code that touches the network. GET only; every URL and redirect target goes through the policy."""

import socket
import urllib.error
import urllib.request

USER_AGENT = "js2-loop-tools-diff/1.0 (INFO 7375 coursework; read-only)"


class TransientError(Exception):
    """A failure a retry might fix: timeout or connection error. .kind says which."""

    def __init__(self, kind, detail=""):
        super().__init__(f"{kind}: {detail}" if detail else kind)
        self.kind = kind


class PolicyRefused(Exception):
    pass


def make_transport(policy):
    class Redirects(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            d = policy.check_request("GET", newurl)
            if d.verdict != "allow":
                raise PolicyRefused(f"redirect refused: {d.reason}")
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    opener = urllib.request.build_opener(Redirects())

    def transport(url, timeout):
        d = policy.check_request("GET", url)
        if d.verdict != "allow":
            raise PolicyRefused(d.reason)
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with opener.open(req, timeout=timeout) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()
        except (socket.timeout, TimeoutError) as e:
            raise TransientError("timeout", str(e))
        except urllib.error.URLError as e:
            if isinstance(e.reason, (socket.timeout, TimeoutError)):
                raise TransientError("timeout", str(e.reason))
            raise TransientError("connection", str(e.reason))

    return transport
