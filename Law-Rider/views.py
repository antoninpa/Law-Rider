#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import scraping
import misc
from itsdangerous import URLSafeSerializer, BadData
from AppliWeb import operations as op
from AppliWeb import app, SqliteDatabase
from flask import render_template, request


database = SqliteDatabase("/full/path/to/pw_DDB.sqlite")


@app.route('/', methods=['GET', 'POST'])
def accueil():
    entries, numbers, users = op.accueil_data()
    print(entries, numbers)
    if request.method == 'GET':
        return render_template('accueil.html', entries=entries, numbers=numbers, users=users)
    elif request.method == 'POST':
        error = misc.G_mail_check(request.form.get('mail'))
        if error is None:
            op.suivre_rech(request.form.get('mail'), request.form.get('id_r'))
            return render_template('accueil.html', entries=entries, numbers=numbers)
        else:
            return render_template('accueil.html', entries=entries, numbers=numbers, error=error)


@app.route('/about')
def about():
    return render_template('about.html')
    

@app.route('/legal')
def legal():
    return render_template('legal.html')


@app.route('/test')
def test():
    op.monitoring()
    return 'test'


@app.route('/fonctionnement')
def fonctionnement():
    return render_template('fonctionnement.html')


@app.route('/nvlle-rech', methods=['POST', 'GET'])
def nvlle_rech():
    if request.method == 'GET':
        return render_template('nvlle-rech.html')
    elif request.method == 'POST':
        # LEGIFRANCE
        if request.form.get('type_rech') == 'legifr':
            error = misc.legifr_search_check(request.form.get('nom_recherche'), request.form.get('id_loi'), request.form.get('mail'))
            if not error:
                op.new_legifr_rech(request.form.get('nom_recherche'), scraping.legifr_spider(request.form.get('id_loi')), request.form.get('mail'), request.form.get('id_loi'))
                return render_template('accueil.html', success=misc.success_search_msg())
            else:
                return render_template('nvlle-rech.html', error=error)
        return render_template('nvlle-rech.html')


@app.route('/desabonnement/<token>', methods=['GET', 'POST'])
def desabonnement(token):
    if request.method == 'GET':
        s = URLSafeSerializer(app.secret_key, salt='unsubscribe')
        try:
            email = s.loads(token)
        except BadData:
            print('Il y a une erreur de type BadData')
        rech, mail_id = op.mailTOrech(email[1])
        return render_template('remove_mail.html', rech=rech, mail_id=mail_id)
    elif request.method == 'POST':
        page_ids = request.form.getlist("to-delete")
        mailID = request.form.get('mail_id')
        for el in page_ids:
            op.delete_abo(el, mailID)
            op.checking_abo(el, mailID)
        bye = "C'est fait !"
        return render_template('remove_mail.html', bye=bye)


@app.errorhandler(403)
def page_forbidden(error):
    return "Cette section n'est pas ouverte au public."


@app.errorhandler(404)
def page_not_found(error):
    return "Oups, il n'y a rien sur cette page!"


@app.errorhandler(400)
def page_not_found(error):
    return "Mauvaise requête..."
