#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import copy

from twisted.web import http, resource

#: CORS - HTTP headers the client may use
CORS_ALLOWED_CLIENT_HEADERS = [
    'Content-Type',
]

#: CORS - HTTP methods the client may use
CORS_ALLOWED_METHODS_DEFAULT = ['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS']

#: CORS - default origin header value
CORS_DEFAULT_ALLOW_ORIGIN = '*'

#: CORS - HTTP headers the server will send as part of OPTIONS response
CORS_DEFAULT = {
    'Access-Control-Allow-Origin': CORS_DEFAULT_ALLOW_ORIGIN,
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Max-Age': '86400',
    'Access-Control-Allow-Methods': ','.join(CORS_ALLOWED_METHODS_DEFAULT),
    'Access-Control-Allow-Headers': ', '.join(CORS_ALLOWED_CLIENT_HEADERS)
}


def json_response(request, data, indent=1):
    """
    Create a JSON representation for *data* and set HTTP headers indicating
    that JSON encoded data is returned.

    Args:
        request (twisted.web.server.Request): HTTP request object
        data: response content
        indent: indentation level or None
    Returns:
        JSON representation of *data* with appropriate HTTP headers
    """
    request.setHeader("content-type", "application/json; charset=utf-8")
    return json.dumps(data, indent=indent)


class RESTControllerSkeleton(resource.Resource):
    isLeaf = True

    def __init__(self, *args, **kwargs):
        resource.Resource.__init__(self)
        self._cors_header = copy.copy(CORS_DEFAULT)
        http_verbs = []
        self.session = kwargs.get("session")

        for verb in CORS_ALLOWED_METHODS_DEFAULT:
            method_name = 'render_{:s}'.format(verb)
            if hasattr(self, method_name):
                http_verbs.append(verb)
        self._cors_header['Access-Control-Allow-Methods'] = ','.join(http_verbs)

    def render_OPTIONS(self, request):
        """
        Render response for an HTTP OPTIONS request.

        Args:
            request (twisted.web.server.Request): HTTP request object
        Returns:
            HTTP response with headers
        """
        for key in self._cors_header:
            request.setHeader(key, self._cors_header[key])

        return ''

    def render_GET(self, request):
        """
        HTTP GET implementation.

        Args:
            request (twisted.web.server.Request): HTTP request object
        Returns:
            HTTP response with headers
        """
        request.setHeader(
            'Access-Control-Allow-Origin', CORS_DEFAULT_ALLOW_ORIGIN)

        data = {
            "_controller": self.__class__.__name__,
            "request_postpath": request.postpath,
            "method": request.method,
            "request_path": request.path,
        }

        return json_response(request, data)

    def render_POST(self, request):
        """
        HTTP POST implementation.

        Args:
            request (twisted.web.server.Request): HTTP request object
        Returns:
            HTTP response with headers
        """
        request.setHeader(
            'Access-Control-Allow-Origin', CORS_DEFAULT_ALLOW_ORIGIN)

        data = {
            "_controller": self.__class__.__name__,
            "request_postpath": request.postpath,
            "method": request.method,
            "request_path": request.path,
        }

        return json_response(request, data)


class SimpleRootController(resource.Resource):
    isLeaf = False

    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild("demo", RESTControllerSkeleton())
        self.putChild("", RESTControllerSkeleton())

if __name__ == '__main__':
    from twisted.web.server import Site
    from twisted.internet import reactor

    root = SimpleRootController()
    # root.putChild("configuration", RESTControllerSkeleton())
    factory_r = Site(root)

    reactor.listenTCP(19999, factory_r)
    reactor.run()
