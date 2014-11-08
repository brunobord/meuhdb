#!/usr/bin/env python
#-*- coding: utf-8 -*-
from codecs import open
import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

init_py = open('meuhdb/__init__.py').read()
metadata = dict(re.findall("__([a-z]+)__ = ['\"]([^']+)['\"]", init_py))
metadata['doc'] = re.findall('"""(.+)"""', init_py)[0]

params = dict(
    name='meuhdb',
    description=metadata['doc'],
    packages=['meuhdb'],
    version=metadata['version'],
    author='Bruno Bord',
    author_email='bruno@jehaisleprintemps.net',
    url=metadata['url'],
    license=open('LICENSE').read(),
    include_package_data=True,
    install_requires=open('requirements.txt').readlines(),
    zip_safe=False,
    classifiers=[
    ],
)

if __name__ == '__main__':
    setup(**params)
