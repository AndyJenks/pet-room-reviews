DROP TABLE IF EXISTS Rooms;
DROP TABLE IF EXISTS Staircases;
DROP TABLE IF EXISTS LegacyStars;
DROP TABLE IF EXISTS Reviews;

-- Staircases or houses live in courts or streets
CREATE TABLE IF NOT EXISTS Staircases (
	id INT(7) NOT NULL AUTO_INCREMENT,
	name varchar(255),
	abbr varchar(255),
	PRIMARY KEY (id),
	UNIQUE (abbr)
);

DELETE FROM Staircases;
INSERT INTO Staircases(abbr, name) VALUES 
	("FWS16", "16 Fitzwilliam Street"),
	("FWS17", "17 Fitzwilliam Street"),
	("FWS19", "19 Fitzwilliam Street"),
	("FWS22", "22 Fitzwilliam Street"),
	("PS24", "24 Parkside"),
	("PS30", "30 Parkside"),
	("TS35", "35 Trumpington Street"),
	("TS39", "39 Trumpington Street"),
	("TCT7", "7 Tennis Court Terrace"),
	("B", "B Staircase"),
	("C", "C Staircase"),
	("D", "D Staircase"),
	("G", "G Staircase"),
	("H", "H Staircase"),
	("I", "I Staircase"),
	("K", "K Staircase"),
	("L", "L Staircase"),
	("M", "M Staircase"),
	("FC", "Fen Court"),
	("Nark", "Noah's Ark"),
	("LSMH", "Little St Mary's Hostel"),
	("Hostel", "Hostel"),
	("Whittle", "Whittle"),
	("WSB", "William Stone Building");

CREATE TABLE IF NOT EXISTS Rooms ( 
id INT(7) NOT NULL AUTO_INCREMENT,
abbr VARCHAR(255) UNIQUE,
on_ballot BOOL DEFAULT 0,
available BOOL DEFAULT 0,
approved BOOL DEFAULT 0,
claimant VARCHAR(255),
longname VARCHAR(255),
localname VARCHAR(255),
sortby VARCHAR(255),
staircase VARCHAR(255),
ensuite BOOL DEFAULT 0,
doubleset BOOL DEFAULT 0,
has_sink BOOL DEFAULT 0,
gyp_has_hob BOOL DEFAULT 0,
fire_warden BOOL DEFAULT 0,
extended BOOL DEFAULT 0,
extended_only BOOL DEFAULT 0,
cost SMALLINT,
cost_extended SMALLINT,
doubleset_cost_a SMALLINT,
doubleset_cost_b SMALLINT,
general_comments TEXT,
additional_comments TEXT,
PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS Reviews ( 
id INT(7) NOT NULL AUTO_INCREMENT,
date DATE,
room_id VARCHAR(255),
approved BOOL DEFAULT 0,
username VARCHAR(255),
summary TEXT,
text TEXT,
cost SMALLINT,
is_legacy BOOL DEFAULT 0,
noise_night INT,
noise_day INT,
temperature INT,
daylight INT,
storage INT,
gyp_facilities INT,
gyp_cupboard INT,
bike_storage INT,
room_view INT,
room_condition INT,
laundry INT,
n_gyp INT,
n_shower INT,
n_toilet INT,
deleted BOOL DEFAULT 0,
deleted_date DATE,
deleted_username VARCHAR(255),
PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS LegacyStars (
id INT(7) NOT NULL AUTO_INCREMENT,
review_id INT(7),
overall INT,
kitchen INT,
bathroom INT,
size INT,
PRIMARY KEY (id),
FOREIGN KEY (review_id) REFERENCES Reviews(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS RoomReviewAdmins (
id INT(7) NOT NULL AUTO_INCREMENT,
name VARCHAR(255),
PRIMARY KEY (id));
