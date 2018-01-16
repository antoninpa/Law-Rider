#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import random

DEBUG = True # Turns on debugging features in Flask
SECRET_KEY = 'MOT DE PASSE'
SECURITY_PASSWORD_SALT = str(random.randint(0, 499))
DATABASE = {
    'name': 'pw_DDB.sqlite',
    'engine': 'peewee.SqliteDatabase',
}
