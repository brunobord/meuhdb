#!/usr/bin/env python
#-*- coding: utf-8 -*-
from os import unlink
from tempfile import mkstemp
import random
import time
from meuhdb.core import MeuhDb, DUMPER


def dump_load(backend):
    fd, filename = mkstemp()
    db = MeuhDb(filename, backend=backend)
    for x in range(200000):
        db.set("%d" % x, {'score': random.randrange(1, 100)})
    t0 = time.clock()
    db.commit()
    t1 = time.clock()
    t2 = time.clock()
    db = MeuhDb(filename, backend=backend)
    t3 = time.clock()
    unlink(filename)
    return t3 - t2, t1 - t0

if __name__ == '__main__':
    result = ((dump_load(backend), backend) for backend in DUMPER)
    result = sorted(result)
    for t, backend in result:
        print t, backend
