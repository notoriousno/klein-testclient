from klein import Klein
from kleint import Kleint
from twisted.internet import reactor, defer
from twisted.trial.unittest import TestCase

class KleintTest(TestCase):

    router = Klein()

    @router.route('/string', methods=['GET'])
    def return_string(request):
        return 'hello world'

    @router.route('/bytes')
    def return_bytes(request):
        return b'hello world'

    @router.route('/deferred', methods=['POST'])
    def return_deferred(request):
        d = defer.Deferred()
        reactor.callLater(0, d.callback, 'hello world')
        return d

    @router.route('/headers')
    def setting_headers(request):
        request.setHeader('Accept-Charset', 'utf-8')
        request.setHeader('Accept-Language', 'en-US')

    @router.route('/status')
    def set_status(request):
        request.setResponseCode(418, b'teapot')

    test_client = Kleint(router)


    def test_test(self):
        response = self.test_client.request('GET', '/string')
        @response.addCallback
        def verify(resp):
            self.assertEquals(resp.content, 'hello world')
            self.assertEquals(resp.code, 200)

    def test_bytes(self):
        response = self.test_client.request('GET', '/bytes')
        @response.addCallback
        def verify(resp):
            assert resp.content == 'hello world'
            assert resp.code == 200

    def test_deferred(self):
        response = self.test_client.request('POST', '/deferred')
        @response.addCallback
        def verify(resp):
            self.assertEquals(resp.content, 'hello world')

    def test_setting_headers(self):
        response = self.test_client.request('GET', '/headers')
        @response.addCallback
        def verify(resp):
            encoding = resp.raw_headers['accept-charset'][0]
            self.assertEquals(encoding, 'utf-8')
            lang = resp.raw_headers.get('accept-language')[0]
            self.assertEquals(lang, 'en-US')

    def test_status_code(self):
        response = self.test_client.request('GET', '/status')
        @response.addCallback
        def verify(resp):
            self.assertEquals(resp.code, 418)
            self.assertEquals(resp.phrase, b'teapot')

    def test_unhandled_method(self):
        response = self.test_client.request('POST', '/string')
        @response.addCallback
        def verify(resp):
            self.assertEquals(resp.code, 405)

    def test_unknown_route(self):
        response = self.test_client.request('GET', '/doesnotexist')
        @response.addCallback
        def verify(resp):
            self.assertEquals(resp.code, 404)

    def test_branched(self):
        router = Klein()
        branch = Klein()

        @router.route('/branch', branch=True)
        def branched_resource(request):
            return branch.resource()

        @branch.route('/twig')
        def twig_resource(request):
            return 'hello world'

        test_client = Kleint(router)
        response = test_client.request('GET', '/branch/twig')
        @response.addCallback
        def verify(resp):
            self.assertEquals(resp.content, 'hello world')
