#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import redis

__author__ = 'dz0ny'
__email__ = 'dz0ny@ubuntu.si'
__version__ = '0.0.3'

class Enviroment:
    # Singleton

    database = redis.StrictRedis.from_url(
        os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    )