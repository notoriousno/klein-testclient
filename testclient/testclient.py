import attr
from twisted.internet import defer
from twisted.test import proto_helpers
from twisted.web.http import unquote
from twisted.web.test.requesthelper import DummyRequest, DummyChannel
from twisted.web.server import Request


#@attr.s
class TestClient(object):

    def __init__(self, klein_app, hostname='', port=8000):
        self.klein_app = klein_app
        self.hostname = hostname.encode('utf-8')
        self.port = port

    def buildRequest(self):
        request = Request(DummyChannel())
        # request = Request(proto_helpers.StringTransport())
        request.setHeader('Accept', '*/*')
        request.setHeader('User-Agent', 'klien')
        return request

    def setArgs(self, request_args, user_args):
        for key, value in user_args.items():
            try:
                key = key.encode('utf-8')
            except:
                pass

            request_args[key] = value if isinstance(value, list) else [value]

    def setContent(self, request, content):
        request.setHeader('content-length', len(content))
        request.content = content

    def setHeaders(self, request, headers):
        for key, val in headers.items():
            request.setHeader(key, val)

    def fetch(self, method, url_endpoint, content=None, args=None, headers=None):
        url_path = url_endpoint.encode('utf-8')

        request = self.buildRequest()
        request.method = method.encode('utf-8')
        request.prepath = []
        request.postpath = list(map(unquote, url_path[1:].split(b'/')))
        request.path = url_path
        request.setHost(self.hostname, self.port)

        if content:
            self.setContent(request, content)

        if args:
            self.setArgs(request.args, args)

        if headers:
            self.setHeaders(request, headers)

        result = self.klein_app.resource().render(request)
        return request


class Response(object):
    notifyFinish = attr.ib()
    content = attr.ib(default=None)
    responseCode = attr.ib(default=200)
    done = attr.ib(default=True)


if __name__ == '__main__':
    from klein import Klein
    from twisted.internet import task, reactor

    app = Klein()
    @app.route('/path/<path:url_path>')
    def urlPath(request, url_path):
        return 'hello'

    @app.route('/defer')
    def deferred(request):
        return defer.Deferred()

    testClient = TestClient(app)
    print(testClient.fetch('', '/path/abc/123').transport.written.read())
    print(testClient.fetch('', '/defer'))
