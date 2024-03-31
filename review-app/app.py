# app.py - (C) Andrew Jenkins 2022-23
# Flask web app to accept and approve room reviews.

# The reviews themselves are hosted on static pages, which must be updated from time to time.

import os
import random
import sys
from datetime import datetime
from collections import namedtuple

import questions

try:
    import MySQLdb
    print("Using MySQLdb")
except ImportError:
    import pymysql
    print("Using pymysql")
    pymysql.install_as_MySQLdb()
    import MySQLdb
    print("(installed pymysql as MySQLdb)")

from flask import Flask, request, render_template, redirect, url_for, session, g
from werkzeug.exceptions import NotFound, Forbidden

import config # secrets! defines DB_USER, DB_PASSWORD, DB_DATABASE

app = Flask(__name__)

app.secret_key = config.APP_KEY
MONTHS = ["January", "February", "March", "April", "May", "June", "July", 
          "August", "September", "October", "November", "December"]


DEBUG = False

# TODO: Add cost question with extended checkbox

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        print("creating database connection")
        db = g._database = MySQLdb.connect(user=config.DB_USER, passwd=config.DB_PASSWORD, db=config.DB_DATABASE)

    return db

def get_csrf_token():
    return secrets.token_urlsafe()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        print("closing database")
        db.close()


def get_remote_user(request):
    # since it doesn't "Just Work"
    user = request.remote_user
    if user is None:
        # I think this works since it should only be coming from the logged in user as added by the .htaccess, and I tried passing X-Whom with another username while logged and it didn't work
        # But it might be wrong because I'm sure logging in 'just worked' before Dec 2023.
        user = request.headers.get("X-Whom")
        print("X-Whom:", user)

    return user


def can_submit_review(user):
    ## TODO: check user is allowed to leave a review (is current student/was petrean)
    return True


def is_admin(user):
    # for the moment it's necessary to add users manually to the RoomReviewAdmins table in the database.
    d = get_db()
    c = d.cursor()

    c.execute("SELECT name FROM RoomReviewAdmins")
    admins = [i[0] for i in c.fetchall()]

    print("admins:", admins)
    print("vs", user)

    return user in admins or DEBUG


def store_review(user, room, summary, text, timestamp, multichoice=None):
    # N.B. This function does NOT check that the review is allowed to be
    # submitted or that the data is valid/sanitized

    d = get_db()
    c = d.cursor()

    c.execute("INSERT INTO Reviews(username, date, room_id, summary, text) VALUES (%s, %s, %s, %s, %s)", (user, timestamp, room, summary, text))
    review_id = c.lastrowid
    if multichoice:
        # create a copy of the dict so that a review_id entry can be
        # added to this one.
        qa1 = {q: a for q, a in multichoice.items()}
        qa1["review_id"] = review_id
        # this trusts the question ids not to contain sql injection
        # (since we created them) but not the answers given.
        c.execute("UPDATE Reviews SET {} WHERE id=%(review_id)s".format(",".join("{0}=%({0})s".format(name) for name in multichoice)), qa1)

    d.commit()

def clean_multichoice(formdata):
    output = {}
    # question id, question text, answers
    for q, qq, a in questions.multi_choice:
        val = formdata.get(q)
        try:
            iv = int(val)
            # TODO: a better mapping between the question and answer.
            # What if we change the questions, for example?

            # the output is the index of the question if and only if that index is valid.
            output[q] = iv if iv < len(a) else None

        except (ValueError,TypeError):
            output[q] = None


    return output

def room_exists(room_id):
    if room_id is None:
        return False

    d = get_db()
    c = d.cursor()

    c.execute("SELECT id FROM Rooms WHERE abbr=%s", (room_id,))
    return bool(len(c.fetchall()))


DBReview = namedtuple("DBReview", ("review_id", "room_id", "summary", "date", "text", "username"))
def render_admin_page(username, message=None):

    d = get_db()
    c = d.cursor()
    c.execute("SELECT id,room_id,summary,date,text,username FROM Reviews WHERE (approved=0 AND deleted=0)")

    reviews = [DBReview(*r) for r in c.fetchall()]

    for i,r in enumerate(reviews):
        paras = [l.strip() for l in sanitize(r.text).split("\n")]
        reviews[i] = r._replace(text=(paras))
    
    return render_template("adminpage.htm", username=username, reviews=reviews, message=message)

def check_approve_form(username, form):
    print(form)

    # which ones are actually not approved yet?

    d = get_db()
    c = d.cursor()
    c.execute("SELECT id, room_id FROM Reviews WHERE approved=0")

    ids = [(i[0]) for i in c.fetchall()]

    to_approve = []
    to_delete = []
    for i in ids:
        action = form.get(str(i))
        if action=="a":
            to_approve.append((i,)) 
        elif action =="d":
            to_delete.append((i,))

    c.executemany("UPDATE Reviews SET approved=1 WHERE id=%s", to_approve)
    today = datetime.today()
    for i in to_delete:
        c.execute("UPDATE Reviews SET deleted=1,deleted_username=%s,deleted_date=%s WHERE id=%s", (username, today,i))
    d.commit()

    
    return render_admin_page(username, message="Approved {} and deleted {} reviews".format(len(to_approve), len(to_delete)))



def sanitize(text):
    if text is None:
        return None
    else:
        # thank you to https://stackoverflow.com/a/11550901
        escapes = {#'\"': '&quot;',
                   #'\'': '&#39;',
                   '<': '&lt;',
                   '>': '&gt;'}
        text = text.replace("&", "&amp;")
        for seq, esc in escapes.items():
            text = text.replace(seq, esc)
        return text

    
@app.route("/",methods=["GET","POST"])
def review():
    #print("Request from host", request.host)
    username = get_remote_user(request)
    if username is None:
        username = "Anonymous"

    if request.method == "POST":
        if not can_submit_review(username):
            return "User not authorised to submit review. Are you a Petrean?"
        room = sanitize(request.form.get("room"))
        if (not room) or not room_exists((room)):
            return "No room or invalid room specified. The room was {}. This is probably a bug -- contact the admin.".format(repr(room))

        summary = sanitize(request.form.get("summary"))
        if not summary:
            return "Fail: no summary/title was given"
        if "text" in request.form:
            body = sanitize(request.form["text"])
        else:
            body = None

        ts = datetime.now()
        multichoice = clean_multichoice(request.form)
        store_review(username, room, summary, body, ts, multichoice)
        return "Room review has been saved and will be reviewed by page admin"
    else:
        room_id = request.args.get("room")
        return render_template("form.htm", room_id=room_id, username=username, room_name=room_id)

@app.route("/adm", methods=["GET", "POST"])
def admin():
    user = get_remote_user(request)
    if is_admin(user):
        username = user
    else:
        return "You are not an admin.", 403

    if request.method == "POST":
        return check_approve_form(username, request.form)
    else:
        return render_admin_page(username)

