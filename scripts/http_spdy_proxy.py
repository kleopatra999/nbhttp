#!/usr/bin/env python

"""
A simple HTTP->SPDY proxy.
"""


import logging
import sys
from urlparse import urlsplit, urlunsplit

try: # run from dist without installation
    sys.path.insert(0, "..")
    from src import Server, run
    from src.spdy_client import SpdyClient
except ImportError:
    from nbhttp import Server, run
    from nbhttp.spdy_client import SpdyClient

logging.basicConfig()
log = logging.getLogger('server')
log.setLevel(logging.DEBUG)

class ProxyClient(SpdyClient):
    read_timeout = 10
    connect_timeout = 15

def proxy_handler(method, uri, req_hdrs, s_res_start, req_pause):
    # can modify method, uri, req_hdrs here
    print uri
    (scheme, authority, path, query, fragid) = urlsplit(uri)
    uri = urlunsplit((scheme, backend_authority, path, query, fragid))
    def c_res_start(version, status, phrase, res_hdrs, res_pause):
        # can modify status, phrase, res_hdrs here
        res_hdrs = [(n.lower(),v.strip()) for (n,v) in res_hdrs if n.lower() not in ['connection', 'content-length', 'transfer-encoding', 'keep-alive']]
        res_body, res_done = s_res_start(status, phrase, res_hdrs, res_pause)
        # can modify res_body here
        return res_body, res_done
    c = ProxyClient(c_res_start)
    req_body, req_done = c.req_start(method, uri, req_hdrs, req_pause)
    # can modify req_body here
    return req_body, req_done


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1])
    backend_authority = sys.argv[2]
    server = Server('', port, proxy_handler)
    run()