"""Shared test setup: no real network, output/ redirected to a temp dir."""

import io
import json
import os
import shutil
import socket
import tempfile
import unittest
import urllib.error
from unittest import mock

from js2 import policy


def _no_network(*args, **kwargs):
    raise AssertionError("a test tried to open a real network connection")


class FakeResponse:
    def __init__(self, body, status=200):
        self.body = body
        self.status = status

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def http_error(url, code):
    return urllib.error.HTTPError(url, code, "status %d" % code, {}, io.BytesIO(b""))


def greenhouse_body(*ids):
    return json.dumps({"jobs": [{"id": i, "title": "Job %s" % i} for i in ids]}).encode()


def lever_body(*ids):
    return json.dumps([{"id": i, "text": "Job %s" % i} for i in ids]).encode()


class SandboxTestCase(unittest.TestCase):
    """Points ALLOWED_OUTPUT at a temp dir and blocks every socket."""

    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp(prefix="js2-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.output = os.path.join(self.tmp, "output")
        os.makedirs(self.output)
        for target, value in [
            ("js2.policy.ALLOWED_OUTPUT", self.output),
            ("socket.create_connection", _no_network),
            ("socket.socket.connect", _no_network),
        ]:
            p = mock.patch(target, value)
            p.start()
            self.addCleanup(p.stop)
        del policy.DECISIONS[:]
        self.addCleanup(policy.DECISIONS.clear)
