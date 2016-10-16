# Description

A helper class to aide in testing applications based on ``klien``.


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
