MeuhDb
======

    The database that says "Meuh"

|Build Status| |Coverage Status|

**MeuhDb** is a "dummy" key / JSON value store written in Python.

Install
-------

To install the latest release:

::

    pip install meuhdb

... but since this is a very early release, you'd better stick to this
Github source repository. You may want to read `the
Changelog <https://github.com/brunobord/meuhdb/blob/master/Changelog.md>`__,
too.

Basic usage
-----------

.. code:: python

    >>> from meuhdb import MeuhDb
    >>> db = MeuhDb()  # Create in-memory database
    >>> db.set('one', {'name': 'Alice', 'good': True, 'chief': True})
    >>> db.set('two', {'name': 'Bob', 'good': True})
    >>> db.set('three', {'name': 'Carl', 'good': False})
    >>> db.filter(name='Alice')
    {'one': {'chief': True, 'good': True, 'name': 'Alice'}}
    >>> db.filter(good=True)
    {'two': {'good': True, 'name': 'Bob'}, 'one': {'chief': True, 'good': True, 'name': 'Alice'}}
    >>> db.filter(good=True, chief=True)  # More than one criteria, it's a "AND"
    {'one': {'chief': True, 'good': True, 'name': 'Alice'}
    >>> db.delete('one')
    >>> db.filter(name='Alice')
    {}
    >>> db.exists('one')
    False
    >>> db.insert({'name': 'John'})
    'eb3c3a1d-8999-4052-9e3c-2f3542c047b1'
    >>> db.update('eb3c3a1d-8999-4052-9e3c-2f3542c047b1', {'age': 42})
    >>> db.get('eb3c3a1d-8999-4052-9e3c-2f3542c047b1')
    {'age': 42, 'name': 'John'}

At the moment, you can only query on "equalities", i.e. a strict
equality between what you're looking for and what's in the JSON fields
(no special operator: greater than, different, etc).

The values must be JSON serializable values (dictionaries, does not work
with dates, datetimes, sets, etc.)

Database creation
~~~~~~~~~~~~~~~~~

There are a few optional parameters with the ``MeuhDb`` class
constructor:

.. code:: python

    MeuhDb(
      path=None,
      autocommit=False, autocommit_after=None,
      lazy_indexes=False,
      backend=DEFAULT_BACKEND)

-  ``path``: is the file path of your JSON database if you want to save
   it to a file. If the file already exists, **MeuhDb** tries to load
   its data. If it's not provided, the DB will be in-memory.
-  ``autocommit``: if set to ``True``, every "write" operation will be
   transmitted to the file. It can be I/O consuming, since the whole DB
   is written on the disk every time.
-  ``autocommit_after``: A numeric value. If set, the database will be
   committed every "n" write operations. Bear in mind that if the
   ``autocommit`` flag is set, it has priority over the counter.
-  ``lazy_indexes``: When set to True, when the DB is written to the
   database, only the definition of the indexes is stored, not the index
   values themselves. This means the DB is faster at writing times, but
   will load slower, because we'll need to rebuild all indexes,
-  ``backend``: chose which JSON backend you can use. There are 3
   backends possible, from the least efficient, to the best one: "json"
   (from the standard lib), "simplejson", "jsonlib", "yajl", or "ujson".
   **MeuhDb** will try to load each one of them and make them available
   if you want. The ``DEFAULT_BACKEND`` value will take the most
   performing backend value available. If you provide an unavailable
   backend, don't worry, **MeuhDb** will fallback to the comfortable
   \`\ ``json`` from the standard library.

Example:

.. code:: python

    >>> db = MeuhDb('hello.json', autocommit=False, backend='ujson')
    >>> db.set('1', {'name': 'Alice'})  # data is not on disk
    >>> db.commit()  # saves to disk
    >>> db = MeuhDb('hello.json', autocommit=True)
    >>> db.all()  # Data is reloaded from the disk
    {u'1': {u'name': u'Alice'}}
    >>> db.set('2', {'name': 'Bob'})  # data is written on disk

Indexes
-------

**MeuhDb** supports index creation. You can index one or more fields to
accelerate queries.

Example:

.. code:: python

    >>> db.create_index('name')
    >>> db.filter(name='Alice')  # Will use this index

-  You don't have to index all the fields available in your JSON values,
   only the one you may query on.
-  Indexes will be saved on ``commit()`` along with the Database.
-  if somehow the index is screwed up, simply create it with the
   ``recreate`` argument: ``db.create_index('name', recreate=True)``.

Index types
~~~~~~~~~~~

You can specify the index type using this:

::

    db.create_index('name', _type='lazy')

You can only create two types of indexes: ``default`` or ``lazy``. Lazy
indexes will not be stored when the database is committed, and will be
reloaded at startup. You can mix default and lazy indexes.

Note: since all JSON key should be strings, you can't obviously store
indexes with non-string values. As soon as an index receives a
non-string value (an int or a boolean, for example), it'll be changed
into a lazy index.

Warnings
--------

This is not a real actual ACID-ready database manager. This will
probably suit a "one-user-only" use case. Opening an loading a large
file is very I/O consuming. So **MeuhDb** will **never** replace a
proper NoSQL database system.

Hack
----

**MeuhDb** will work with a standard Python 2 distribution. (I've got
plans to make it Python-3-ready)

Inside a virtualenv, simply clone this repository and install it in dev
mode:

::

    git clone https://github.com/brunobord/meuhdb.git
    cd meuhdb
    pip install -e ./

You may want to install one or more of these packages to be able to pick
one of these enhanced backends:

-  ``simplejson``,
-  ``jsonlib`` (or ``jsonlib-python3``),
-  ``yajl``,
-  ``ujson``

To run the tests, you'll have to install ``tox`` (``pip install tox``)
and simply run the command ``tox``.

Todo
~~~~

A lot of things are missing. `The Github issues
list <https://github.com/brunobord/meuhdb/issues>`__ will work as a
"todo list". If you have any bug report, suggestion, please do.

--------------

License
-------

This software is published under the terms of the MIT License See the
`LICENSE <LICENSE>`__ file for more information.

.. |Build Status| image:: https://travis-ci.org/brunobord/meuhdb.svg?branch=master
   :target: https://travis-ci.org/brunobord/meuhdb
.. |Coverage Status| image:: https://img.shields.io/coveralls/brunobord/meuhdb.svg
   :target: https://coveralls.io/r/brunobord/meuhdb
