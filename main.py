#!/usr/bin/env python
# -*- coding: utf-8 -*-

import data
from flask import Flask, render_template, request, send_file, redirect, url_for

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def accueil():
    if request.method == 'POST':
        id_loi = request.form.get('id_loi')
        if 'feed_name' in request.form:
            legif_res_list = data.legifr_spider(id_loi)
            data.feed_gen(id_loi, legif_res_list)
            data.create_feed(id_loi, request.form.get('feed_name'), legif_res_list[0])
            return render_template('accueil.html', mydata=data.read_all())
        else:
            if data.legifr_search_check(request.form.get('id_loi')) is '':
                if data.check_exists(request.form.get('id_loi')) is False:
                    texte_name = data.get_texte_name(id_loi)
                    if len(texte_name) == 1:
                        legif_res_list = data.legifr_spider(id_loi)
                        data.feed_gen(id_loi, legif_res_list)
                        data.create_feed(id_loi, texte_name[0], legif_res_list[0])
                        return render_template('accueil.html', feeds_list=data.read_all())
                    else:
                        return render_template('accueil.html', feed_names=texte_name, id_loi=id_loi)
                else:
                    return redirect(url_for('accueil', my_data=data.read_all(), _anchor=id_loi))
    else:
        return render_template('accueil.html', my_data=data.read_all())


@app.route('/feeds/<feed>/<feed_id>')
def feeds(feed, feed_id):
    return send_file('./data/{}/{}.xml'.format(feed, feed_id))


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == "__main__":
    app.run()
