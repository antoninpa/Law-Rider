#!/usr/bin/env python2.7
# coding: utf-8

import requests
import re
import misc
import feedparser
from bs4 import BeautifulSoup


def cnil_communiques():
    lst_return = []
    r = requests.get("https://www.cnil.fr/fr/communiques")
    soup = BeautifulSoup(r.text, 'lxml')
    views = soup.find_all('div', attrs={'class': 'views-row'})
    for el in views:
        title = el.find('h3', attrs={'class': 'ctn-gen-liste-titre'}).text
        url = el.find('a').get('href')
        lst_return.append([title, "https://www.cnil.fr"+url])
    clean = misc.clean_rech(lst_return)
    clean.append(['CNIL', 'Communiqués'])
    return clean


def cnil_actualites():
    lst_return = []
    actu = "https://www.cnil.fr/fr/rss.xml"
    feed = feedparser.parse(actu)
    res = feed["items"]
    for el in res:
        title = el['summary_detail']['value']
        url = el['links'][0]['href']
        lst_return.append([title, url])
    clean = misc.clean_rech(lst_return)
    clean.append(['CNIL', 'Acualités'])
    return clean


def g29_opinions():
    lst_return = []
    r = requests.get("http://ec.europa.eu/justice/data-protection/article-29/documentation/opinion-recommendation/index_en.htm")
    soup = BeautifulSoup(r.text, 'lxml')
    l = soup.find('div', attrs={'id': 'maincontentSec2'})
    d = l.find_all('a', attrs={'class': 'link-ico'})
    for el in d:
        url = el.get('href')
        desc = el.find('span').text
        lst_return.append([desc, "http://ec.europa.eu"+url])
    clean = misc.clean_rech(lst_return)
    clean.append(['G29', 'Avis & Opinions'])
    return clean


def g29_letters():
    lst_return = []
    r = requests.get("http://ec.europa.eu/justice/data-protection/article-29/documentation/other-document/index_en.htm")
    soup = BeautifulSoup(r.text, 'lxml')
    l = soup.find('div', attrs={'id': 'maincontentSec2'})
    d = l.find_all('a', attrs={'class': 'link-ico'})
    for el in d:
        url = el.get('href')
        desc = el.find('span').text
        if desc == 'appendix':
            pass
        else:
            lst_return.append([desc, "http://ec.europa.eu"+url])
    clean = misc.clean_rech(lst_return)
    clean.append(['G29', 'Communications'])
    return clean


def g29_pressrelease():
    lst_return = []
    r = requests.get("http://ec.europa.eu/justice/data-protection/article-29/press-material/press-release/index_en.htm")
    soup = BeautifulSoup(r.text, 'lxml')
    l = soup.find('div', attrs={'id': 'maincontentSec2'})
    d = l.find_all('a', attrs={'class': 'link-ico'})
    for el in d:
        url = el.get('href')
        m = re.search(r'(?:- | Party -| Party )(.*)', el.find('span').text)
        desc = m.group()
        if desc == 'appendix':
            pass
        else:
            lst_return.append([desc, "http://ec.europa.eu"+url])
    clean = misc.clean_rech(lst_return)
    clean.append(['G29', 'Communiqués de presse'])
    return clean


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
        'radioMots': "MTE",
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


def aws_cgu():
    paraph = []  # Will receive list of paragraphs
    r = requests.get('https://aws.amazon.com/aup/')
    soup = BeautifulSoup(r.text, 'lxml')
    intro = soup.find_all('div', attrs={'class': 'lead'})
    mtext = soup.find('div', attrs={'class': 'content parsys'})
    dd = mtext.find_all('div', attrs={'class':'section'})
    for el in dd:
        paraph.append(el.text)
    date = re.search(r"(?<=Updated )(.*)(?=</i>)", str(intro[1])).group(0)
    return date, paraph

def aws_cust_agr():
    paraph = []  # Will receive list of paragraphs
    r = requests.get('https://aws.amazon.com/agreement/')
    soup = BeautifulSoup(r.text, 'lxml')
    mtext = soup.find('div', attrs={'class': 'content parsys'})
    dd = mtext.find_all('div', attrs={'class': 'section'})
    for el in dd:
        paraph.append(el.text)
    date = re.search(r"(?<=Last updated )(.*)(?=\n)", dd[-1].text).group(0)
    return date, paraph

def aws_ser_term():
    paraph = []  # Will receive list of paragraphs
    r = requests.get('https://aws.amazon.com/service-terms/')
    soup = BeautifulSoup(r.text, 'lxml')
    mtext = soup.find('div', attrs={'class': 'content parsys'})
    dd = mtext.find_all('div', attrs={'class': 'section'})
    for el in dd:
        paraph.append(el.text.replace('\n', ''))
    date = re.search(r"(?<=Last updated: )(.*)(?=\n)", dd[0].text).group(0)
    del paraph[0]  # Remove date from list
    return date, paraph

def fb_privacy():
    paraph = []  # Will receive list of paragraphs
    r = requests.get('https://www.facebook.com/about/privacy/')
    soup = BeautifulSoup(r.text, 'lxml')
    mtext = soup.find_all('div', attrs={'class': '_3x93'})
    for el in mtext:
        a = el.get_text().encode('latin-1').replace('Revenir en haut ', '')
        paraph.append(a.decode('utf-8'))
    date = re.search(r"(?<=vision : )(.*)", paraph[-1].encode('utf-8')).group(0)
    return date, paraph


def fb_terms():
    paraph = []
    r = requests.get('https://www.facebook.com/legal/terms')
    soup = BeautifulSoup(r.text, 'lxml')
    articles = soup.find_all('li', attrs={'style': 'margin-bottom: 16px;'})
    for el in articles:
        a = el.get_text().encode('latin-1')
        paraph.append(a.decode('utf-8'))
    corps = soup.find_all('div', attrs={'class': 'mvm uiP fsm'})
    date = re.search(r"(?<=révision : )(.*)", corps[2].text.encode('latin-1')).group(0)
    return date, paraph


if __name__ == "__main__":
    aws_ser_term()
