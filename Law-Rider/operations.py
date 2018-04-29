#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import time
import scraping as scr
import mail
import misc
from peewee import IntegrityError, SqliteDatabase
from AppliWeb.models import Abonnements, Mails, Recherches

database = SqliteDatabase("/home/antoninx_v2/Bureau/SpiderOak Hive/AppliWeb/pw_DDB.sqlite")


def delete_abo(id_rech, id_mail):
    abo = Abonnements.get(
        Abonnements.recherche == id_rech,
        Abonnements.personne == id_mail
    )
    abo.delete_instance()

def delete_rech(id_rech):
    rech = Recherches.get(
        Recherches.id == id_rech
    )
    rech.delete_instance()

def delete_mail(id_mail):
    adress = Mails.get(
        Mails.id == id_mail
    )
    adress.delete_instance()

def update_rech(rech_id, results):
    upRech = Recherches.select().where(Recherches.id == rech_id).get()

    upRech.res_1 = results[0][0]
    upRech.res_1_url = results[0][1]
    upRech.res_2 = results[1][0]
    upRech.res_2_url = results[1][1]
    upRech.res_3 = results[2][0]
    upRech.res_3_url = results[2][1]
    upRech.res_4 = results[3][0]
    upRech.res_4_url = results[3][1]
    upRech.res_5 = results[4][0]
    upRech.res_5_url = results[4][1]

    upRech.save()


def update_cgu(rech_id, cgu_id, res,  date):
    misc.csv_writer(cgu_id, res)
    upRech = Recherches.select().where(Recherches.id == rech_id).get()
    upRech.res_1 = date
    upRech.save()


def compare(new_res, res_1):
    news = []
    if res_1 == new_res[1][0]:
        news.append([new_res[0][0], new_res[0][1]])
        return news
    elif res_1 == new_res[2][0]:
        news.append([new_res[0][0], new_res[0][1]])
        news.append([new_res[1][0], new_res[1][1]])
        return news
    elif res_1 == new_res[3][0]:
        news.append([new_res[0][0], new_res[0][1]])
        news.append([new_res[1][0], new_res[1][1]])
        news.append([new_res[2][0], new_res[2][1]])
        return news
    else:
        return new_res

def checking_abo(rech_id, mail_id):
    """
    Vérifie qu'une recherche est toujours
    suivie, sinon elle est supprimée.
    Vérifie qu'une Personne a au moins un 
    abonnement, sinon elle est supprimée
    :param rech_id, mail_id 
    :return: nbre d'abonnés
    """
    abonnes_nbr = suivi_par(rech_id)
    abonnements_nbr = abonne_a(mail_id)
    if abonnes_nbr == []:
        delete_rech(rech_id)
    if abonnements_nbr == []:
        delete_mail(mail_id)


def monitoring():
    for el in Recherches.select():
        time.sleep(1)  # Gently crawling
        if el.type_rech == 'legifr': # Legifrance
            new_legif = scr.legifr_spider(el.opt_1)
            if new_legif[0][0] == el.res_1:  # No new results
                continue
            else:
                new = compare(new_legif, el.res_1)
                new.append(el.opt_1)
                mail.manage_mail(new, el.id, el.opt_1, el.user_name)
                #update_rech(el.id, new_legif)
        elif el.type_rech == 'g29': # G29
            if el.opt_1 == 'Communiqués de presse':
                new_g29 = scr.g29_pressrelease()
            elif el.opt_1 == 'Communications':
                new_g29 = scr.g29_letters()
            elif el.opt_1 == 'Avis & Opinions':
                new_g29 = scr.g29_opinions()
            if new_g29[0][0] == el.res_1:
                continue
            else:
                new = compare(new_g29, el.res_1)
                mail.manage_mail(new, el.id, 'G29 - '+el.opt_1)
                #update_rech(el.id, new_g29)
        """
        elif el.type_rech == 'cgu':
            print('in !!')
            if el.opt_1 == 'amazon_aws_aup':
                title = "Amazon Web Services - Acceptable Use Policy"
                date, new_res = scr.aws_cgu()
            elif el.opt_1 == 'amazon_aws_st':
                title = 'Amazon Web Services - Service Terms'
                date, new_res = scr.aws_ser_term()
            elif el.opt_1 == 'facebook_terms':
                title = 'Facebook - Droits et Obligations'
                date, new_res = scr.fb_terms()
            else:
                continue
            if date == el.res_1:
                continue
            else:
                old_res = misc.csv_reader(el.opt_1)
                new_table = misc.compare_html(new_res, old_res)
                update_cgu(el.id, el.opt_1, new_res, date)
                misc.html_writer(el.opt_1, new_table, el.res_1, date, title)
        """

# - Fonctions sur l'index d'Abonnements -------------->>>>

def abonne_a(mail_id):
    """
    Fonction qui renvoie une liste de toutes les
    recherches auxquelles est abonné un utilisateur
    :param mail_id: identifiant d'un Mail
    :return: liste des rech_id
    """
    rech_id = []
    l = (Recherches
         .select()
         .join(Abonnements, on=Abonnements.recherche)
         .where(Abonnements.personne == mail_id))
    for el in l:
        rech_id.append(el.id)
    return rech_id


def mailTOrech(mailDesc):
    """
    Fonction qui renvoie une liste de liste contenant
    l'ID, le n° et le nom de la recherche pour chaque 
    abonnement du mail en param.
    :param mailDesc: mail de la personne abonnée
    :return: [[1, 2012-300, Loi Jardé], [...]]
    """
    rech = []
    mail_id = Mails.select().where(Mails.mail_desc == mailDesc).get()
    l = (Recherches
         .select()
         .join(Abonnements, on=Abonnements.recherche)
         .where(Abonnements.personne == mail_id))
    for el in l:
        rech.append([el.id, el.opt_1, el.user_name])
    return rech, mail_id.id


def suivi_par(rech_id):
    """
    Fonction qui renvoie une liste de tous les
    utilisateurs qui suivent une recherche
    :param rech_id: identifiant d'une recherche
    :return: liste des mails_id
    """
    mail_id = []
    l = (Mails
         .select()
         .join(Abonnements, on=Abonnements.personne)
         .where(Abonnements.recherche == rech_id))
    for el in l:
        mail_id.append(el.id)

    return mail_id


def suivi_par_mail(rech_id):
    """
    Returns a list of lists with mail_id, mail_desc
    ex : [ [1, abc@xy.z], [2, def@uv.w]]
    :param rech_id:
    :return:
    """
    mails = []
    l = (Mails
         .select()
         .join(Abonnements, on=Abonnements.personne)
         .where(Abonnements.recherche == rech_id))
    for el in l:
        mails.append([el.id, el.mail_desc])
    return mails

# - Création des Objets PERSONNES (Mails) ------------------>


def add_mail(_mail):
    try:
        with database.transaction():
            new_mail = Mails.create(mail_desc=_mail)
            return new_mail.id
    except IntegrityError:
        return Mails.get(Mails.mail_desc == _mail).id


# Création des Objets RECHERCHES ------------------>

def add_cgu(cgu_id, content, date, name):
    try:
        with database.transaction():
            new_cgu = Recherches.create(type_rech='cgu',
                                        opt_1=cgu_id,
                                        user_name='',
                                        res_1=date,
                                        res_1_url='',
                                        res_2='',
                                        res_2_url='',
                                        res_3='',
                                        res_3_url='',
                                        res_4='',
                                        res_4_url='',
                                        res_5='',
                                        res_5_url=''
                                        )
            misc.csv_writer(cgu_id, content)
            comp = misc.compare_html(content, content)
            misc.html_writer(cgu_id, comp, date, date, name)
            return new_cgu.id
    except IntegrityError:
        print('INTEGRITY ERROR')
        return Recherches.get(Recherches.opt_1 == cgu_id).id


def add_instit_rech(rech):
    try:
        with database.transaction():
            new_g29 = Recherches.create(type_rech='Institutions',
                                        opt_1=rech[5][0],
                                        user_name=rech[5][1],
                                        res_1=rech[0][0],
                                        res_1_url=rech[0][1],
                                        res_2=rech[1][0],
                                        res_2_url=rech[1][1],
                                        res_3=rech[2][0],
                                        res_3_url=rech[2][1],
                                        res_4=rech[3][0],
                                        res_4_url=rech[3][1],
                                        res_5=rech[4][0],
                                        res_5_url=rech[4][1])
            return new_g29.id
    except IntegrityError:
        return Recherches.get(Recherches.opt_1 == rech[5]).id


def add_legifr_rech(usr_name, rech, id_rech):
    try:
        with database.transaction():
            new_rech = Recherches.create(type_rech='legifr',
                                         opt_1=id_rech,
                                         user_name=usr_name,
                                         res_1=rech[0][0],
                                         res_1_url=rech[0][1],
                                         res_2=rech[1][0],
                                         res_2_url=rech[1][1],
                                         res_3=rech[2][0],
                                         res_3_url=rech[2][1],
                                         res_4=rech[3][0],
                                         res_4_url=rech[3][1],
                                         res_5=rech[4][0],
                                         res_5_url=rech[4][1])
            return new_rech.id

    except IntegrityError:
        return Recherches.get(Recherches.opt_1 == rech[5]).id


# Lien entre les RECHERCHES et les PERSONNES ----------->

"""
def new_cgu_rech(CGUtype, mail):
    new_mail = add_mail(mail)
    if CGUtype == 'amazon_aws_aup':
        name = 'Amazon Web Services - Acceptable Use Policy'
        date, content = scr.aws_cgu()
    elif CGUtype == 'amazon_aws_ca':
        name = 'Amazon Web Services - Customer Agreement'
        date, content = scr.aws_cust_agr()
    elif CGUtype == 'amazon_aws_st':
        name = 'Amazon Web Services - Service Terms'
        date, content = scr.aws_ser_term()
    elif CGUtype == 'facebook_pp':
        name = 'Facebook - Privacy Policy'
        date, content = scr.fb_privacy()
    elif CGUtype == 'facebook_terms':
        name = 'Facebook - Déclaration des Droits et Responsabilités'
        date, content = scr.fb_terms()

    new_rech = add_cgu(CGUtype, content, date, name)
    try:
        with database.transaction():
            abo = Abonnements.create(recherche=new_rech, personne=new_mail)
    except IntegrityError:
        print('problème dans la table abonnement CGU')
"""

def new_legifr_rech(user_name, rech, mail, id_rech):
    new_rech = add_legifr_rech(user_name, rech, id_rech)
    new_mail = add_mail(mail)
    try:
        with database.transaction():
            abo = Abonnements.create(recherche=new_rech, personne=new_mail)
    except IntegrityError:
        print('problème dans la table abonnement legifr')


def new_instit_rech(rech, mail):
    # I would like this bloc to be
    # handled by a single specific function (a sorting function)
    print(rech)
    if rech == 'WP29_communiques':
        res = scr.g29_pressrelease()
    elif rech == 'WP29_communications':
        res = scr.g29_letters()
    elif rech == 'WP29_avis':
        res = scr.g29_opinions()
    elif rech == 'cnil_comm':
        res = scr.cnil_communiques()
    elif rech == 'cnil_actu':
        res = scr.cnil_actualites()

    new_rech = add_instit_rech(res)
    new_mail = add_mail(mail)
    try:
        with database.transaction():
            abo = Abonnements.create(recherche=new_rech, personne=new_mail)
    except IntegrityError:
        print('problème dans la table abonnement Institutions')


def suivre_rech(_mail, id_rech):
    new_mail = add_mail(_mail)
    try:
        with database.transaction():
            abo = Abonnements.create(recherche=id_rech, personne=new_mail)
    except IntegrityError:
        print('problème dans la table abonnement')

# Extraction de données spécifiques : ------->>>>>>


def accueil_data():
    """
    Returns data for the "acceuil.html" table and pill(s)
    :param
    :return lst_r : all recherche | number : data
    """
    lst_r = {}
    number = []
    users = []
    for rech in Recherches.select():
        if rech.type_rech == 'legifr':
            lst_r[rech.user_name] = [rech.opt_1,
                                     rech.res_1,
                                     rech.res_1_url,
                                     rech.id]
        """
        elif rech.type_rech == 'Institutions':
            lst_r[rech.user_name] = [rech.opt_1,
                                     rech.res_1,
                                     rech.res_1_url,
                                     rech.id]
        
        elif rech.type_rech == 'cgu':
            if rech.opt_1 == 'amazon_aws_aup':
                lst_r['Acceptable Use Policy'] = ['AWS',
                                                  'Dernière MàJ : '+rech.res_1,
                                                  'http://antoninp.pythonanywhere.com/cgu/'+rech.opt_1,
                                                  rech.id]
            elif rech.opt_1 == 'amazon_aws_st':
                lst_r['Service Terms'] = ['AWS',
                                          'Dernière MàJ : '+rech.res_1,
                                          'http://antoninp.pythonanywhere.com/cgu/'+rech.opt_1,
                                          rech.id]
            elif rech.opt_1 == 'amazon_aws_ca':
                lst_r['Customer Agreement'] = ['AWS',
                                          'Dernière MàJ : '+rech.res_1,
                                          'http://antoninp.pythonanywhere.com/cgu/'+rech.opt_1,
                                          rech.id]
            elif rech.opt_1 == 'facebook_pp':
                lst_r['Privacy Policy'] = ['Facebook',
                                          'Dernière MàJ : '+rech.res_1,
                                          'http://antoninp.pythonanywhere.com/cgu/'+rech.opt_1,
                                          rech.id]
            elif rech.opt_1 == 'facebook_terms':
                lst_r['Droits et Responsabilités'] = ['Facebook',
                                          'Dernière MàJ : '+rech.res_1,
                                          'http://antoninp.pythonanywhere.com/cgu/'+rech.opt_1,
                                          rech.id]
            else:
                continue
        """
    number.append(len(Recherches.select()))
    users.append(len(Mails.select()))
    return lst_r, number, users

if __name__ == '__main__':
    monitoring()
