#!/usr/bin/env python
# -*- coding: utf-8 -*-
import redis

__author__ = 'dz0ny'
__email__ = 'dz0ny@ubuntu.si'
__version__ = '0.0.3'

class Enviroment:
    # Singleton
    database = redis.StrictRedis(host='localhost', port=6379, db=0)