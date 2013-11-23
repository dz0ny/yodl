#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']

setup(name='yodl',
      version=get_version('yodl/__init__.py'),
      description='Your mom\'s music downloader',
      long_description=readme + '\n\n' + history,
      entry_points={
          'console_scripts': [
              'yomm = yodl.__main__:main',
          ],
      },
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Tornado",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      packages=find_packages(exclude=['supervisor', 'tests', 'tests.*']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'tornado',
          'redis',
          'celery',
          'youtube_dl'
      ],
      test_suite='nose.collector',
      )
