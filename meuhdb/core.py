#-*- coding: utf-8 -*-
"""
MeuhDB, a database that says "meuh".
"""
from __future__ import unicode_literals
from copy import deepcopy
from functools import wraps
import os
from uuid import uuid4
import warnings

import six

from .backends import DEFAULT_BACKEND, BACKENDS
from .exceptions import BadValueError


def autocommit(f):
    "A decorator to commit to the storage if autocommit is set to True."
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        result = f(self, *args, **kwargs)
        if self._meta.commit_ready():
            self.commit()
        return result
    return wrapper


def intersect(d1, d2):
    """Intersect dictionaries d1 and d2 by key *and* value."""
    return dict((k, d1[k]) for k in d1 if k in d2 and d1[k] == d2[k])


class Meta(object):
    """Meta-information, not directly related to the database itself, but
    the way it's being accessed.
    """
    def __init__(self,
                 path=None, autocommit=False, autocommit_after=None,
                 lazy_indexes=False,
                 backend=DEFAULT_BACKEND):
        self.path = path
        self.lazy_indexes = lazy_indexes

        # Commits / Autocommit
        self.autocommit = autocommit
        self.autocommit_after = autocommit_after
        # Counter
        self.uses_counter = False
        if self.autocommit_after is not None:
            self.uses_counter = True
            self.init_counter = int(self.autocommit_after)
            self.counter = self.init_counter

        if backend not in BACKENDS:
            warnings.warn('{} backend not available, falling '
                          'back to standard json'.format(backend))
            backend = "json"
        self.backend = backend

    @property
    def serializer(self):
        return BACKENDS[self.backend]['dumper']

    @property
    def deserializer(self):
        return BACKENDS[self.backend]['loader']

    def commit_ready(self):
        if self.autocommit:
            return True
        if self.uses_counter:
            self.counter -= 1
            if self.counter:
                return False
            else:
                # counter == 0 -> reset and commit
                self.counter = self.init_counter
                return True


class MeuhDb(object):
    """
    MeuhDb is a key / JSON value store.
    """
    def __init__(self,
                 path=None, autocommit=False, autocommit_after=None,
                 lazy_indexes=False,
                 backend=DEFAULT_BACKEND):
        """
        Options:

        * ``path``: Path to the DB filename,
        * ``autocommit``: If set to True, will save data to the DB at every
          'write' operation,
        * ``autocommit_after``: A numeric value. If set, the database will be
          committed every "n" write operations,
        * ``lazy_indexes``: When set to True, when the DB is written to the
          database, only the definition of the indexes is stored, not the index
          values themselves. This means the DB is faster at writing times, but
          will load slower, because we'll need to rebuild all indexes,
        * ``backend``: Set which backend to use. Will default to the fastest
          backend available, or the stdlib ``json`` module.

        """
        self._meta = Meta(
            path,
            autocommit=autocommit, autocommit_after=autocommit_after,
            lazy_indexes=lazy_indexes,
            backend=backend)
        self.raw = {}
        self.raw['indexes'] = {}
        self.raw['data'] = {}
        self.raw['index_defs'] = {}
        if path:
            if os.path.exists(path):
                try:
                    data = self.deserialize(open(path).read())
                    self.raw.update(data)
                except ValueError:
                    pass
        self._clean_index()

    def serialize(self, obj):
        return self._meta.serializer(obj)

    def deserialize(self, obj):
        return self._meta.deserializer(obj)

    @property
    def data(self):
        "Return raw data."
        return self.raw['data']

    @property
    def indexes(self):
        "Return index data"
        return self.raw['indexes']

    @property
    def index_defs(self):
        "Return the index definitions"
        return self.raw['index_defs']

    def exists(self, key):
        "Return True if key is in the keystore."
        return key in self.data

    def get(self, key):
        """
        Return value of 'key' if it's in the database.
        Raise KeyError if not.
        """
        return self.data[key]

    @autocommit
    def set(self, key, value):
        "Set value to the key store."
        # if key already in data, update indexes
        if not isinstance(value, dict):
            raise BadValueError(
                'The value {} is incorrect.'
                ' Values should be strings'.format(value))
        _value = deepcopy(value)
        if key in self.data:
            self.delete_from_index(key)
        self.data[key] = _value
        self.update_index(key, _value)

    @autocommit
    def insert(self, value):
        "Insert value in the keystore. Return the UUID key."
        key = str(uuid4())
        self.set(key, value)
        return key

    @autocommit
    def delete(self, key):
        "Delete a `key from the keystore."
        if key in self.data:
            self.delete_from_index(key)
        del self.data[key]

    @autocommit
    def update(self, key, value):
        """Update a `key` in the keystore.
        If the key is non-existent, it's being created
        """
        if not isinstance(value, dict):
            raise BadValueError(
                'The value {} is incorrect.'
                ' Values should be strings'.format(value))
        if key in self.data:
            v = self.get(key)
            v.update(value)
        else:
            v = value
        self.set(key, v)

    @property
    def lazy_indexes(self):
        return set([
            idx_name for (idx_name, value) in self.raw['index_defs'].items()
            if value['type'] == 'lazy'
        ])

    def commit(self):
        "Commit data to the storage."
        if self._meta.path:
            with open(self._meta.path, 'wb') as fd:
                raw = deepcopy(self.raw)
                # LAZY INDEX PROCESSING
                # Save indexes only if not lazy
                lazy_indexes = self.lazy_indexes  # Keep this list safe
                if not self._meta.lazy_indexes:
                    # Remove indexes if needed
                    for idx_name in lazy_indexes:
                        del raw['indexes'][idx_name]
                    for index_name, values in raw['indexes'].items():
                        for value, keys in values.items():
                            raw['indexes'][index_name][value] = list(keys)
                # don't store indexes if not needed
                if not raw['indexes'] or self._meta.lazy_indexes:
                    del raw['indexes']
                try:
                    fd.write(six.u(self.serialize(raw)))
                except TypeError:
                    fd.write(six.b(self.serialize(raw)))

    def all(self):
        "Retrieve the data from the keystore"
        return self.data

    def keys_to_values(self, keys):
        "Return the items in the keystore with keys in `keys`."
        return dict((k, v) for k, v in self.data.items() if k in keys)

    def filter_key(self, key, value):
        "Search keys whose values match with the searched values"
        searched = {key: value}
        return set([k for k, v in self.data.items() if
                    intersect(searched, v) == searched])

    def filter(self, **kwargs):
        """
        Filter data according to the given arguments.
        """
        self._used_index = False
        keys = set(self.data.keys())
        for key_filter, v_filter in kwargs.items():
            if key_filter in self.indexes:
                self._used_index = True
                if v_filter not in self.indexes[key_filter]:
                    keys = set([])
                else:
                    keys = keys.intersection(
                        self.indexes[key_filter][v_filter])
            else:
                keys = keys.intersection(self.filter_key(key_filter, v_filter))
        return self.keys_to_values(keys)

    def delete_from_index(self, key):
        "Delete references from the index of the key old value(s)."
        old_value = self.data[key]
        keys = set(old_value.keys()).intersection(self.indexes.keys())
        for index_name in keys:
            if old_value[index_name] in self.indexes[index_name]:
                del self.indexes[index_name][old_value[index_name]]

    def update_index(self, key, value):
        "Update the index with the new key/values."
        for k, v in value.items():
            if k in self.indexes:
                # A non-string index value switches it into a lazy one.
                if not isinstance(v, six.string_types):
                    self.index_defs[k]['type'] = 'lazy'
                if v not in self.indexes[k]:
                    self.indexes[k][v] = set([])
                self.indexes[k][v].add(key)

    @autocommit
    def create_index(self, name, recreate=False, _type='default'):
        """
        Create an index.
        If recreate is True, recreate even if already there.
        """
        if name not in self.indexes or recreate:
            self.build_index(name, _type)

    @autocommit
    def build_index(self, idx_name, _type='default'):
        "Build the index related to the `name`."
        indexes = {}
        has_non_string_values = False
        for key, item in self.data.items():
            if idx_name in item:
                value = item[idx_name]
                # A non-string index value switches it into a lazy one.
                if not isinstance(value, six.string_types):
                    has_non_string_values = True
                if value not in indexes:
                    indexes[value] = set([])
                indexes[value].add(key)
        self.indexes[idx_name] = indexes
        if self._meta.lazy_indexes or has_non_string_values:
            # Every index is lazy
            _type = 'lazy'
        self.index_defs[idx_name] = {'type': _type}

    @autocommit
    def remove_index(self, idx_name):
        "Remove an index from the database."
        if idx_name in self.indexes:
            del self.indexes[idx_name]

    def _clean_index(self):
        "Clean index values after loading."
        for idx_name, idx_def in self.index_defs.items():
            if idx_def['type'] == 'lazy':
                self.build_index(idx_name)
        for index_name, values in self.indexes.items():
            for value in values:
                if not isinstance(values[value], set):
                    values[value] = set(values[value])
