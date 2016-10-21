import attr
from twisted.internet import defer

#@attr.s
class TestClient(object):

    def __init__(self, klein_app, server_name=''):
        self.klein_app = klein_app
        self.klein_map = klein_app.url_map.bind(server_name)
        self.klein_endpoints = klein_app.endpoints

    def resourceFactory(self):
        from twisted.web.test.requesthelper import DummyRequest, DummyChannel
        return DummyRequest(DummyChannel())

    def request(self, method, url_endpoint, body=None, params=None, headers=None):
        fn_name, url_vars = self.klein_map.match(url_endpoint, method=method)
        resource = self.resourceFactory()
        result = self.klein_endpoints[fn_name](self.klein_app._instance, resource, **url_vars)

        if isinstance(result, (defer.Deferred)):
            response = Response(notifyFinish=resource.notifyFinish(), done=False)
            result.addCallback(self.setContent, response)
            result.addCallback(lambda x, y: y.callback(None), response.notifyFinish)
        elif isinstance(result, (str, bytes)):
            resource.notifyFinish().called = True
            response = Response(resource.notifyFinish(), content=result, responseCode=resource.responseCode)
        else:
            raise ValueError('@TODO Validate returned')

        return response

    def setContent(self, content, response):
        if not isinstance(content, (str, bytes)):
            raise ValueError('@TODO')

        response.content = content


@attr.s
class Response(object):
    notifyFinish = attr.ib()
    content = attr.ib(default=None)
    responseCode = attr.ib(default=200)
    done = attr.ib(default=True)


if __name__ == '__main__':
    from klein import Klein
    from twisted.internet import task, reactor

    klein_app = Klein()
    @klein_app.route('/')
    def home(request):
        request.setResponseCode(799)
        return 'hello world'

    @klein_app.route('/inline')
    @defer.inlineCallbacks
    def inline_cb(request):
        yield
        return 'inline hello'

    @klein_app.route('/deferred')
    def testDeferred(request):
        return task.deferLater(reactor, 3, lambda: 'Hey Earth!')

    tester = TestClient(klein_app, 'http://notorious.no')
    response = tester.request('GET', '/')
    print(response.responseCode)

    response = tester.request('GET', '/inline')
    print(response.responseCode)

    def asyncTest():
        response = tester.request('GET', '/deferred')
        response.notifyFinish.addCallback(lambda x, y: y.content, response)
        response.notifyFinish.addCallback(print)
        return response.notifyFinish

    asyncTest()

    reactor.run()
