from flask import render_template, request, redirect, current_app, Flask, flash, url_for, Response, session
from . import app
import urllib.parse
import socket
import requests
import base64

from .models import User
from flaskr import db

def get_hostname(full_url):
    url = urllib.parse.urlparse(full_url)
    hostname = url.netloc.split(":")[0]
    return hostname

@app.after_request
def per_request_callbacks(response):
    response.headers['X-Server'] = current_app.config.get("THIS_IP").strip()
    response.headers['FLAG'] = current_app.config.get("FLAG1").strip()
    return response

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method=='POST':
        return render_template("homefake.html")
    return render_template("home.html")


@app.route("/robots.txt")
def robots():
    xml ='''User-agent: *

Disallow: /twooter
'''
    return Response(xml, mimetype='text/plain')

@app.route("/twooter")
def notflag():
    return render_template("notflag.html")


def aws_check_get(res):
    print("fetching", res)
    bad_list = ["169.254.169.254"]
    hostname = get_hostname(res)
    print("hostname", hostname)
    if socket.gethostbyname(hostname) in bad_list:
        flash("stop trying to be evil. that's not in scope")

    # manually handle redirects for aws the bad_list
    url = res
    print("now fetching", url)
    fake_headers = dict(request.headers)
    bad_headers = ['Host', 'Content-Length', 'Cache-Control', 'Origin', 'Content-Type', 'Accept', 'Connection']
    for h in bad_headers:
        if h in fake_headers:
            del fake_headers[h]
    print(fake_headers)
    while True:
        # Like every good proxy we forward ALL the user headers
        r = requests.get(url, allow_redirects=False, headers=fake_headers)
        print("r returned")
        if not r.is_redirect:
            break

        url = r.headers['Location']
        print("next vising {}".format(url))
        if get_hostname(url) in bad_list:
            flash("stop trying to be evil. that's not in scope")
            return redirect(url_for("app.home"))

    print("finished ", r)
    return r


@app.route("/profile", methods=["GET", "POST"])
def profile():
    cur_user = None

    picture_data = ''
    if not cur_user:
        if not session.get("user"):
            flash("Please log in")
            return redirect(url_for("app.login"))
        cur_user = User.query.filter_by(username=session['user']).first()

    if request.method == "POST":
        # fetch profilepicture data
        try:
            url = request.form.get("profile_picture_url", "https://ih1.redbubble.net/image.161325777.9441/flat,800x800,075,t.u1.jpg")
            # Make it easier lol
            #imagetypes = ['jpg', 'png', 'svg', 'gif', 'bmp']
            #for ft in imagetypes:
            #    if url.endswith(ft):
            #        break
            #else:
            #    flash("Not a recognised image filetype")
            #    return render_template("profile.html", user=cur_user)


            r = aws_check_get(url)
            print(r)

            profile_picture_data = base64.b64encode(r.content)
            cur_user.profile_picture_data = profile_picture_data
            db.session.add(cur_user)
            db.session.commit()
            flash("Profile updated")
        except Exception as e:
            flash(e)
    return render_template("profile.html", user = cur_user)

@app.route("/logout")
def logout():
    session['user'] = None
    session.clear()
    return redirect(url_for("app.login"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("user"):
        flash("you are already logged in")
        return(redirect(url_for("app.profile")))


    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")


        if not username or not password:
            flash("Please have enter both a username and password")
            return render_template("register.html")

        cur_user = User.query.filter_by(username = username, password = password).first()
        if not cur_user:
            flash("Invalid username and password")
            return render_template("login.html")

        session['user'] = cur_user.username
        flash("Login successful")
        return redirect(url_for("app.profile"))

    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get("user"):
        flash("you are already logged in")
        return(redirect(url_for("app.profile")))

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Please have both a username and password")
            return render_template("register.html")

        # check existence of username
        check_user = User.query.filter_by(username = username).all()
        if check_user:
            flash("Username already registered")
            return render_template("register.html")

        new_user = User(username=username, password=password, profile_picture_data=b'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAAAAACPAi4CAAACD0lEQVRYw+2WIbKsMBBFr0VGx+Px+GyAJaBZADtgAbiRSBxuBGIMCotCIrExEblPEHgwE+rx61c98T/tptI509253Q34l4YbcANuwL8L0K25dLOb/ADbIxquAFSQW28ETyCcLwBioPQCTA0UP9+3s4LQ/iImiC9EYAeg9QMKRFeKoAVqP0BBXXoGoCNBmulgY7FU5zPpo18XQhoS5AvvFumTsr9ZRT8gmXgFICsnpLltcwBR0bRVKoBY+3Pu22cIiLRqmyIGUH8rsQsgKkuSnBIgOdGyTbbobC0QvFaADiH6TUepv4YkH0C6sXuBUDtAuZRjJUSQ3iS0PFTXCRakjRDZnWOzpvdmDdDsE1qugZyd9k2e9CRpAmQ+QIZAk2Sf5GYRLGYSZO/+sYGLJPIrUW3HSyTNqsQX8HR9HLsHj/06WI83/9cawYMk7SMbSdLKswikJckxe1j3KD0JUgPJ3nEAch8gB4Zj18PNgxjBuDtIXYieUZXufo4BYqeDx0G+DRB6pWjC/TvqeMkci3Sg1jFYBycyIGsgWI9mBURm7YVBALKcjNVdAiCzJ72QAUhe2pqplIAYvsd6JwAEUgpgr/ePJFIAEFIGAES33wujWrtclPZ8jtpSrH5qPG4m26ahEFIVP6yEuVBSiDBt7edqs1pfWmpGa/sL2/lZvdnzDwEfIzj+7Qjuj6wbcAP+P8AXpzZqUKBcnewAAAAASUVORK5CYII=')
        db.session.add(new_user)
        db.session.commit()

        flash("New user registered")
        return redirect(url_for("app.login"))

    return render_template("register.html")
