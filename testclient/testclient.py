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
        if not isinstance(result, (bytes, str, defer.Deferred)):
            raise ValueError('@TODO Validate returned')
        return result, resource

class Response(object):
    pass

if __name__ == '__main__':
    from klein import Klein
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

    tester = TestClient(klein_app, 'http://notorious.no')
    content, resource = tester.request('GET', '/')
    print(resource.responseCode)
    content, resource = tester.request('GET', '/inline')
    print(resource.responseCode)
