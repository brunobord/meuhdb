#-*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from os import unlink
from tempfile import mkstemp
from unittest import TestCase
import logging

from .core import MeuhDb
from .exceptions import BadValueError

logging.captureWarnings(True)


class InMemoryDatabase(TestCase):
    def setUp(self):
        self.db = MeuhDb()  # in-memory DB


class InMemoryDatabaseData(InMemoryDatabase):
    def setUp(self):
        super(InMemoryDatabaseData, self).setUp()
        self.db.set('one', {'name': 'Alice', 'good': True, 'chief': True})
        self.db.set('two', {'name': 'Bob', 'good': True})
        self.db.set('three', {'name': 'Carl', 'good': False})


class DatabaseTest(InMemoryDatabase, TestCase):
    def test_set_get_simple(self):
        self.db.set('key', {'name': "me"})
        self.assertEquals(self.db.get('key'), {'name': "me"})

    def test_set_copy(self):
        value = {'a': 'abcd'}
        self.db.set('key', value)
        value.update({'b': 1234})
        # An update on the initial value shouldn't re-write the value stored
        self.assertEquals(self.db.get('key'), {'a': 'abcd'})

    def test_delete(self):
        self.db.set('key', {'name': "me"})
        self.assertTrue(self.db.exists('key'))
        self.db.delete('key')
        self.assertFalse(self.db.exists('key'))

    def test_update(self):
        self.db.set('key', {'name': "me"})
        self.assertEquals(self.db.get('key'), {'name': "me"})
        self.db.update('key', {'thing': 'stuff'})
        self.assertEquals(self.db.get('key'), {'name': "me", 'thing': 'stuff'})
        # updating an non-existing key means creating it
        self.db.update('other', {'hello': 'world'})
        self.assertEquals(self.db.get('other'), {'hello': 'world'})

    def test_insert(self):
        key = self.db.insert({'hello': 'world'})
        self.assertEquals(self.db.get(key), {'hello': 'world'})

    def test_bad_value(self):
        self.assertRaises(BadValueError, self.db.set, 'a', '1')
        self.assertRaises(BadValueError, self.db.set, 'a', 123)
        self.assertRaises(BadValueError, self.db.set, 'a', None)
        self.assertRaises(BadValueError, self.db.insert, '1')
        self.assertRaises(BadValueError, self.db.insert, 123)
        self.assertRaises(BadValueError, self.db.insert, None)

    def test_bad_value_update(self):
        self.db.set('key', {'name': 'me'})
        self.assertRaises(BadValueError, self.db.update, 'key', '1')
        self.assertRaises(BadValueError, self.db.update, 'key', 123)
        self.assertRaises(BadValueError, self.db.update, 'key', None)


class DatabaseStoreTest(TestCase):
    def setUp(self):
        self.fd, self.filename = mkstemp()
        self.db = MeuhDb(self.filename)

    def tearDown(self):
        unlink(self.filename)

    def test_commit(self):
        self.db.set('key', {'hello': 'world'})
        db = MeuhDb(self.filename)  # reload
        self.assertFalse(db.exists("key"))
        self.db.commit()
        db = MeuhDb(self.filename)  # reload
        self.assertTrue(db.exists("key"))
        self.assertEquals(db.get('key'), {'hello': 'world'})

    def test_commit_delete(self):
        self.db.set('key', {'hello': 'world'})
        self.db.commit()
        self.db.delete('key')
        db = MeuhDb(self.filename)  # reload
        self.assertEquals(db.get("key"), {'hello': 'world'})
        self.db.commit()
        db = MeuhDb(self.filename)  # reload
        self.assertFalse(db.exists('key'))


class DatabaseStoreChangeBackendTest(TestCase):
    def setUp(self):
        self.fd, self.filename = mkstemp()
        self.db = MeuhDb(self.filename, backend='json')

    def tearDown(self):
        unlink(self.filename)

    def test_backend(self):
        self.assertEquals(self.db._meta.backend, 'json')
        self.assertEquals(self.db._meta.serializer, json.dumps)
        self.assertEquals(self.db._meta.deserializer, json.loads)

    def test_missing_backend(self):
        db = MeuhDb(backend='missing-json')
        self.assertEquals(db._meta.backend, 'json')
        self.assertEquals(self.db._meta.serializer, json.dumps)
        self.assertEquals(self.db._meta.deserializer, json.loads)


class DatabaseStoreAutocommitTest(TestCase):
    def setUp(self):
        self.fd, self.filename = None, 'test.json'
        self.db = MeuhDb(self.filename, autocommit=True)

    def tearDown(self):
        unlink(self.filename)

    def test_autocommit_set(self):
        self.db.set('key', {'hello': 'world'})
        db = MeuhDb(self.filename)  # reload
        self.assertEquals(db.get('key'), {'hello': 'world'})

    def test_autocommit_delete(self):
        self.db.set('key', {'hello': 'world'})
        self.db.delete('key')
        db = MeuhDb(self.filename)  # reload
        self.assertFalse(db.exists('key'))

    def test_autocommit_create_index(self):
        self.db.set('1', {'name': 'Alice'})
        self.db.set('2', {'name': 'Bob'})
        self.db.create_index('name')
        db = MeuhDb(self.filename)  # reload
        self.assertTrue(db.exists('1'))
        self.assertTrue(db.exists('2'))
        self.assertTrue('name' in db.indexes)
        index = db.indexes['name']
        self.assertEquals(index['Alice'], set(['1']))
        self.assertEquals(index['Bob'], set(['2']))

    def test_autocommit_delete_index(self):
        self.db.create_index('name')
        self.db.remove_index('name')
        db = MeuhDb(self.filename)  # reload
        self.assertFalse('name' in db.indexes)

    def test_autocommit_update(self):
        self.db.set('key', {'name': "me"})
        self.assertEquals(self.db.get('key'), {'name': "me"})
        self.db.update('key', {'thing': 'stuff'})
        db = MeuhDb(self.filename)  # reload
        self.assertEquals(db.get('key'), {'name': "me", 'thing': 'stuff'})
        # updating an non-existing key means creating it
        self.db.update('other', {'hello': 'world'})
        db = MeuhDb(self.filename)  # reload
        self.assertEquals(db.get('other'), {'hello': 'world'})

    def test_autocommit_update_name_index(self):
        self.db.set('1', {'name': 'Alice'})
        self.db.set('2', {'flag': True})
        self.db.create_index('name')
        self.db.update('2', {'name': 'Bob'})
        db = MeuhDb(self.filename)  # reload
        self.assertTrue('name' in db.indexes)
        index = db.indexes['name']
        self.assertEquals(index['Alice'], set(['1']))
        self.assertEquals(index['Bob'], set(['2']))

    def test_autocommit_ensure_set(self):
        self.db.create_index('name')
        self.db.set('1', {'name': 'Alice'})
        self.db.set('2', {'name': 'Alice'})
        db = MeuhDb(self.filename)  # reload
        self.assertTrue('name' in db.indexes)
        index = db.indexes['name']
        self.assertEquals(index['Alice'], set(['1', '2']))

    def test_autocommit_insert(self):
        key = self.db.insert({'hello': 'world'})
        db = MeuhDb(self.filename)  # reload
        self.assertEquals(db.get(key), {'hello': 'world'})


class DatabaseStoreAutocommitAfterTest(TestCase):
    def setUp(self):
        self.fd, self.filename = None, 'test.json'
        self.db = MeuhDb(self.filename, autocommit_after=3)
        self.db.commit()  # file is created

    def tearDown(self):
        unlink(self.filename)

    def test_autocommit_after(self):
        self.db.set('key', {'name': 'Alice'})
        db = MeuhDb(self.filename)  # reload
        self.assertFalse(db.exists('key'))
        self.db.set('key', {'name': 'Alice 2'})
        db = MeuhDb(self.filename)  # reload
        self.assertFalse(db.exists('key'))
        self.db.set('key', {'name': 'Alice 3'})
        db = MeuhDb(self.filename)  # reload
        self.assertTrue(db.exists('key'))

    def test_autocommit_after_other_command(self):
        self.db.set('key1', {'name': 'Alice'})
        self.db.set('key2', {'name': 'Alice'})
        self.db.set('key3', {'name': 'Alice'})
        # Should be committed
        self.db.delete('key3')
        db = MeuhDb(self.filename)  # reload
        self.assertTrue(db.exists('key3'))


class DatabaseFilter(InMemoryDatabaseData, TestCase):

    def test_all(self):
        result = self.db.all()
        self.assertTrue('one' in result)
        self.assertTrue('two' in result)
        self.assertTrue('three' in result)

    def test_filter(self):
        result = self.db.filter(good=True)
        self.assertFalse(self.db._used_index)
        self.assertTrue('one' in result)
        self.assertTrue('two' in result)
        self.assertFalse('three' in result)

    def test_filter_false(self):
        result = self.db.filter(good=False)
        self.assertFalse(self.db._used_index)
        self.assertFalse('one' in result)
        self.assertFalse('two' in result)
        self.assertTrue('three' in result)

    def test_filter_missing(self):
        result = self.db.filter(missing=True)
        self.assertFalse(self.db._used_index)
        self.assertFalse(result)  # empty dict
        result = self.db.filter(name='Bruno')
        self.assertFalse(self.db._used_index)
        self.assertFalse(result)  # empty dict

    def test_filter_multiple(self):
        result = self.db.filter(good=True, name='Bob')
        self.assertFalse(self.db._used_index)
        self.assertFalse('one' in result)
        self.assertTrue('two' in result)
        self.assertFalse('three' in result)


class DatabaseIndexTest(InMemoryDatabaseData, TestCase):

    def test_create_index_name(self):
        self.db.create_index('name')
        self.assertTrue('name' in self.db.indexes)
        index = self.db.indexes['name']
        self.assertTrue('Alice' in index)
        self.assertTrue('Bob' in index)
        self.assertTrue('Carl' in index)

    def test_update_index_name(self):
        self.db.create_index('name')
        self.db.set('four', {'name': 'John'})
        index = self.db.indexes['name']
        self.assertTrue('John' in index)

    def test_delete_index_name(self):
        self.db.create_index('name')
        self.db.delete('one')
        index = self.db.indexes['name']
        self.assertFalse('Alice' in index)
        self.assertTrue('Bob' in index)
        self.assertTrue('Carl' in index)

    def test_create_index_good(self):
        self.db.create_index('good')
        self.assertTrue('good' in self.db.indexes)
        index = self.db.indexes['good']
        self.assertTrue(True in index)
        self.assertTrue(False in index)
        self.assertEquals(index[True], set(['one', 'two']))
        self.assertEquals(index[False], set(['three']))

    def test_create_index_chief(self):
        self.db.create_index('chief')
        self.assertTrue('chief' in self.db.indexes)
        index = self.db.indexes['chief']
        self.assertTrue(True in index)
        self.assertFalse(False in index)
        self.assertEquals(index[True], set(['one']))

    def test_search_index(self):
        self.db.create_index('name')
        result = self.db.filter(name='Alice')
        self.assertTrue(self.db._used_index)
        self.assertTrue('one' in result)
        self.assertFalse('two' in result)
        self.assertFalse('three' in result)

    def test_search_index_empty(self):
        self.db.create_index('name')
        result = self.db.filter(name='Nobody')
        self.assertTrue(self.db._used_index)
        self.assertFalse(result)

    def test_remove_index_name(self):
        self.db.create_index('name')
        self.assertTrue('name' in self.db.indexes)
        self.db.remove_index('name')
        self.assertFalse('name' in self.db.indexes)
