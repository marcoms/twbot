#!/usr/bin/env python3

# © 2016 Marco Scannadinari <m@scannadinari.co.uk>

import sys
import threading
import atexit
import pprint
import sqlite3 as sqlite

from urllib.parse import urlencode
from uuid import uuid4 as uuid

# frequently used modules aliased for convenience

import bottle as b
import tweepy as t

import bcrypt
import delorean as dmc
from docopt import docopt


import twbot_sql

__doc__ = """
twbot - Twitter Quiz Robot

Usage:
  {invok} help
  {invok} [--port <port>]

Options:
  -p <port>, --port <port>  Port to serve web interface at [default: 8080]

Written by Marco Scannadinari
""".format(invok=sys.argv[0]).strip()

req = b.request
resp = b.response

################################################################################
# FUNCTIONS BEGIN ##############################################################


def get_twbot_meta(c):
	"""
	get the contents of the meta table

	returns a dict object of the single meta table
	"""

	results = c.execute("SELECT * FROM meta;")
	if results:
		return dict(results.fetchone())
	else:
		raise RuntimeError("the database is incorrectly structured")


def get_is_logged_in(c):
	"""
	determine if the administrator is logged in

	returns True if logged in
	"""

	session = get_twbot_meta(c).get("session")
	cookie_session = req.get_cookie("session")

	if None in (session, cookie_session):
		return False

	return session == cookie_session


def logout(c):
	"""
	log the client out
	"""

	# remove the session UUID from the client and server

	resp.delete_cookie("session")
	c.execute("UPDATE meta SET session = NULL;")

	conn.commit()


def get_tpl_vars(c):
	"""
	get variables for templates to use

	returns a dict of variables
	"""

	tpl_vars = TPL_VARS_BASE.copy()
	meta = get_twbot_meta(c)

	# remove non-relevant data for templates
	meta.pop("id")

	# combine the two dicts
	tpl_vars.update(meta)

	tpl_vars["is_logged_in"] = get_is_logged_in(c)

	return tpl_vars


def hash_password(password):
	"""
	bcrypt hash a password
	"""

	salt = bcrypt.gensalt(SALT_ROUNDS)
	return bcrypt.hashpw(
		password=password,
		salt=salt,
	)


def password_matches(password, hashed):
	"""
	compare a cleartext password to a bcrypt-hashed one

	returns True if the password is a match

	args:
		password - cleartext password
		hashed   - bcrypt-hashed password
	"""

	if not isinstance(password, bytes) or not isinstance(hashed, bytes):
		raise RuntimeError("password and hashed must be bytes")

	# bcrypt uses built-in salts, so using the hashed password as the salt
	# parameter will yield the same hashed password if they match
	return bcrypt.hashpw(password, hashed) == hashed


def get_tables(c):
	"""
	return a list of tables in the database
	"""

	tables = c.execute("SELECT name FROM SQLITE_MASTER WHERE type = 'table';").fetchall()
	return [element["name"] for element in tables]


def get_twitter_api(c=None, keys=None):
	"""
	obtain a Twitter API instance
	"""

	if bool(c) == bool(keys):
		raise RuntimeError("either cursor or keys, not both, and not none!")

	if c:
		meta = get_twbot_meta(c)
		keys = {
			"api_key": meta["api_key"],
			"api_secret": meta["api_secret"],
			"access_key": meta["access_key"],
			"access_secret": meta["access_secret"],
		}

	auth = t.OAuthHandler(keys["api_key"], keys["api_secret"])
	auth.set_access_token(keys["access_key"], keys["access_secret"])

	return t.API(auth)


def get_points(player_id):
	print("points for", player_id)

	players = c.execute("SELECT * FROM players WHERE id = ?;", (player_id,)).fetchall()
	if not players:
		return None

	answers = c.execute("SELECT * FROM answers WHERE player_id = ?;", (player_id,)).fetchall()
	if not answers:
		return 0

	points = 0
	for answer in answers:
		print("found answer")

		answer = dict(answer)
		score = answer.get("score")
		if score:
			points += score

	return points


def init_db(conn, reset=False):
	"""
	ensure the database has the required tables for twbot

	args:
		reset - whether to delete all of the data beforehand
	"""

	c = conn.cursor()

	if reset:
		print("dropping tables..")

		c.execute("PRAGMA foregin_keys = OFF;")
		conn.commit()

		tables = get_tables(c)

		if "meta" in tables:
			c.execute("DROP TABLE meta;")

		if "players" in tables:
			c.execute("DROP TABLE players;")

		if "questions" in tables:
			c.execute("DROP TABLE questions;")

		if "possible_answers" in tables:
			c.execute("DROP TABLE possible_answers;")

		if "answers" in tables:
			c.execute("DROP TABLE answers;")

		if "dms" in tables:
			c.execute("DROP TABLE dms;")

		if "mentions" in tables:
			c.execute("DROP TABLE mentions;")

		c.execute("PRAGMA foregin_keys = ON;")
		conn.commit()

	c.execute(twbot_sql.CREATE_META)
	c.execute(twbot_sql.CREATE_PLAYERS)
	c.execute(twbot_sql.CREATE_QUESTIONS)
	c.execute(twbot_sql.CREATE_POSSIBLE_ANSWERS)
	c.execute(twbot_sql.CREATE_ANSWERS)
	c.execute(twbot_sql.CREATE_DMS)
	c.execute(twbot_sql.CREATE_MENTIONS)

	if not c.execute("SELECT * FROM meta").fetchone():
		c.execute(twbot_sql.INIT_META)

	conn.commit()

# FUNCTIONS END ################################################################
################################################################################

if __name__ != "__main__":
	print("this is not a library")
	sys.exit(1)

args = docopt(__doc__, help=False)

if args["help"]:
	print(__doc__)
	sys.exit(0)

twbot_port = args["--port"]

pp = pprint.PrettyPrinter(width=1)

try:
	conn = sqlite.connect("twbot.db")
except sqlite.Error as err:
	print(str(err))
	sys.exit(1)

# allow accessing columns by their name like a dict
conn.row_factory = sqlite.Row

c = conn.cursor()

# foreign key constraint support

c.execute("PRAGMA foreign_keys = ON;")
conn.commit()

init_db(conn)

app = b.Bottle()

api = get_twitter_api(c)

################################################################################
# CONSTANTS BEGIN ##############################################################

HELPER_TEXT_INTRO = "(Direct message me with the question number, a colon, and then your answer, e.g. {number}: "
HELPER_TEXT_MULTIPLE_CHOICE = HELPER_TEXT_INTRO + "A for answer A)"
HELPER_TEXT_OPEN_ENDED = HELPER_TEXT_INTRO + "Lorem ipsum ...)"

# computational power used for salts. higher values = harder to brute force,
# slower password hashing
SALT_ROUNDS = 14

MAX_TWEET_LEN = 140
UK_TZ = "Europe/London"

TPL_VARS_BASE = {
	"req": req,
	"c": c,
	"dmc": dmc,
	"api": api,
	"get_points": get_points,
}

# CONSTANTS END ################################################################
################################################################################

################################################################################
# ROUTES BEGIN #################################################################

"""
The "@" syntax that follows is known as a decorator, and is equivelant but more
concise way of passing a function to another function. This works because a
function is also an object in Python.

e.g.:

	@fn_x
	def fn_y():
		pass

is equivelant to:

	def fn_y():
		pass

	fn_y = fn_x(fn_y)

With the @(Bottle instance).get decorator, it registers the passed function to
be ran whenever the route passed to the get() function is matched by a GET
request to the server.
@(Bottle instance).post does the same, however it responds to POST requests
instead of GET requests.

The passed function to either of these decorators may either return the response
body (sent from the server to the client), or be passed to the
@(Bottle instance).view decorator, that gets passed a name of a template in the
"views" directory to return as the response body.
"""


@app.get("/static/<filepath:path>")
def static_file(filepath):
	# correctly handle static file requests
	return b.static_file(filepath, root="static")


@app.get("/")
@b.view("index.tpl")
def index():
	return get_tpl_vars(c)


@app.post("/register")
def register():
	meta = get_twbot_meta(c)
	if meta["first_run_step"] != 0:
		return

	username = req.POST.get("username")
	password = req.POST.get("password")

	# form validation

	if not username or not password:
		b.redirect("/?" + urlencode({
			"message": "Enter username and password",
		}))
	elif len(password) < 5:
		b.redirect("/?" + urlencode({
			"message": "Password must be at least five characters",
		}))

	# generate the password hash with the generated salt
	hashed_password = hash_password(password.encode())

	# commit admin details and proceed to next step
	c.execute("""UPDATE meta SET
		username = ?,
		password = ?,
		first_run_step = 1;
	""", (username, hashed_password))

	conn.commit()

	b.redirect("/")


@app.post("/register-tokens")
def register_tokens():
	meta = get_twbot_meta(c)
	if meta["first_run_step"] != 1:
		return

	api_key = req.POST.get("api-key")
	api_secret = req.POST.get("api-secret")
	access_key = req.POST.get("access-key")
	access_secret = req.POST.get("access-secret")

	print("api key:", api_key)
	print("api secret:", api_secret)
	print("access key:", access_key)
	print("access secret:", access_secret)

	auth = t.OAuthHandler(api_key, api_secret)
	auth.set_access_token(access_key, access_secret)

	api = t.API(auth)

	try:
		api.me()
	except t.TweepError:
		print("couldn't use twitter api")
		b.redirect("/?" + urlencode({"message": "One or more fields incorrect"}))

	c.execute("""
		UPDATE meta SET
			api_key = ?,
			api_secret = ?,
			access_key = ?,
			access_secret = ?,
			first_run_step = 2;
	""", (
		api_key,
		api_secret,
		access_key,
		access_secret,
	))

	conn.commit()

	b.redirect("/")


@app.post("/finish-setup")
def finish_setup():
	meta = get_twbot_meta(c)
	if meta["first_run_step"] != 2:
		return

	finish_time = dmc.utcnow().shift(UK_TZ)
	api.update_profile(description="Twitter Quiz Robot since " + finish_time.format_datetime())
	api.update_profile_image("static/img/twbot.png")

	# -1 means that the first run phase has been completed
	c.execute("UPDATE meta SET first_run_step = -1;")
	conn.commit()

	b.redirect("/")


@app.get("/players")
@app.get("/players/<handle>")
@b.view("players.tpl")
def players(handle=None):
	tpl_vars = get_tpl_vars(c)
	tpl_vars["handle"] = handle
	return tpl_vars


@app.get("/login")
@b.view("login.tpl")
def login():
	return get_tpl_vars(c)


@app.post("/login")
def login_post():
	username = req.POST.get("username")
	password = req.POST.get("password")
	meta = get_twbot_meta(c)

	valid = True
	if username == meta["username"]:
		if not password_matches(password.encode(), meta["password"]):
			valid = False
	else:
		valid = False

	if valid:
		# generate a UUID (Universally Unique IDentifier). Each one is unique
		# except in exceptional circumstances, and so it will be infeasible for
		# someone to forge one that authenticates them into the system
		session = str(uuid())

		resp.set_cookie("session", session, httponly=True)
		c.execute("UPDATE meta SET session = ?;", (session,))
		conn.commit()

		b.redirect("/questions")
	else:
		b.redirect("/login?" + urlencode({"message": "Incorrect login"}))


@app.get("/logout")
@b.view("logout.tpl")
def logout_get():
	return get_tpl_vars(c)


@app.post("/logout")
def logout_post():
	if not get_is_logged_in(c):
		b.redirect("/")
		return

	logout(c)

	b.redirect("/")


@app.get("/settings")
@b.view("settings.tpl")
def settings():
	return get_tpl_vars(c)


@app.post("/update-meta")
def update_meta():
	if not get_is_logged_in(c):
		print("tried to update meta with no login")
		b.redirect("/")

	meta_orig = get_twbot_meta(c)
	print("original meta:", meta_orig)

	username = req.POST.get("username") or meta_orig["username"]
	password = req.POST.get("password").encode() or meta_orig["password"]
	api_key = req.POST.get("api-key") or meta_orig["api_key"]
	api_secret = req.POST.get("api-secret") or meta_orig["api_secret"]
	access_key = req.POST.get("access-key") or meta_orig["access_key"]
	access_secret = req.POST.get("access-secret") or meta_orig["access_secret"]

	try:
		api = get_twitter_api(keys={
			"api_key": api_key,
			"api_secret": api_secret,
			"access_key": access_key,
			"access_secret": access_secret,
		})

		api.me()
	except t.TweepError:
		print("invalid keys")
		b.redirect("/settings?" + urlencode({"message": "Invalid keys"}))

	print("username:", username)
	print("password:", password)
	print("api key:", api_key)
	print("api secret:", api_secret)
	print("access key:", access_key)
	print("access secret:", access_secret)

	print("updating meta..")

	c.execute("UPDATE meta SET username = ?;", (username,))
	c.execute("UPDATE meta SET password = ?;", (password,))
	c.execute("UPDATE meta SET api_key = ?;", (api_key,))
	c.execute("UPDATE meta SET api_secret = ?;", (api_secret,))
	c.execute("UPDATE meta SET access_key = ?;", (access_key,))
	c.execute("UPDATE meta SET access_secret = ?;", (access_secret,))
	conn.commit()

	logout(c)
	b.redirect("/settings")


@app.get("/questions")
@b.view("questions.tpl")
def questions():
	return get_tpl_vars(c)


@app.post("/create-question")
def create_question():
	if not get_is_logged_in(c):
		print("requested to add a question with no login")
		b.redirect("/")

	question = req.POST.get("question").strip()
	is_multiple_choice = req.POST.get("is-multiple-choice") == "on"
	ask_time = req.POST.get("ask-time")

	ask_time = dmc.parse(ask_time, UK_TZ, dayfirst=False)
	ask_time = ask_time.shift("UTC")

	# question length check

	if len(question) + len("question x: ") > MAX_TWEET_LEN:
		print("question too long")
		b.redirect("/questions" + urlencode({"message": "Question too long"}))

	# question existence check

	if not question:
		print("no question!")
		b.redirect("/questions?" + urlencode({"message": "No question has been provided"}))

	print("\napparently..")
	print("  question is", question)
	print("  multiple choice is", is_multiple_choice)
	print("  ask time is", ask_time, ask_time.epoch)

	if is_multiple_choice:
		print("is multiple choice")

		answers = {
			"a": req.POST.get("answer-a"),
			"b": req.POST.get("answer-b"),
			"c": req.POST.get("answer-c"),
			"d": req.POST.get("answer-d"),
		}

		answers = {letter: answers[letter] for letter in answers if answers[letter].strip()}
		answers_list = list(answers.values())
		correct_answer = req.POST.get("correct-answer")

		print("  answers are", answers, "(" + str(answers_list) + ")")
		print("  correct answer is", correct_answer)

		# answers length check

		for answer in answers_list:
			if len(answer) + len("is it x: ?") > MAX_TWEET_LEN:
				print("possible")
				b.redirect("/questions" + urlencode({"message": "Possible answer too long"}))

		# answers quantity check

		if len(answers) < 2:
			b.redirect("/questions?" + urlencode({"message": "Not enough answers given - two or more needed"}))

		# answers duplicate check

		if len(answers) != len(set(answers_list)):
			b.redirect("/questions?" + urlencode({"message": "Duplicate answers given"}))

		# correct answer existence check

		if not correct_answer:
			b.redirect("/questions?" + urlencode({"message": "No correct answer specified"}))

		# check for matching correct answer

		if (
			(correct_answer == "a" and not answers.get("a")) or
			(correct_answer == "b" and not answers.get("b")) or
			(correct_answer == "c" and not answers.get("c")) or
			(correct_answer == "d" and not answers.get("d"))
		):
			print(
				"no matching correct answer! correct_answer is",
				correct_answer,
				"and answers are",
				answers
			)

			b.redirect("/questions?" + urlencode({"message": "The correct answer specified does not exist"}))

	# insert question

	c.execute("INSERT INTO questions (ask_time, question) VALUES (?, ?)", (ask_time.epoch, question))
	question_id = c.lastrowid

	print("inserted question with id", question_id)

	if is_multiple_choice:
		for letter in answers:
			# insert each possible answer
			c.execute("""
			INSERT INTO possible_answers (question_id, letter, answer) VALUES (
				?,
				?,
				?
			);
			""", (
				question_id,
				letter,
				answers[letter],
			))

			possible_answer_id = c.lastrowid
			print("inserted possible_answer with id", possible_answer_id)

			if letter == correct_answer:
				# store the correct answer id
				c.execute(
					"UPDATE questions SET possible_answer_id = ? WHERE id = ?",
					(possible_answer_id, question_id)
				)

				print("updated question with possible_answer_id", possible_answer_id)

	conn.commit()

	b.redirect("/questions")


@app.post("/delete-question/<id:int>")
def delete_question(id):
	if not get_is_logged_in(c):
		print("requested to delete a question with no login..")
		b.redirect("/")

	print("going to delete question with id", id)

	c.execute("UPDATE questions SET possible_answer_id = NULL WHERE id = ?;", (id,))
	c.execute("DELETE FROM answers WHERE question_id = ?;", (id,))
	c.execute("DELETE FROM possible_answers WHERE question_id = ?;", (id,))
	c.execute("DELETE FROM questions WHERE id = ?;", (id,))
	conn.commit()

	b.redirect("/questions")


@app.get("/answers")
@b.view("answers.tpl")
def answers():
	return get_tpl_vars(c)


@app.post("/mark-answers")
def mark_answers():
	if not get_is_logged_in(c):
		print("attempted to mark answers with no login..")
		b.redirect("/")

	post = req.POST

	for mark in post:
		answer_id = int(mark.split("-")[1])
		answer = c.execute("SELECT * FROM answers WHERE id = ?;", (answer_id,)).fetchone()
		question = c.execute("SELECT * FROM questions WHERE id = ?;", (answer["question_id"],)).fetchone()
		score = post[mark]

		print("got answer", answer)
		print("got question", question)

		if answer["score"] is not None:
			print("answer has already been marked")
			b.redirect("/answers")

		print("admin gave score", score, "with answer id", answer_id)

		c.execute("UPDATE answers SET score = ? WHERE id = ?;", (score, answer_id))
		conn.commit()

	b.redirect("/answers")


@app.post("/rm-tweets-dms")
def rm_tweets_dms():
	if not get_is_logged_in(c):
		print("tried to rm tweets dms with no login..")
		b.redirect("/")

	print("ACHTUNG, deleting tweets!!")

	tweets = api.user_timeline(user_id=api.me().id, count=200)
	for tweet in tweets:
		print("destroying tweet:", tweet.text)
		api.destroy_status(tweet.id)
		print("destroyed.")

	print("ACHTUNG, deleting dms!!")

	dms = api.direct_messages(count=200)
	for dm in dms:
		print("destroying dm:", dm.text)
		api.destroy_direct_message(id=dm.id)
		c.execute("DELETE FROM dms WHERE id = ?;", (dm.id,))
		print("destroyed.")

	b.redirect("/settings")


@app.post("/reset")
def reset():
	if not get_is_logged_in(c):
		print("tried to reset with no login..")
		b.redirect("/")

	print("ACHTUNG, resetting database!!")
	init_db(conn, reset=True)

	b.redirect("/settings")


# ROUTES END ###################################################################
################################################################################

"""
Rate limits

One question can total up to 6 tweets:
- 1 * question
- 1 * helper text
- 4 (max) * possible answers

2400 tweets/day = 100/hour = 1.66/minute

Therefore we can manage to broadcast one question every 4 minutes, but 10 will be
used for a reasonable margin of safety (considering other API calls as well)
"""


def do_work():
	# calls to the Twitter API will be wrapped in "##"s for visibility

	conn = sqlite.connect("twbot.db")
	conn.row_factory = sqlite.Row
	c = conn.cursor()

	meta = get_twbot_meta(c)

	print("\ndoing work..")

	if meta["first_run_step"] == -1:
		api = get_twitter_api(c)

		print("\ndoing work..")

		try:
			questions = c.execute(
				"SELECT * FROM questions WHERE is_asked = 0 AND ask_time <= ?",
				(int(dmc.utcnow().epoch),),
			).fetchall()

			# QUESTIONS

			for question in questions:
				print("\ngot question:", question["question"], "to be asked at", question["ask_time"])

				## statuses/update ##
				tweet = api.update_status(status="Question " + str(question["id"]) + ": " + question["question"])

				print("tweeted question with status id", tweet.id)
				c.execute("UPDATE questions SET is_asked = 1 WHERE id = ?;", (question["id"],))
				conn.commit()

				if question["possible_answer_id"]:
					# multiple choice

					answers = c.execute(
						"SELECT * FROM possible_answers WHERE question_id = ?;",
						(question["id"],)
					)

					# sort the answers in alphabetical order
					answers = sorted(answers, key=lambda answer: answer["letter"])

					for answer in answers:
						print("got answer", answer["letter"], answer["answer"])

						# reply to question tweet with possible answer

						## statuses/update ##
						answer_tweet = api.update_status(
							status="@" + api.me().screen_name + " Is it " + answer["letter"].upper() + ": " + answer["answer"] + "?",
							in_reply_to_status_id=tweet.id,
						)

						print("tweeted answer with id", answer_tweet.id)

					helper_text = HELPER_TEXT_MULTIPLE_CHOICE.format(number=question["id"])

					## statuses/update ##
					api.update_status(
						status="@" + api.me().screen_name + " " + helper_text,
						in_reply_to_status_id=tweet.id,
					)

					print("tweeted helper text")
				else:
					# open-ended question

					helper_text = HELPER_TEXT_OPEN_ENDED.format(number=question["id"])
					api.update_status(
						status="@" + api.me().screen_name + " " + helper_text,
						in_reply_to_status_id=tweet.id,
					)
			# MENTIONS

			## statuses/mentions_timeline ##
			mentions = api.mentions_timeline(count=200)

			for mention in mentions:
				print("\ngot mention from", mention.user.screen_name, "body:", mention.text)

				results = c.execute("SELECT * FROM mentions WHERE id = ?;", (mention.id,)).fetchall()

				if results:
					print("already handled mention..")
					continue

				c.execute("INSERT INTO mentions (id) VALUES (?);", (mention.id,))
				print("inserted mention")
				conn.commit()

				if mention.user.screen_name == api.me().screen_name:
					print("mention from twbot user, ignoring..")
					continue

				# this tweet has not been handled

				print("new mention!")

				players = c.execute("SELECT * FROM players WHERE id = ?;", (mention.user.id,)).fetchall()

				if not players:
					# follow user, allowing them to direct message

					print("following user..")

					## friendships/create ##
					api.create_friendship(user_id=mention.user.id)

					# reply to the tweet

					print("replying to mention..", mention.id)

					## statuses/update ##
					api.update_status(
						status="@" + mention.user.screen_name +
						" Welcome! Follow me to be notified of questions!",
						in_reply_to_status_id=mention.id,
					)

					c.execute("INSERT INTO players (id) VALUES (?);", (mention.user.id,))

					print("inserted created new player")
					conn.commit()

			# DIRECT MESSAGES

			## direct_messages ##
			dms = api.direct_messages(count=200)

			for dm in dms:
				print("\ndirect messaged by", dm.sender.screen_name, "body:", dm.text)

				results = c.execute("SELECT * FROM dms WHERE id = ?;", (dm.id,)).fetchall()

				if results:
					print("already handled dm..")
					continue

				c.execute("INSERT INTO dms (id) VALUES (?);", (dm.id,))
				conn.commit()

				# this dm has not been handled

				print("new dm!")

				answer_parts = dm.text.split(":")
				if len(answer_parts) < 2:
					# this player is not adhering to the answer format

					print("badly formatted dm..")

					## direct_messages/new ##
					api.send_direct_message(
						user_id=dm.sender.id,
						text="I don't understand... Please refer to the instructions given with the question",
					)

					continue

				if len(answer_parts) > 2:
					# have only two list elements, with the second being the full answer
					# e.g. ["1", "Lorem", " Ipsum", " Dolor"] -> ["1", "Lorem Ipsum Dolor"]
					answer_parts[1] = "".join(answer_parts[1:])

				# remove leading and trailing whitespace with .strip()

				question_id = int(answer_parts[0].strip())
				answer = answer_parts[1].strip()

				print("got answer to question id", question_id, "with answer", answer)

				questions = c.execute("SELECT * FROM questions WHERE id = ?;", (question_id,)).fetchall()

				if not questions:
					print("no question with id", question_id)
					api.send_direct_message(user_id=dm.sender.id, text="No such question!")
					continue

				question = questions[0]
				print("found question:", question)

				player = c.execute("SELECT * FROM players WHERE id = ?;", (dm.sender.id,)).fetchone()

				answers = c.execute(
					"SELECT * FROM answers WHERE player_id = ? AND question_id = ?;",
					(dm.sender.id, question["id"]),
				).fetchall()

				if answers:
					print("player already answered this..")
					api.send_direct_message(user_id=dm.sender.id, text="You already answered that question!")
					print("sent tweet")
					continue

				dm_time = dmc.Delorean(dm.created_at, "UTC")
				print("dm was posted at", dm_time)

				if question["possible_answer_id"]:
					# multiple choice question

					print("multiple choice")

					answer = answer.lower()

					# get a list of possible answers to the question
					possible_answers = c.execute(
						"SELECT * FROM possible_answers WHERE question_id = ?;",
						(question_id,),
					).fetchall()

					possible_answer_match = None
					for possible_answer in possible_answers:
						# loop through each possible answer to see if the player's answer exists

						if possible_answer["letter"] == answer:
							possible_answer_match = possible_answer["id"]
							break

					if not possible_answer_match:
						print("no answer with letter", answer)
						api.send_direct_message(user_id=dm.sender.id, text="No such answer with that letter!")
						continue

					correct_answer = c.execute(
						"SELECT * FROM possible_answers WHERE id = ?;",
						(question["possible_answer_id"],),
					).fetchone()

					is_correct = True if answer == correct_answer["letter"] else False
					score = 10 if is_correct else 0

					if is_correct:
						message = "Correct! +" + str(score) + " points! "
					else:
						message = \
							"Incorrect! The correct answer was " + \
							correct_answer["letter"].upper()

					api.send_direct_message(user_id=dm.sender.id, text=message)

					c.execute("""INSERT INTO answers (
						player_id,
						question_id,
						possible_answer_id,
						answer,
						time,
						score,
						dm_id,
						messaged_score
					) VALUES (
						?,  -- player_id
						?,  -- question_id
						?,  -- possible_answer_id
						?,  -- answer
						?,  -- time
						?,  -- score
						?,  -- dm_id
						?   -- messaged_score
					);""", (
						player["id"],
						question["id"],
						possible_answer_match,
						answer,
						dm_time.epoch,
						score,
						dm.id,
						1
					))

					conn.commit()
				else:
					# non-multiple choice question

					c.execute("""INSERT INTO answers (
						player_id,
						question_id,
						answer,
						time,
						dm_id,
						messaged_score
					) VALUES (
						?,  -- player_id
						?,  -- question_id
						?,  -- answer
						?,  -- time
						?,  -- dm_id
						?   -- messaged_score
					);""", (
						player["id"],
						question["id"],
						answer,
						dm_time.epoch,
						dm.id,
						False
					))

					conn.commit()

			answers = c.execute("SELECT * FROM answers;").fetchall()
			for answer in answers:
				answer = dict(answer)

				if (answer.get("score") is not None) and (not answer["messaged_score"]):
					# in this case, the non-multiple choice answer has been scored by the administrator, and the player needs to be notified of their score

					print("notifying user of score..")

					api.send_direct_message(user_id=dm.sender.id, text="You got +" + str(answer["score"]) + " points for your answer!")
					c.execute("UPDATE answers SET messaged_score = 1;")
					conn.commit()
		except t.TweepError as err:
			# an exception will crash this timer and stop it from re-running, so it
			# would be best to log it and carry on for the user's sake
			print("ACHTUNG, got error", err)
	else:
		print("first run not completed..")

	c.close()

	# run every 10 minutes
	timer = threading.Timer(60 * 10, do_work)

	timer.daemon = True
	timer.start()
	print("\nscheduled next timer..")


@atexit.register
def cleanup():
	print("goodbye")

	c.close()
	conn.commit()
	conn.close()

timer = threading.Timer(1, do_work)
timer.daemon = True
timer.start()

# start the twbot server
app.run(host="0.0.0.0", port=twbot_port)

c.close()
