from unittest import TestCase
from os import unlink
from tempfile import mkstemp

from meuhdb.core import MeuhDb


class InMemoryDatabase(TestCase):
    def setUp(self):
        self.db = MeuhDb()  # in-memory DB


class InMemoryDatabaseData(InMemoryDatabase):
    def setUp(self):
        super(InMemoryDatabaseData, self).setUp()
        self.db.set('one', {'name': 'Alice', 'good': True, 'chief': True})
        self.db.set('two', {'name': 'Bob', 'good': True})
        self.db.set('three', {'name': 'Carl', 'good': False})


class TempStorageDatabase(TestCase):

    options = {}

    def setUp(self):
        self.fd, self.filename = mkstemp()
        self.db = MeuhDb(self.filename, **self.options)

    def tearDown(self):
        unlink(self.filename)


class TempStorageDatabaseData(TempStorageDatabase):
    def setUp(self):
        super(TempStorageDatabaseData, self).setUp()
        self.db.set('one', {'name': 'Alice', 'good': True, 'chief': True})
        self.db.set('two', {'name': 'Bob', 'good': True})
        self.db.set('three', {'name': 'Carl', 'good': False})
