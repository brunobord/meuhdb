#-*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import logging
from os import unlink, getenv
import random
from tempfile import mkstemp
import time
from unittest import TestCase

from .core import MeuhDb


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
    def test_set_get_dict(self):
        self.db.set('key', {'name': "me"})
        self.assertEquals(self.db.get('key'), {'name': "me"})

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

    def test_autocommit_insert(self):
        key = self.db.insert({'hello': 'world'})
        db = MeuhDb(self.filename)  # reload
        self.assertEquals(db.get(key), {'hello': 'world'})


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


if getenv('RUN_PERFORMANCE_TESTS', False):
    class DatabasePerformanceTest(InMemoryDatabase, TestCase):

        def setUp(self):
            super(DatabasePerformanceTest, self).setUp()
            for x in range(200000):
                self.db.set(x, {'score': random.randrange(1, 100)})

        def test_performances(self):
            t0 = time.clock()
            self.db.filter(score=42)
            t1 = time.clock()
            self.db.create_index('score')
            t2 = time.clock()
            self.db.filter(score=42)
            t3 = time.clock()
            logging.debug(t3 - t2)
            logging.debug(t1 - t0)
            self.assertTrue(t3 - t2 < t1 - t0)
