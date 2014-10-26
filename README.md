# MeuhDb

> The database that says "Meuh"

**MeuhDb** is a "dummy" key / JSON value store written in Python.

## Basic usage

``` python
>>> from meuhdb.core import MeuhDb
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
```

At the moment, you can only query on "equalities", i.e. a strict equality
between what you're looking for and what's in the JSON fields (no special
operator: greater than, different, etc).

The values must be JSON serializable values (dictionaries, does not work with
dates, datetimes, sets, etc.)


### Database creation

There are a few optional parameters with the ``MeuhDb`` class constructor:

```python
MeuhDb(path=None, autocommit=False, backend=DEFAULT_BACKEND)
```

* `path`: is the file path of your JSON database if you want to save it to a
  file. If the file already exists, **MeuhDb** tries to load its data. If it's
  not provided, the DB will be in-memory.
* `autocommit`: if set to `True`, every "write" operation will be transmitted
  to the file. It can be I/O consuming, since the whole DB is written on the
  disk every time.
* `backend`: chose which JSON backend you can use. There are 4 backends
  possible, from the least efficient, to the best one: "json" (from the standard
  lib), "simplejson", "ujson" and "msgpack".
  **MeuhDb** will try to load each one of them and make them available if you
  want. The ``DEFAULT_BACKEND`` value will take the most performing backend
  value available.
  If you provide an unavailable backend, don't worry, **MeuhDb** will fallback
  to the comfortable ``json` from the standard library.

**WARNING**: ``msgpack`` library will load and dump your JSON data into a binary
format. It's a very fast and compact storage method, but binary data is not
readable with a regular text viewer. If you want to browse your database, you'll
have to rely in the ``msgpack`` library.

Example:

```python
>>> db = MeuhDb('hello.json', autocommit=False, backend='ujson')
>>> db.set('1', {'name': 'Alice'})  # data is not on disk
>>> db.commit()  # saves to disk
>>> db = MeuhDb('hello.json', autocommit=True)
>>> db.all()  # Data is reloaded from the disk
>>> {u'1': {u'name': u'Alice'}}
>>> db.set('2', {'name': 'Bob'})  # data is written on disk
```

## Indexes

**MeuhDb** supports index creation. You can index one or more fields to accelerate
queries.

Example:

```python
>>> db.create_index('name')
>>> db.filter(name='Alice')  # Will use this index
```

* You don't have to index all the fields available in your JSON values, only
  the one you may query on.
* Indexes will be saved on ``commit()`` along with the Database.
* if somehow the index is screwed up, simply create it with the ``recreate``
  argument: ``db.create_index('name', recreate=True)``.

## Warnings

This is not a real actual ACID-ready database manager. This will probably suit a
"one-user-only" use case. Opening an loading a large file is very I/O consuming.
So **MeuhDb** will **never** replace a proper NoSQL database system.

## Hack

**MeuhDb** will work with a standard Python 2 distribution. (I've got plans
to make it Python-3-ready)

Inside a virtualenv, simply clone this repository and install it in dev mode:

```
git clone https://github.com/brunobord/meuhdb.git
cd meuhdb
pip install -e ./
```

You may want to install one or more of these packages to be able to pick one of
these enhanced backends:

* `simplejson`
* `usjon`
* `msgpack`

To run the tests, you'll have to install ``tox`` (``pip install tox``) and
simply run the command ``tox``.

### Todo

A lot of things:

* Advanced Index manipulation (remove_index, uniqueness?, multiple fields?),
* Advanced queries (à la Django with ``field__gt``, ``field__contains``, etc),
* ``insert`` method with automatic UUID generation,
* Python 3 support...

----

## License

This software is published under the terms of the MIT License

```
Copyright (c) 2014 Bruno Bord

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
