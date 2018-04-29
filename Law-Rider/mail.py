#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import operations as op
import requests
from flask import current_app as app
from itsdangerous import URLSafeSerializer
from flask import url_for, render_template


def unsub_URL(mail):
    """
    Builds a safe url to unsubscribe
    :param mail: mail adress as a string
    :return: url associated with the token
    """
    s = URLSafeSerializer(app.config['SECRET_KEY'], salt='unsubscribe')
    token = s.dumps(mail)
    url = url_for('desabonnement', token=token)
    return url


def manage_mail(res, rech_id, title, user_name):
    users = op.suivi_par_mail(rech_id)
    for el in users:
        html = mail_builder(res, title, user_name, unsub_URL(el))
        mail_sender(html, el, title)


def mail_sender(myhtml, user, title):
    key = 'YOUR MAILGUN KEY HERE'
    request_url = 'https://api.mailgun.net/v3/sandbox7557916c81ae483dbc9551350d247d55.mailgun.org/messages'
    request = requests.post(
        request_url,
        auth=('api', key),
        data={
            'from': 'law.Rider() <maj@law-rider.fr>',
            'to': user,
            'subject': 'MàJ: '+title,
            'html': myhtml
        }
    )

    print 'Status: {0}'.format(request.status_code)
    print 'Body:   {0}'.format(request.text)


def mail_builder(news, title, user_name, url):
    del news[-1]  # Supprime le numéro de recherche, sinon il sort dans le mail
    html = render_template(
        'MAIL_mainV2.html',
        title=title,
        data=''.join(['<li style="padding-bottom:10px;"><a href=\"' + el[1] + '\">' + el[0] + '</a></li>' for el in news]),
        user_name=user_name,
        url=url,
    )
    return html

