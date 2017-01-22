# Description

A helper class to aide in testing applications based on ``klien``.
It's quite difficult for those who are new to Klein or Twisted to comprehend the testing process.
`Kleint` (pronounced like *client*) will hopefully bridge that gap and ease developers into more complicated/flexible methods.


# Example

``` python
#----- Klein Application -----
from klein import Klein
app = Klein()

@app.route('/hello')
def hello(request):
    request.setResponseCode(418)
    request.setHeader('Content-Type', 'application/json')
    return 'hello world'

#----- Test Application -----
from kleint import Kleint
tester = Kleint(app)

response = tester.request('GET', '/hello')
@response.addCallback(resp)
def verify(resp):
    assert resp.content == 'hello world'
    assert resp.code == 418
    assert resp.raw_headers['content-type'][0] == 'application/json'
```


# Design

Strongly influenced by similar helpers from Tornado and Flask projects. Klein uses werkzeug which makes it rather easy to make a simple test client.

``` python
klein_app = Klein()
# ...
url_map = klein_app.url_map.bind('', '/')
fn_name, url_vars = url_map.match('/some/endpoint')

request = genDummyResource()
app._endpoints[fn_name](instance, request, **url_vars)
# ...

return request # with updated headers and what not
```
