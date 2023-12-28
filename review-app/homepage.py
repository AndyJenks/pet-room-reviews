import MySQLdb
import config

PAGE_TEMPLATE = """<!doctype html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="generator" content="Andy's ad-hoc static site generator">
	<style>
body{{
	max-width: 800px;
	margin: 0 auto;
	padding: 0 5px;
	font-family: sans-serif;
}}
section{{
	border-radius: 5px;
	padding: 15px;
	margin-bottom: 10px;
}}

	</style>
	<title>Peterhouse Room Reviews</title>
</head>
<body>
	<h1>Peterhouse Undergraduate Room Reviews</h1>
	<section id="notice" style="border: 3px solid red;">
	<h2 style="color: red; margin: 10px auto; text-align: center;"> VERY IMPORTANT NOTICE </h2>
	<p> The information on this site has been lifted from the JCR room
	selection site, the 2020-2021 room review Google doc, and a few reviews left on this site since then.</p>
	<p>
	The Accommodation Office weren't happy with the JCR room site because a
	number of the reviews and photos were outdated, and people then
	complained when it transpired rooms had been refitted or furniture had
	changed, or rooms were not on the ballot, etc.</p>
	<p> However, I am of the opinion that the old reviews are fun and are of historical
	interest, so I've put them up here. I haven't included the photos,
	mainly to make my own life easier.</p>
	<p>If you continue to read these reviews, you should understand that:</p>
	<ul><li><strong>this is	historical information which may no longer be
				relevant</strong></ul>
	<ul><li><strong>some of the rooms listed here may not be on the
				ballot</strong></ul>
	<ul><li><strong>you should absolutely not complain to the Accommodation
				Office, JCR, etc. about the room you choose on
				the basis of ANY information here</strong></ul>
	<p> If any part of this site is broken (which is quite likely), or you want to correct
    some wrong information, or add a missing room to the site, I can be reached at <a href='mailto:adj35@srcf.net'> adj35@srcf.net</a> or the same CRSID at <code>cantab.ac.uk</code> </p>
	</section>
	<section id="historical" style="border: 3px solid gold;">
	<h2 style="color: black; margin: 10px auto; text-align: center;">
		Historical notes </h2>
	<p> Before 2015 the JCR used to be just above the MCR in what is now the
	lower floor of Noah's Ark. It then moved to the Davidson Room in Whittle
	before its current location in the Nightingale Room. As such references
	to JCR proximity and noise are among the most likely to be outdated.</p>
	<p> In summer 2021: Fitz Street bedrooms were redecorated with some
	getting new furniture. H5 and H6 were refurbished. G staircase got a
	new bathroom and gyp. </p>
    <p> In summer 2022: Noah's Ark got new gyp and bathrooms. 38
    Trumpington St new to ballot (not on this site yet). New furniture in 19 and 22 Fitz Street.
    </p> </section>
	
    <h2> Quick links (click to jump down) </h2>
    <ul>
    {quicklinks}
    </ul>
	<h2>Staircases / Houses</h2>
    {staircases}
</body>
"""
QUICKLINK_TEMPLATE = """    <li><a href='#{abbr}'>{longname}</a></li>"""
STAIRCASE_TEMPLATE = """    <h3 id='{abbr}'>{longname}</h3>
        <ul>
{rooms}
        </ul>
"""
ROOM_TEMPLATE = """        <li><a href='rooms/{room_id}.html'>{room_id}</a>{set}{ensuite}</li>"""

db = MySQLdb.connect(user=config.DB_USER, passwd=config.DB_PASSWORD, db=config.DB_DATABASE)
cursor = db.cursor()
# first check that all the staircases exist

cursor.execute("SELECT abbr, name FROM Staircases ORDER BY id")

staircases = []
quicklinks = []
for abbr, name in cursor.fetchall():
    rooms = []
    cursor.execute("SELECT abbr, doubleset, ensuite FROM Rooms WHERE staircase=%s ORDER BY sortby", (abbr,))
    for r_id, doubleset, ensuite in cursor.fetchall():
        rooms.append(ROOM_TEMPLATE.format(room_id=r_id, 
            set=" <span class=\"set-indicator\">(SET)</span>" if doubleset else "",
            ensuite = " <span class=\"ensuite-indicator\">(En-suite)</span>" if ensuite else ""))
    staircases.append(STAIRCASE_TEMPLATE.format(abbr=abbr, longname=name, rooms="\n".join(rooms)))
    quicklinks.append(QUICKLINK_TEMPLATE.format(abbr=abbr, longname=name))

# Are there any rooms which are not appearing on the home page just because there is no name recorded for their staircase?
cursor.execute("SELECT DISTINCT staircase FROM Rooms WHERE staircase NOT IN (SELECT abbr FROM Staircases)")
for (staircase,) in cursor.fetchall():
    print("WARNING: No record in Staircases table for", staircase)


result = PAGE_TEMPLATE.format(quicklinks="\n".join(quicklinks), staircases="".join(staircases))
print(result)
