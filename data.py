#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author : Antonin Paillet <antoninpa> at <gmail.com>
# licence : Creative Commons - Non commercial - By - Share Alike

import re
import requests
import peewee as pw
import dateutil.tz
import lxml.etree as ET
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime

# -------------------------------------
# ------------- SQLITE ----------------
# -------------------------------------

DATABASE = './data2.sqlite'
db = pw.SqliteDatabase(DATABASE)


class Main(pw.Model):
    text_num = pw.TextField(primary_key=True)
    text_desc = pw.TextField()
    text_jo = pw.TextField()
    feed_desc = pw.TextField()
    feed_url = pw.TextField()

    class Meta:
        database = db


def create_db():
    """
    Creates the table
    """
    try:
        Main.create_table()
    except pw.OperationalError():
        print('BDD déjà créée')


def create_entry(a, b, c, d):
    """
    Creates a new sql entry
    :param a: Number of the text
    :param b: Full name of the text
    :param c: JORF number of the text
    :param d: List with the full name and url of the last result
    """
    try:
        with db.atomic():
            Main.create(
                text_num=a,
                text_desc=b,
                text_jo=c,
                feed_desc=d[0],
                feed_url=d[1]
             )
    except pw.IntegrityError:
        print('The feed is already registered')
        pass


def read_all():
    """
    Gets all the entries in the DB
    :return: List of all results
    """
    i = 1
    res = []
    query = Main.select().dicts()
    for row in query:
        row['num'] = i
        i += 1
        res.append(row)
    return res


def read_one(text_num):
    """
    Gets information about a particular entry
    :param text_num: Number of the text
    :return: List with all values related to an entry
    """
    try:
        feed = Main.get(Main.text_num == text_num)
        res = [feed.text_num, feed.text_desc, feed.feed_desc, feed.feed_url]
        return res
    except pw.DoesNotExist:
        print('The feed {} does not exist'.format(text_num))
        pass


def update_sql(id_loi, fe_desc, fe_url):
    """
    Updates a sql entry with new last text
    :param id_loi: Number of the text
    :param fe_desc: Full name of the last result
    :param fe_url: Url of the last result
    """
    query = Main.update({Main.feed_desc: fe_desc, Main.feed_url: fe_url}).where(Main.text_num == id_loi)
    query.execute()


def check_exists(id_loi):
    """
    Checks whether a specific entry is registered in DB
    :param id_loi: Number of the text
    :return: Boolean indicating whether it exists or not
    """
    query = Main.select().where(Main.text_num == id_loi)
    return query.exists()


def empty_sql():
    """
    Empties the database
    """
    query = Main.delete()
    query.execute()

# -----------------------------------


# -----------------------------------
# ---------- UPDATEs TOOLS ----------
# -----------------------------------


def update_monitor():
    """
    Checks if a new text is available and
    if so updates both the rss feed and sql db
    """
    saved_feeds = read_all()
    for feeds in saved_feeds:
        legif_res = text_results(feeds['text_num'])
        rss_feeds = get_rss(feeds['text_num'])
        for res in legif_res:
            if res[0] in rss_feeds:
                continue
            else:
                update_rss(feeds['text_num'], res)
                update_sql(feeds['text_num'], res[0], res[1])


def get_rss(id_loi):
    """
    Used to build the list of existing feeds,
    used in compare()
    :param id_loi:
    :return: output: list of registered feeds
    """
    output = []
    parser = ET.XMLParser()
    tree = ET.parse('./data/rss/{}.xml'.format(id_loi), parser)
    channel = tree.getroot()
    for element in channel.iter('item'):
        output.append(element.find('title').text)
    return output


def update_rss(id_loi, res_list):
    """
    Update the rss feed with a new item
    :param id_loi: number of the text
    :param res_list: list of new item(s)
    """
    parser = ET.XMLParser()
    tree = ET.parse('./data/rss/{}.xml'.format(id_loi), parser)
    channel = tree.getroot()
    channel[0][7].text = str(datetime.now(dateutil.tz.tzutc()))

    item = ET.SubElement(channel, "item")
    title = ET.SubElement(item, "title")
    title.text = res_list[0]
    link = ET.SubElement(item, "link")
    link.text = res_list[1]
    description = ET.SubElement(item, "guid")
    description.text = res_list[2]

    channel.find(".//item").addprevious(item)

    tree = ET.ElementTree(channel)
    tree.write('./data/rss/{}.xml'.format(id_loi), xml_declaration=True, encoding='utf-8')


def text_results(id_loi):
    """
    Gets the list of texts mentionning the text number
    :param id_loi: number of the text
    :return: a list of list : [['text full name', 'text url', 'text JO number'], []]
    """
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
        'User-Agent': 'Mozilla/5.0 (X11; Debian; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0'
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
    print(lst_return)
    return lst_return


def valid_input_number(search_id):
    """
    Checks if the input is a valid text number
    :param search_id: value from the textinput
    :return: An empty string if the text is valid otherwise an error message.
    """
    errors = ''
    if str(search_id) is '':
        errors = "Le numéro du texte n'est pas renseigné ou son format n'est pas valide."
    else:
        d = re.match('(\d{2,4}-\d{1,4})', str(search_id))
        if d is None:
            errors = "Le numéro du texte n'est pas renseigné ou son format n'est pas valide."
        else:
            pass
    return errors


def text_full_name(id_loi):
    """
    Makes a request to legifrance then scrapes it in order to obtain the full
    name(s) of the text(s) with its JORFTEXT reference(s) in a list of list.
    :param id_loi: number of the text
    :return: list of list(s) eg: [['décret 1', 'JORFTEXT1556'], ['..', '..']]
    """
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
        'User-Agent': 'Mozilla/5.0 (X11; Debian; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0'
    }
    session = requests.Session()
    response = session.post("http://www.legifrance.gouv.fr/rechTexte.do", headers=headers, params=parametres)
    soup = BeautifulSoup(response.text, 'lxml')
    d = soup.find('ol', attrs={'start': '1'})
    a = d.find_all('li')
    for el in a:
        jo_id = re.search(r"(JORFTEXT\d*)", str(el.find_all('a')[0]))
        name = el.find('span', attrs={'class': 'normal'}).text
        lst_return.append([name, jo_id.group(0)])
    return lst_return


def create_feed(id_loi, res_list):
    """
    Creates a .xml rss feed.
    :param id_loi: number of the text
    :param res_list: list of publications
    """
    fg = FeedGenerator()
    fg.id(id_loi)
    fg.title(id_loi)
    fg.author({'name': 'lawrider.fr', 'email': 'antoninpa@gmail.com'})
    fg.link(href='https://www.lawrider.fr', rel='alternate')
    fg.subtitle('Suivez les recensions d\'une loi.')
    fg.link(href='https://www.lawrider.fr', rel='self')
    fg.generator(generator='Antonin Paillet avec python-feedgen.')
    fg.lastBuildDate(datetime.now(dateutil.tz.tzutc()))
    fg.language('fr')
    for el in res_list:
        fe = fg.add_entry()
        fe.id(el[2])
        fe.title(el[0])
        fe.link(href=el[1])

    fg.rss_file('./data/rss/{}.xml'.format(id_loi), encoding='UTF-8')


if __name__ == '__main__':
    text_results('2012-300')


