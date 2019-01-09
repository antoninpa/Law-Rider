#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import requests
import sqlalchemy as db
from sqlalchemy.sql.expression import exists
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator


error_msg = """Le numéro du texte n'est pas renseigné ou son format n'est pas valide."""


### SQLITE ####

def create_feed(text_num, text_desc, feed):
    engine = db.create_engine('sqlite:///static/data.sqlite')
    connection = engine.connect()
    metadata = db.MetaData()
    main = db.Table('main', metadata, autoload=True, autoload_with=engine)
    data = [{
        'text_num': text_num,
        'text_desc': text_desc,
        'feed_desc': feed[0],
        'feed_url': feed[1]
    }]
    query = db.insert(main).values()
    connection.execute(query, data)


def read_one(id_loi):
    engine = db.create_engine('sqlite:///static/data.sqlite')
    connection = engine.connect()
    metadata = db.MetaData()
    main = db.Table('main', metadata, autoload=True, autoload_with=engine)
    result = connection.execute(db.select([main]).where(main.columns.text_num == id_loi)).fetchone()
    print(result)
    return result


def read_all():
    clean_res = []
    engine = db.create_engine('sqlite:///static/data.sqlite')
    connection = engine.connect()
    metadata = db.MetaData()
    main = db.Table('main', metadata, autoload=True, autoload_with=engine)
    results = connection.execute(db.select([main])).fetchall()
    i = 1
    for el in results:
        d = list(el)
        d.append(i)
        clean_res.append(d)
        i += 1
    return clean_res


def update(source, res_text, res_url):
    engine = db.create_engine('sqlite:///static/data.sqlite')
    connection = engine.connect()
    metadata = db.MetaData()
    main = db.Table('main', metadata, autoload=True, autoload_with=engine)
    query = db.update(main).values(feed_desc=res_text, feed_url=res_url)
    query = query.where(main.columns.text_num == source)
    results = connection.execute(query)


def check_exists(id_loi):
    """
    Vérifie qu'un flux existe dans data.sqlite
    :param id_loi: numéro de la loi (clef primaire dans data.sqlite)
    :return: True ou False
    """
    print('in check')
    engine = db.create_engine('sqlite:///static/data.sqlite')
    connection = engine.connect()
    metadata = db.MetaData()
    main = db.Table('main', metadata, autoload=True, autoload_with=engine)
    s = db.select([main]).where(main.columns.text_num == id_loi)
    s = exists(s).select()
    result = connection.execute(s).scalar()
    print(result)
    return result


######################################


def compare():
    res = read_all()
    for el in res:
        legif_res = legifr_spider(el[0])
        if el[2] in legif_res[0]:
            pass
        else:
            feed_gen(el[0], legif_res)
            update(el[0], legif_res[0][0], legif_res[0][1])


### SCRAPING ###

def legifr_spider(id_loi):
    lst_return = []
    parametres = {
        'champNatureTexte': '*',
        'champNumTexte': '',
        'champNOR': '',
        'champDateSignaJ': "",
        'champDateSignaM': "",
        'champDateSignaA': "",
        'champDatePubliJ': "",
        'champDatePubliM': "",
        'champDatePubliA': "",
        'champMots': id_loi,
        'expExacte': 'on',
        'radioMots': "MTE",
        'bouton': 'Rechercher'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
    }
    session = requests.Session()
    r = session.post("https://www.legifrance.gouv.fr/rechTexte.do", headers=headers, params=parametres)
    soup = BeautifulSoup(r.text, 'lxml')
    d = soup.find('ol', attrs={'start': '1'})
    a = d.find_all('li')
    for el in a:
        desc = el.find('span', attrs={'class': 'normal'}).text
        jo_id = re.search(r"(JORFTEXT\d*)", str(el.find_all('a')[0]))
        url = "https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=" + jo_id.group(0) + "&categorieLien=id"
        lst_return.append([desc, url, jo_id.group(0)])
    return lst_return


def legifr_search_check(search_id):
    print('in legifr search check')
    errors = ''
    if str(search_id) is '':
        errors = error_msg
    else:
        d = re.match('(\d{2,4}-\d{1,4})', str(search_id))
        if d is None:
            errors = error_msg
        else:
            pass
    print(errors)
    return errors


def get_texte_name(id_loi):
    lst_return = []
    parametres = {
        'champNatureTexte': '*',
        'champNumTexte': id_loi,
        'champNOR': '',
        'champDateSignaJ': "",
        'champDateSignaM': "",
        'champDateSignaA': "",
        'champDatePubliJ': "",
        'champDatePubliM': "",
        'champDatePubliA': "",
        'champMots': '',
        'expExacte': 'on',
        'radioMots': "MTI",
        'bouton': 'Rechercher'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
    }
    session = requests.Session()
    response = session.post("http://www.legifrance.gouv.fr/rechTexte.do", headers=headers, params=parametres)
    soup = BeautifulSoup(response.text, 'lxml')
    d = soup.find('ol', attrs={'start': '1'})
    a = d.find_all('li')
    for el in a:
        lst_return.append(el.find('span', attrs={'class': 'normal'}).text)
    return lst_return

############################

def feed_gen(id_loi, res_list):
    fg = FeedGenerator()
    fg.id(id_loi)
    fg.title(id_loi)
    fg.author({'name': 'lawrider.fr', 'email': 'antoninpa@gmail.com'})
    fg.link(href='https://www.lawrider.fr', rel='alternate')
    fg.subtitle('Suivez les recensions d\'une loi.')
    fg.link(href='https://www.lawrider.fr', rel='self')
    fg.language('fr')

    for el in res_list:
        fe = fg.add_entry()
        fe.id(el[2])
        fe.title(el[0])
        fe.link(href=el[1])

    fg.rss_file('./data/rss/{}.xml'.format(id_loi))


if __name__ == '__main__':
    compare()
