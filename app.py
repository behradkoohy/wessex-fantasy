from flask import Flask, render_template, request
from views import frontpage
import os
import psycopg2
from urllib.parse import urlparse


wessex_teams = ['1st XI', '2nd XI', '3rd XI', '4th XI', '5th XI (Development Squad)']

# Connecting to the database
result = urlparse(os.environ['DATABASE_URL'])
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname

conn = psycopg2.connect(
    database = database,
    user = username,
    password = password,
    host = hostname
)

# Creating the tables as needed
curs = conn.cursor()
curs.execute("CREATE TABLE IF NOT EXISTS teams (team_id serial PRIMARY KEY, name varchar);")
conn.commit()

# Adding teams to the teams db
for x, t in enumerate(wessex_teams):
	curs = conn.cursor()
	curs.execute("INSERT INTO teams (name) SELECT (%s) WHERE NOT EXISTS (SELECT name FROM teams WHERE name = %s);", (t, t))
	conn.commit()



app = Flask(__name__, template_folder='templates')


@app.route('/')
def frontpage():
	return render_template('front.html')


@app.route('/addplayer', methods=['GET', 'POST'])
def add_player_page():
	
	if request.method == 'GET':
		pass_through = {}

		curs.execute('SELECT name FROM teams;')
		teams_retrieved = [t[0] for t in curs.fetchall()]
		pass_through['teams']=teams_retrieved

		# pass_through['teams']
		return render_template('add_player.html', data=pass_through)
	elif request.method == 'POST':
		pass







