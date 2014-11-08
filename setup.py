#!/usr/bin/env python
#-*- coding: utf-8 -*-
from codecs import open
import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

init_py = open('meuhdb/__init__.py', 'r').read()
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
    license='MIT License',
    include_package_data=True,
    install_requires=[
        'six',
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Database',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)

if __name__ == '__main__':
    setup(**params)
