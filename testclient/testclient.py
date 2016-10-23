from io import BytesIO

import attr
from twisted.internet import defer
from twisted.test import proto_helpers
from twisted.web.http import unquote
from twisted.web.test.requesthelper import DummyRequest, DummyChannel
from twisted.web import server


#@attr.s
class TestClient(object):

    def __init__(self, klein_app, hostname='', port=8000):
        self.klein_app = klein_app
        self.hostname = hostname.encode('utf-8')
        self.port = port

    def buildRequest(self):
        request = Request(DummyChannel())
        # request = server.Request(proto_helpers.StringTransport())
        request.clientproto = b'HTTP/1.1'
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
        # request.method = method.encode('utf-8')
        request.prepath = []
        request.postpath = list(map(unquote, url_path[1:].split(b'/')))
        request.path = url_path
        request.setHost(self.hostname, self.port)
        # request.content = BytesIO()
        # request.requestReceived(method.encode('utf-8'), url_path, b'HTTP/1.1')

        if content:
            self.setContent(request, content)

        if args:
            self.setArgs(request.args, args)

        if headers:
            self.setHeaders(request, headers)

        def displayContent(result, req):
            print('Catching the finishing of a request must be done before kleinapp.render()')
            print('Result: {0}'.format(req.klein_content))
        request.notifyFinish().addCallback(displayContent, request)

        result = self.klein_app.resource().render(request)

        return request


# class Request(server.Request):
class Request(server.Request):
    def _cleanup(self):
        self.channel.transport.written.seek(0)
        self.klein_content = self.channel.transport.written.read()
        # import pdb;pdb.set_trace()
        super(Request, self)._cleanup()

    def isSecure(self):
        return False

class Response(object):
    notifyFinish = attr.ib()
    content = attr.ib(default=None)
    responseCode = attr.ib(default=200)
    done = attr.ib(default=True)


def main():
    from klein import Klein
    from twisted.internet import task, reactor

    app = Klein()
    @app.route('/path/<path:url_path>')
    def urlPath(request, url_path):
        request.setResponseCode(400)
        return 'hello'

    @app.route('/defer')
    def deferred(request):
        reactor.callLater(5, request.finish)
        return defer.Deferred()

    testClient = TestClient(app)
    req = testClient.fetch('GET', '/path/how/to')
    # req = testClient.fetch('GET', '/defer')


from twisted.internet import task, reactor
main()
# reactor.run()
