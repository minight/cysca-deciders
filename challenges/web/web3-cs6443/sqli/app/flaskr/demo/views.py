from flask import render_template, request, render_template_string, current_app, session, Response
from . import app
from flaskr import db
import time

@app.route('/')
def home():
    return render_template("home.html")

@app.route("/robots.txt")
def robots():
    xml ='''User-agent: *

Disallow: /db-debug
Flag: {}
'''.format(current_app.config.get("FLAG2", "notflag{contact_sean_this_shouldnt_happen}"))
    return Response(xml, mimetype='text/plain')

@app.route("/db-debug")
def databasedebug():
    query = request.args.get("query", None)

    msg = []
    if query is None:
        msg.append("no query parameter found. default query used: 'select version()'")
        query = "select version()"
    else:
        query = filter_sql(query)

    d, a = {}, []
    try:
        resp = db.engine.execute(query)
        ## data = list(query)
        for rowproxy in resp:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            d = {}
            for tup in rowproxy.items():
                # build up the dictionary
                d = {**d, **{tup[0]: tup[1]}}
            a.append(d)
            break
    except Exception as e:
        msg.append("error: " + str(e))

    return render_template("db.html", msg = msg, data = a)

def filter_sql(data):
    filter_chars = ['`', "'", '"']
    for c in filter_chars:
        data = data.replace(c, "\\" + c)

    data = data.replace(" ", "NOSPACES")
    data = data.replace("admin", "NO CHEATING")
    return data
