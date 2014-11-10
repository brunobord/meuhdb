import json

from meuhdb.core import MeuhDb
from meuhdb.tests import InMemoryDatabase, InMemoryDatabaseData
from meuhdb.tests import TempStorageDatabase


class DatabaseIndexDataTest(InMemoryDatabaseData):

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


class DatabaseStoreLazyIndexTest(TempStorageDatabase):

    options = {'lazy_indexes': True}

    def tearDown(self):
        self.db.commit()
        super(DatabaseStoreLazyIndexTest, self).tearDown()

    def test_indexes(self):
        self.db.create_index('name')
        self.db.set('key', {'name': 'Alice'})
        self.assertTrue('name' in self.db.indexes)
        index = self.db.indexes['name']
        self.assertTrue('Alice' in index)
        self.assertEquals(index['Alice'], set(['key']))
        self.db.commit()
        loaded_data = json.load(open(self.filename))
        self.assertNotIn('indexes', loaded_data)
        self.assertIn('lazy_indexes', loaded_data)
        self.assertEquals(loaded_data['lazy_indexes'], ['name'])
        # load data out of the lazy file
        db = MeuhDb(self.filename)
        self.assertEquals(db.data, {'key': {'name': 'Alice'}})
        self.assertEquals(db.indexes, {'name': {'Alice': set(['key'])}})


class DatabaseIndexDefsTest(InMemoryDatabase):

    def test_create_index(self):
        self.db.create_index('name')
        self.assertIn('name', self.db.index_defs)
        idx = self.db.index_defs['name']
        self.assertEquals(idx['type'], 'default')
        self.assertEquals(self.db.lazy_indexes, set([]))

    def test_create_lazy(self):
        self.db.create_index('name', _type='lazy')
        self.db.create_index('stuff')
        self.assertIn('name', self.db.index_defs)
        idx = self.db.index_defs['name']
        self.assertEquals(idx['type'], 'lazy')
        self.assertEquals(self.db.lazy_indexes, set(['name']))


class DatabaseIndexDefsLazyTest(TempStorageDatabase):

    options = {'lazy_indexes': True}

    def test_lazy_indexes(self):
        self.db.create_index('name')  # should be default
        self.db.create_index('stuff', _type="default")
        self.db.create_index('thing', _type="lazy")
        # But it's a lazy connection, everything's lazy
        self.assertIn('name', self.db.index_defs)
        idx = self.db.index_defs['name']
        self.assertEquals(idx['type'], 'lazy')
        self.assertEquals(
            self.db.lazy_indexes, set(['name', 'stuff', 'thing']))
