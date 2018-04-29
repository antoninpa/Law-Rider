#!/usr/bin/env python2.7
# coding: utf-8

import requests
import re
import misc
import feedparser
from bs4 import BeautifulSoup

def legifr_spider(id_loi):
    lst_return = []
    parametres = {
        'champNatureTexte': '*',
        'champDateSignaJ': "",
        'champDateSignaM': "",
        'champDateSignaA': "",
        'champDatePubliJ': "",
        'champDatePubliM': "",
        'champDatePubliA': "",
        'champMots': id_loi,
        'expExacte': 'on',
        'radioMots': "MTE",  # Mots exacts dans le texte
        'bouton': 'Rechercher'
    }
    session = requests.Session()
    response = session.post("http://www.legifrance.gouv.fr/rechTexte.do", params=parametres)
    mycookies = response.cookies.get_dict()  # Pour certaines recherches il faut obtenir un cookie
    r = requests.post("http://www.legifrance.gouv.fr/rechTexte.do", params=parametres, cookies=mycookies)
    soup = BeautifulSoup(r.text, 'lxml')
    d = soup.find('ol', attrs={'start': '1'})
    a = d.find_all('li')
    for el in a:
        desc = el.find('span', attrs={'class': 'normal'}).text
        m = re.search(r"(JORFTEXT\d*)", str(el.find_all('a')[0]))
        url = "https://www.legifrance.gouv.fr/affichTexte.do?cidTexte="+m.group()+"&categorieLien=id"
        lst_return.append([desc, url])
    clean = misc.clean_rech(lst_return)

    return clean


if __name__ == "__main__":
    legif_spider('2016-1635')
