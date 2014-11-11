# MeuhDb

## v0.3.0 (2014-11-11)

* Lazy indexes option: will write faster, but load slower,
* Changed the way indexes are built/loaded/stored, This might break your data.
  But who cares? I'm probably the only one to use this,
* Automatically change index type if inserted value is non-string.

## v0.2.0 (2014-11-09)

* Small refactor, splitting core module in submodules,
* Bugfix: throw a ``BadValueError`` when the value provided is not a dict,
* Add a new parameter: ``autocommit_after``. DB will be committed after "n"
  committable operations (set, insert, update, delete...),
* Bugfix: use deepcopy() for the inserted / updated value. Prevent unwanted
  value modification side-effects.

## v0.1.1 (2014-11-08)

* Hotfixing the tox tests mess.

## v0.1.0 (2014-11-08)

* Added performances tests, and reordering libs priority,
* Bugfix: prevent list/set mess during index update,
* Added coveralls.io configuration and badge on the README,
* Little refactors for easier access to API, easier versionning, etc.

## v0.0.3 (2014-10-28)

Added support to:

* ``jsonlib`` (or ``jsonlib-python3``),
* ``yajl`` (couldn't test "yajl" on Python3.4, it failed in Travis tests, but
  it worked on my laptop, so, there's no guarantee),

## v0.0.2 (2014-10-27)

* Added a ``remove_index`` to remove unwanted index,
* Added an ``update`` method,
* Added an ``insert`` method,
* Dropped msgpack format: it was a bad idea,
* The tox test grid is now complete,

## v0.0.1 (2014-10-26)

* Initial release,
* Supports to standard json, simplejson, ujson, ~~msgpack~~,
* Supports Python 2.6, 2.7, 3.3, 3.4,
* set/get values, simple filter, simple indexes,
* in-memory or file storage,
* autocommit option
* #8: automated tests using [travis-ci](https://travis-ci.org/)
