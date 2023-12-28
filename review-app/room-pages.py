import datetime
import os

import MySQLdb

from collections import namedtuple

import questions
import config

db = MySQLdb.connect(user=config.DB_USER, passwd=config.DB_PASSWORD, db=config.DB_DATABASE)

OUTPUT_DATA = "/home/andrew/Documents/Web/JCR_Room_review/site/rooms"
TEMPLATE = """\
<!doctype html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<!--<link rel="stylesheet" type="text/css" href="/style.css">-->
	<style>
body{{ 
	max-width: 800px;
	margin: 0 auto;
	padding: 0 5px;
	font-family: sans-serif;
}}
	</style>
	<title>{room.id} Review</title>
</head>
<body>
<a href="../#{room.staircase_id}"> &lt; back to list</a>
<h1> {room.longname} </h1>
<a href="../add-review?room={room.id}">Add your review for this room</a>
<h2> Reviews </h2>
{reviews}
</body>
"""

## with passed Review obj. Bin scores and q&a
REVIEW_FORMAT = """
<div class="reviewbox">
    <h3> {review.date} </h3>
    <h4> {review.summary} </h3>
    {review.text}
</div>"""

def pformat(s):
    paras = s.split("\n")
    return "\n".join(["<p>" + para + "</p>" for para in paras])


def format_review(r):

    line_lengths = [len(l) for l in r.text.split("\n") if len(l.strip()) > 0]
    if (len(line_lengths) > 1 and r.date < datetime.date(2014,1,1)):
        txt1 = r.text.replace("\r\n", "\n")
        #print(r.text)
        # to catch line break formatted ones
        mean_line_length = sum(line_lengths) / len(line_lengths)
        if (len(line_lengths) and mean_line_length < 80 and
            max(line_lengths) < 100):
            print("=====\n")
            print(r.summary)
            print(r.text)
            print("^^^^^^^^^^^^^^ WILL REFORMAT ^^^^^^^^^^^^^^^")
            thresh = mean_line_length - 10

            lines = txt1.split("\n")
            out = []
            for i,l in enumerate(lines):
                if i == 0 and l.startswith("This comment is imported"):
                    # always give the "this commment imported..." its own line
                    out.append(l + "\n")
                elif len(l) < thresh or l.startswith("-"):
                    out.append(l + "\n")
                else:
                    out.append(l.strip() + " ")
            
            r = r._replace(text="".join(out))
            print(r.text)

    if r.date <= datetime.date(2012,7,21):
        r = r._replace(date="2012 or earlier")
    r = r._replace(text=pformat(r.text))
    return REVIEW_FORMAT.format(review=r)

Review = namedtuple("Review", ("room_id", "summary", "date", "text", "scores", "qa"))
def reviews_for_room(r_id):
    c = db.cursor(MySQLdb.cursors.DictCursor)
    c.execute("SELECT * from Reviews WHERE room_id=%s ORDER BY date DESC", (r_id,))
    # these will be dicts
    records = c.fetchall()
    reviews = []
    for r in records:
        if r["is_legacy"]:
            c.execute("SELECT * FROM LegacyStars WHERE review_id=%s", (r["id"],))
            scores = c.fetchone()
        else:
            scores = None

        if any(r.get(x[0]) is not None for x in questions.multi_choice):
            # we have a qa section
            #print("multichoice ignored")
            qa = None
        else:
            qa = None

        reviews.append(Review(r["room_id"], r["summary"], r["date"], r["text"], scores, qa))

    return reviews

c2 = db.cursor()
c2.execute("SELECT Rooms.abbr, longname, staircase, Staircases.name, doubleset, ensuite FROM Rooms LEFT JOIN Staircases ON Rooms.staircase=Staircases.abbr ORDER BY Staircases.id")
Room = namedtuple("Room",("id", "longname", "staircase_id", "staircase_name", "doubleset", "ensuite"))

rooms = [Room(*r) for r in c2.fetchall()]

for r in rooms:
    fname = os.path.join(OUTPUT_DATA, r.id + ".html")
    reviews = reviews_for_room(r.id)
    review_txt = "".join([format_review(r) for r in reviews])
    page = TEMPLATE.format(room=r,
            reviews=review_txt)
    with open(fname, "x") as f:
        f.write(page)
