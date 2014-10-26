#!/usr/bin/env python
#-*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

NAME = 'meuhdb'
DESCRIPTION = 'A database that says "Meuh".'
REQUIREMENTS = [
]
__VERSION__ = '0.0.1'

params = dict(
    name=NAME,
    description=DESCRIPTION,
    packages=['meuhdb'],
    version=__VERSION__,
    author='Bruno Bord',
    author_email='bruno@jehaisleprintemps.net',
    license='MIT License',
    include_package_data=True,
    install_requires=REQUIREMENTS,
    zip_safe=False,
    classifiers=[
    ],
)

if __name__ == '__main__':
    setup(**params)
