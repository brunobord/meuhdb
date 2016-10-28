from meuhdb.exceptions import BadValueError
from meuhdb.tests import InMemoryDatabase, InMemoryDatabaseData


class DatabaseTest(InMemoryDatabase):
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

    def test_del_key(self):
        self.db.set('key', {'name': 'me', 'age': 42})
        # missing key in record, shouldn't trigger an error
        self.db.del_key('key', 'missing')
        self.assertEquals(self.db.get('key'), {'name': 'me', 'age': 42})
        self.db.del_key('key', 'name')
        self.assertEquals(self.db.get('key'), {'age': 42})


class DatabaseFilter(InMemoryDatabaseData):

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

    def test_filter_keys(self):
        result1 = self.db.filter_keys(good=True)
        self.assertTrue('one' in result1)
        self.assertTrue('two' in result1)
        self.assertFalse('three' in result1)
        result2 = self.db.filter_keys(name='Carl')
        self.assertFalse('one' in result2)
        self.assertFalse('two' in result2)
        self.assertTrue('three' in result2)

    def test_and(self):
        result1 = self.db.filter_keys(good=True)
        result2 = self.db.filter_keys(name='Carl')
        result = result1 & result2
        self.assertFalse('one' in result)
        self.assertFalse('two' in result)
        self.assertFalse('three' in result)

    def test_or(self):
        result1 = self.db.filter_keys(good=True)
        result2 = self.db.filter_keys(name='Carl')
        result = result1 | result2
        self.assertTrue('one' in result)
        self.assertTrue('two' in result)
        self.assertTrue('three' in result)
