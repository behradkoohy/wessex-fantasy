from flask import Flask, render_template, request, jsonify, flash
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
curs.execute("""CREATE TABLE IF NOT EXISTS teams 
							(team_id serial PRIMARY KEY, 
							name varchar);
						""")
conn.commit()
curs.execute("""CREATE TABLE IF NOT EXISTS player_details 
							(player_id serial PRIMARY KEY, 
							name varchar, 
							nickname varchar,
							shirt_number int, 
							team_id serial REFERENCES teams (team_id));
						""")
conn.commit()
# Adding teams to the teams db
for x, t in enumerate(wessex_teams):
	curs = conn.cursor()
	curs.execute("INSERT INTO teams (name) SELECT (%s) WHERE NOT EXISTS (SELECT name FROM teams WHERE name = %s);", (t, t))
	conn.commit()


# start the website and set up the secret key
# key is already set up on the heroku
app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ['SECRET_KEY']



@app.route('/')
def frontpage():
	return render_template('front.html')


@app.route('/addplayer', methods=['GET', 'POST'])
def add_player_page():
	pass_through = {}

	curs.execute('SELECT name FROM teams;')
	teams_retrieved = [t[0] for t in curs.fetchall()]
	pass_through['teams']=teams_retrieved

	if request.method == 'GET':
		

		# pass_through['teams']

		return render_template('add_player.html', data=pass_through)
	elif request.method == 'POST':
		# [('playername', 'Mikey Gimson'), ('playername', '6'), ('playerteam', '1st XI'), ('playerpos', 'Forward')])
		form = request.form

		name = form['playername']
		shirt_number = form['playernumber'] 
		nickname = form['playernickname']
		team = form['playerteam'] 
		position = form['playerpos']
		message = name + ' has successfully been added to the database.'

		if name == 'reset':
			print('resetting db')
			curs.execute('TRUNCATE TABLE player_details;')
			conn.commit()
			# reset the DB when this is passed
		else:
			curs.execute("SELECT team_id FROM teams WHERE name = %s ;", (team, ))
			team_id = curs.fetchone()[0]
			try:
				curs.execute("INSERT INTO player_details (name, nickname, shirt_number, team_id) VALUES (%s, %s, %s, %s);",(name, nickname, shirt_number, team_id))
				conn.commit()
			except Exception as e:
				flash('Error while adding player','danger')
			else:
				flash(message, 'success')
		return render_template('add_player.html', data=pass_through)






