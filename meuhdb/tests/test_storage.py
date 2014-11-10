import json
import logging

from meuhdb.core import MeuhDb
from meuhdb.tests import TempStorageDatabase

logging.captureWarnings(True)


class DatabaseCommitTest(TempStorageDatabase):
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


class DatabaseStoreChangeBackendTest(TempStorageDatabase):

    options = {'backend': 'json'}

    def test_backend(self):
        self.assertEquals(self.db._meta.backend, 'json')
        self.assertEquals(self.db._meta.serializer, json.dumps)
        self.assertEquals(self.db._meta.deserializer, json.loads)

    def test_missing_backend(self):
        db = MeuhDb(backend='missing-json')
        self.assertEquals(db._meta.backend, 'json')
        self.assertEquals(self.db._meta.serializer, json.dumps)
        self.assertEquals(self.db._meta.deserializer, json.loads)


class DatabaseStoreAutocommitTest(TempStorageDatabase):

    options = {'autocommit': True}

    def test_set(self):
        self.db.set('key', {'hello': 'world'})
        db = MeuhDb(self.filename)  # reload
        self.assertEquals(db.get('key'), {'hello': 'world'})

    def test_delete(self):
        self.db.set('key', {'hello': 'world'})
        self.db.delete('key')
        db = MeuhDb(self.filename)  # reload
        self.assertFalse(db.exists('key'))

    def test_create_index(self):
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

    def test_delete_index(self):
        self.db.create_index('name')
        self.db.remove_index('name')
        db = MeuhDb(self.filename)  # reload
        self.assertFalse('name' in db.indexes)

    def test_update(self):
        self.db.set('key', {'name': "me"})
        self.assertEquals(self.db.get('key'), {'name': "me"})
        self.db.update('key', {'thing': 'stuff'})
        db = MeuhDb(self.filename)  # reload
        self.assertEquals(db.get('key'), {'name': "me", 'thing': 'stuff'})
        # updating an non-existing key means creating it
        self.db.update('other', {'hello': 'world'})
        db = MeuhDb(self.filename)  # reload
        self.assertEquals(db.get('other'), {'hello': 'world'})

    def test_update_name_index(self):
        self.db.set('1', {'name': 'Alice'})
        self.db.set('2', {'flag': True})
        self.db.create_index('name')
        self.db.update('2', {'name': 'Bob'})
        db = MeuhDb(self.filename)  # reload
        self.assertTrue('name' in db.indexes)
        index = db.indexes['name']
        self.assertEquals(index['Alice'], set(['1']))
        self.assertEquals(index['Bob'], set(['2']))

    def test_ensure_set(self):
        self.db.create_index('name')
        self.db.set('1', {'name': 'Alice'})
        self.db.set('2', {'name': 'Alice'})
        db = MeuhDb(self.filename)  # reload
        self.assertTrue('name' in db.indexes)
        index = db.indexes['name']
        self.assertEquals(index['Alice'], set(['1', '2']))

    def test_insert(self):
        key = self.db.insert({'hello': 'world'})
        db = MeuhDb(self.filename)  # reload
        self.assertEquals(db.get(key), {'hello': 'world'})


class DatabaseStoreAutocommitAfterTest(TempStorageDatabase):

    options = {'autocommit_after': 3}

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
