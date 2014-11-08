import json

BACKENDS = {
    'json': {
        'dumper': json.dumps,
        'loader': json.loads,
    }
}
DEFAULT_BACKEND = 'json'

try:
    import simplejson
    BACKENDS.update({
        'simplejson': {
            'dumper': simplejson.dumps,
            'loader': simplejson.loads,
        }
    })
    DEFAULT_BACKEND = 'simplejson'
except ImportError:
    pass

try:
    import yajl
    BACKENDS.update({
        'yajl': {
            'dumper': yajl.dumps,
            'loader': yajl.loads,
        }
    })
    DEFAULT_BACKEND = 'yajl'
except ImportError:
    pass

try:
    import jsonlib
    BACKENDS.update({
        'jsonlib': {
            'dumper': jsonlib.dumps,
            'loader': jsonlib.loads,
        }
    })
    DEFAULT_BACKEND = 'jsonlib'
except ImportError:
    pass

try:
    import ujson
    BACKENDS.update({
        'ujson': {
            'dumper': ujson.dumps,
            'loader': ujson.loads,
        }
    })
    DEFAULT_BACKEND = 'ujson'
except ImportError:
    pass
