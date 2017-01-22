from sys import getdefaultencoding

from six import PY3
from treq.testing import RequestTraversalAgent
from twisted.internet import defer
from twisted.web.client import CookieAgent, readBody
from zope.interface import directlyProvides

if PY3:
    from http.cookiejar import CookieJar
else:
    from cookielib import CookieJar


def ensure_bytes(v, encoding='utf-8'):
    if not isinstance(v, bytes):
        return v.encode(encoding)
    return v

class Kleint(object):

    encoding = getdefaultencoding()
    cookiejar = CookieJar()

    def __init__(self, router, base_url='https://localhost'):
        self.base_url = base_url
        self.inmemory_agent = RequestTraversalAgent(router.resource())
        self.inmemory_agent._realAgent = CookieAgent(
            self.inmemory_agent._realAgent,
            self.cookiejar)

    @defer.inlineCallbacks
    def request(self, method, uri, headers=None, data=None):

        # @TODO Form data producer
        method = ensure_bytes(method)
        uri = ensure_bytes('/'.join([self.base_url, uri.strip('/')]))

        response = yield self.inmemory_agent.request(method, uri, headers)
        content = yield readBody(response)
        response.content = content.decode(self.encoding)
        response.raw_headers = Headers(response.headers)
        response.cookiejar = self.cookiejar
        defer.returnValue(response)

class Headers(object):

    def __init__(self, headers):
        self._headers = headers

    def __getitem__(self, key):
        return self._headers.getRawHeaders(key, [])

    def get(self, key, default=None):
        return self._headers.getRawHeaders(key, default)
