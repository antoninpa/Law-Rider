#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import peewee


database = peewee.SqliteDatabase("./pw_DDB.sqlite")


def initialize():
    database.connect()
    database.create_tables([Abonnements, Mails, Recherches], safe=True)
    database.close()


class Recherches(peewee.Model):
    type_rech = peewee.CharField()
    opt_1 = peewee.CharField(unique=True)
    user_name = peewee.CharField()
    res_1 = peewee.CharField()
    res_1_url = peewee.CharField()
    res_2 = peewee.CharField()
    res_2_url = peewee.CharField()
    res_3 = peewee.CharField()
    res_3_url = peewee.CharField()
    res_4 = peewee.CharField()
    res_4_url = peewee.CharField()
    res_5 = peewee.CharField()
    res_5_url = peewee.CharField()

    class Meta:
        database = database
        indexes = (
            (('type_rech', 'opt_1'), True),
        )


class Mails(peewee.Model):
    mail_desc = peewee.CharField(unique=True)

    class Meta:
        database = database


class Abonnements(peewee.Model):
    recherche = peewee.ForeignKeyField(Recherches)
    personne = peewee.ForeignKeyField(Mails)

    class Meta:
        database = database
        indexes = (
            (('recherche', 'personne'), True),
        )


if __name__ == "__main__":
    try:
        Abonnements.create_table()
    except peewee.OperationalError():
        print('Table Abonnements déjà créée')

    try:
        Recherches.create_table()
    except peewee.OperationalError():
        print('Table Recherches déjà créée')

    try:
        Mails.create_table()
    except peewee.OperationalError():
        print('Table Mails déjà créée')
