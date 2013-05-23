from functools import wraps
try:
    # PY2
    from urllib import quote_plus
except ImportError:
    # PY3
    from urllib.parse import quote_plus

from .transport import Transport
from .exceptions import NotFoundError

def _normalize_hosts(hosts):
    """
    Helper function to transform hosts argument to
    :class:`~elasticsearch.Elasticsearch` to a list of dicts.
    """
    # if hosts are empty, just defer to defaults down the line
    if hosts is None:
        return [{}]

    out = []
    # normalize hosts to dicts
    for i, host in enumerate(hosts):
        if isinstance(host, (type(''), type(u''))):
            h = {"host": host}
            if ':' in host:
                # TODO: detect auth urls
                host, port = host.rsplit(':', 1)
                if port.isdigit():
                    port = int(port)
                    h = {"host": host, "port": port}
            out.append(h)
        else:
            out.append(host)
    return out

def _normalize_list(list_or_string):
    """
    for index and type arguments in url, identify if it's a string or a
    sequence and produce a working representation (comma separated string).
    """
    if isinstance(list_or_string, (type(''), type(u''))):
        return quote_plus(list_or_string)
    return quote_plus(','.join(list_or_string))


# parameters that apply to all methods
GLOBAL_PARAMS = ('pretty', )

def query_params(*es_query_params):
    """
    Decorator that pops all accepted parameters from method's kwargs and puts
    them in the params argument.
    """
    def _wrapper(func):
        @wraps(func)
        def _wrapped(*args, **kwargs):
            params = kwargs.pop('params', {})
            for p in es_query_params + GLOBAL_PARAMS:
                if p in kwargs:
                    params[p] = kwargs.pop(p)
            return func(*args, params=params, **kwargs)
        return _wrapped
    return _wrapper


class Elasticsearch(object):
    """
    Elasticsearch low-level client. Provides a straightforward mapping from
    Python to ES REST endpoints.
    """
    def __init__(self, hosts=None, **kwargs):
        """
        :arg hosts: list of nodes we should connect to. Node should be a
            dictionary ({"host": "localhost", "port": 9200}), the entire dictionary
            will be passed to the :class:`~elasticsearch.Connection` class as
            kwargs, or a string in the format ot ``host[:port]`` which will be
            translated to a dictionary automatically.  If no value is given the
            :class:`~elasticsearch.Connection` class defaults will be used.

        :arg kwargs: any additional arguments will be passed on to the
            :class:`~elasticsearch.Transport` class and, subsequently, to the
            :class:`~elasticsearch.Connection` instances.
        """
        self.transport = Transport(_normalize_hosts(hosts), **kwargs)

    @query_params('timeout')
    def create_index(self, index, body=None, params=None):
        status, data = self.transport.perform_request('PUT', '/%s' % quote_plus(index), params=params, body=body)
        return data

    @query_params()
    def delete_index(self, index='', ignore_missing=False, params=None):
        index = _normalize_list(index)
        try:
            status, data = self.transport.perform_request('DELETE', '/%s' % quote_plus(index), params=params)
        except NotFoundError:
            if ignore_missing:
                return
            raise
        return data

    @query_params()
    def refresh(self, index=None, params=None):
        url = '/_refresh'
        if index:
            url = '/%s/_refresh' % _normalize_list(index)
        status, data = self.transport.perform_request('POST', url, params=params)
        return data

    @query_params('consistency', 'op_type', 'parent', 'percolate', 'refresh', 'replication', 'routing', 'timeout', 'timestamp', 'ttl', 'version', 'version_type')
    def index(self, index, doc_type, body, id=None, params=None):
        status, data = self.transport.perform_request('PUT', '/%s/%s/%s' % map(quote_plus, (index, doc_type, str(id))), params=params, body=body)
        return data

    @query_params('fields', 'parent', 'preference', 'realtime', 'refresh', 'routing', 'timeout')
    def get(self, index, id, doc_type=u'_all', params=None):
        status, data = self.transport.perform_request('GET', '/%s/%s/%s' % map(quote_plus, (index, doc_type, str(id))), params=params)
        return data

    @query_params('explain', 'fields', 'from', 'ignore_indices', 'indices_boost', 'preference', 'routing', 'search_type', 'size', 'sort', 'source', 'stats', 'timeout', 'version')
    def search(self, query, index='_all', doc_type=None, params=None):
        body = None
        if isinstance(query, (type(''), type(u''))):
            params['q'] = query
        else:
            body = query

        url = '/%s/%s/_search' % (_normalize_list(index), _normalize_list(doc_type)) if doc_type else '/%s/_search' % _normalize_list(index)

        status, data = self.transport.perform_request('GET', url, params=params, body=body)
        return data


