#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import re
import csv
import pandas as pd

def csv_writer(type, res):
    with open('./AppliWeb/CGU/'+type+'.csv', 'w') as csvfile:
        fieldname = [type]
        writer = csv.DictWriter(csvfile, fieldnames=fieldname)
        writer.writeheader()
        for el in res:
            writer.writerow({type: el})


def csv_reader(type):
    ret = []
    df = pd.read_csv('./AppliWeb/CGU/'+type+'.csv', encoding='utf-8')
    for el in df[type]:
        ret.append(el)
    return ret


def html_writer(type, html, new_date, old_date, title):
    with open('./AppliWeb/templates/CGU/'+type+'.html', 'w') as f:
        html_intro = """
        {% extends 'CGU.html' %}
        {% block container %}
        {% autoescape false %}
        """

        html_title="""
<div class='row'>
    <div class='col-lg-12'>
        <div class='bs-component'>
            <h2>{2}</h2>
            <table>
                <tr>
                    <td>
                        <p class='lead' style='text-align: left; color: #2c3e50;'>{0}</p>
                    </td>
                    <td>
                        <p class='lead' style='text-align: center; color: #2c3e50;'>{1}</p>
                    </td>
                </tr>
            </table>
        </div>
    </div>
</div>
        """.format(new_date, old_date, title)

        html_outro = """
        {% endautoescape %}

<div class="bs-docs-section">
    <div class="row">
        <div class="col-lg-12">
            <div class="bs-component">
</br></br></br>
</div></div></div></div>
{% endblock %}
        """
        f.write(html_intro)
        f.write(html_title)
        f.write(html)
        f.write(html_outro)
        f.close()


# Messages ------------------------------------->>>>>>>>>

def success_search_msg():
    msg = """La veille est bien enregistrée: vous serez averti s'il y a du nouveau !"""
    return msg

def mail_error_msg():
    msg = """Vous n'avez pas renseigné d'adresse mail ou son format n'est pas valide (RFC 5322 et RFC 5321)."""
    return msg


def name_error_msg():
    msg = """Vous n'avez pas donné de nom à votre recherche."""
    return msg


def id_error_msg():
    msg = """Le numéro du texte n'est pas renseigné ou son format n'est pas valide."""
    return msg


def G_mail_check(mail):
    errors = []
    print(mail)
    if str(mail) is '':
        errors.append(mail_error_msg())
    else:
        d = re.compile('[^@]+@[^@]+\.[^@]+').findall(str(mail))
        if not d:
            errors.append(mail_error_msg())
            return errors
        else:
            return errors
    return errors


def clean_rech(lst_return):
    clean = []
    if len(lst_return) >= 5:
        [clean.append(lst_return[x]) for x in xrange(0, 5)]
    elif len(lst_return) is 4:
        [clean.append(lst_return[x]) for x in xrange(0, 4)]
        clean.append(['', ''])
    elif len(lst_return) is 3:
        [clean.append(lst_return[x]) for x in xrange(0, 3)]
        clean.append(['', ''])
        clean.append(['', ''])
    elif len(lst_return) is 2:
        [clean.append(lst_return[x]) for x in xrange(0, 2)]
        clean.append(['', ''])
        clean.append(['', ''])
        clean.append(['', ''])
    elif len(lst_return) is 1:
        [clean.append(lst_return[x]) for x in xrange(0, 1)]
        clean.append(['', ''])
        clean.append(['', ''])
        clean.append(['', ''])
        clean.append(['', ''])
    return clean


def legifr_search_check(name, m_id, mail):
    errors = []
    def name_check():
        if str(name) is '':
            errors.append(name_error_msg())
        else:
            pass

    def id_check():
        if str(m_id) is '':
            errors.append(id_error_msg())
        else:
            d = re.match('(\d{2,4}-\d{1,4})', str(m_id))
            if d is None:
                return errors.append(id_error_msg())
            else:
                pass

    def mail_check():
        if str(mail) is '':
            errors.append(mail_error_msg())
        else:
            d = re.match('[^@]+@[^@]+\.[^@]+', str(mail))
            if d is None:
                return errors.append(mail_error_msg())
            else:
                pass
    name_check()
    id_check()
    mail_check()
    return errors

if __name__ == '__main__':
    compare_html()
