#!/usr/bin/env python
# -*- coding: utf-8 -*-

# author : Antonin Paillet <antoninpa> at <gmail.com>
# licence : Creative Commons - Non commercial - By - Share Alike


import data
from flask import Flask, render_template, request, send_file, redirect, url_for
from peewee import SqliteDatabase


database = SqliteDatabase('./data2.sqlite')
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def accueil():
    if request.method == 'POST':
        id_loi = request.form.get('id_loi')
        if 'feed_name' in request.form:  # 
            legif_res_list = data.text_results(id_loi)
            data.create_feed(id_loi, legif_res_list)
            data.create_entry(id_loi, request.form.get('feed_name'), request.form.get('feed_jo'), legif_res_list[0])
            return render_template('accueil.html', my_data=data.read_all())
        else:
            err = data.valid_input_number(request.form.get('id_loi'))
            if err is '':
                if data.check_exists(request.form.get('id_loi')) is False:
                    texte_name = data.text_full_name(id_loi)
                    if len(texte_name) == 1:
                        legif_res_list = data.text_results(id_loi)
                        data.create_feed(id_loi, legif_res_list)
                        data.create_entry(id_loi, texte_name[0][0], texte_name[0][1], legif_res_list[0])
                        return render_template('accueil.html', my_data=data.read_all())
                    else:
                        return render_template('accueil.html', feed_names=texte_name, id_loi=id_loi)
                else:
                    return redirect(url_for('accueil', my_data=data.read_all(), _anchor=id_loi))
            else:
                return render_template('accueil', errors=err)
    else:
        return render_template('accueil.html', my_data=data.read_all())


@app.route('/feeds/<feed>/<feed_id>')
def feeds(feed, feed_id):
    return send_file('./data/{}/{}.xml'.format(feed, feed_id))


@app.route('/about')
def about():
    return render_template('about.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.before_request
def _db_connect():
    database.connect()


@app.teardown_request
def _db_close(exc):
    if not database.is_closed():
        database.close()


if __name__ == "__main__":
    app.run()
