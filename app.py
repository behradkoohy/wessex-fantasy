from flask import Flask, render_template, request, jsonify, flash, url_for, session, logging, redirect
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash, check_password_hash
import os
import psycopg2
from models import User
from players import players_blueprint
from user import user_blueprint
from fixtures import fixtures_blueprint


wessex_teams = ['1st XI', '2nd XI', '3rd XI', '4th XI', '5th XI (Development Squad)']
positions = ['Forward', 'Midfield', 'Defence', 'Goalkeeper']

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
conn.autocommit = True
curs = conn.cursor()



# Creating the tables as needed
curs = conn.cursor()
curs.execute("""CREATE TABLE IF NOT EXISTS teams 
							(team_id serial PRIMARY KEY, 
							name varchar);
						""")
conn.commit()
curs.execute("""CREATE TABLE IF NOT EXISTS positions
							(position_id serial PRIMARY KEY,
							position_name varchar);
						""")
conn.commit()
curs.execute("""CREATE TABLE IF NOT EXISTS player_details 
							(player_id serial PRIMARY KEY, 
							name varchar NOT NULL, 
							nickname varchar,
							shirt_number int,
							position_id serial REFERENCES positions (position_id),
							team_id serial REFERENCES teams (team_id));
						""")
conn.commit()
curs.execute("""CREATE TABLE IF NOT EXISTS users
							(user_id serial PRIMARY KEY,
							email TEXT NOT NULL UNIQUE,
							password_hash TEXT NOT NULL,
							name TEXT NOT NULL);
							""")
conn.commit()

# curs.execute("""CREATE TABLE IF NOT EXISTS user_details

# 	""")
# Adding teams to the teams db
for x, t in enumerate(wessex_teams):
	curs = conn.cursor()
	curs.execute("INSERT INTO teams (name) SELECT (%s) WHERE NOT EXISTS (SELECT name FROM teams WHERE name = %s);", (t, t))
	conn.commit()

for x, t in enumerate(positions):
	curs = conn.cursor()
	curs.execute("INSERT INTO positions (position_name) SELECT (%s) WHERE NOT EXISTS (SELECT position_name FROM positions WHERE position_name = %s);", (t, t))
	conn.commit()

# start the website and set up the secret key
# key is already set up on the heroku
app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ['SECRET_KEY']
app.register_blueprint(players_blueprint)
app.register_blueprint(user_blueprint)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def user_loader(id):
	print(session)
	curs = conn.cursor()
	curs.execute("SELECT user_id, name, email, password_hash FROM users WHERE user_id = %s;", (id, ))
	matching_emails = curs.fetchone()
	if matching_emails is not None:
		u = matching_emails
		user = User(u[0], u[1], u[2], u[3])
		return user

def user_loader_email(email):
	curs = conn.cursor()
	curs.execute("SELECT user_id, name, email, password_hash FROM users WHERE email = %s;", (email, ))
	matching_emails = curs.fetchone()
	if matching_emails is not None:
		u = matching_emails
		user = User(u[0], u[1], u[2], u[3])
		return user


@app.route('/')
def frontpage():
	return render_template('front.html')



def reset_table():
	curs = conn.cursor()
	curs.execute('DROP TABLE users;')
	conn.commit()
	curs.execute("""CREATE TABLE IF NOT EXISTS users
							(user_id serial PRIMARY KEY,
							email TEXT NOT NULL UNIQUE,
							password_hash TEXT NOT NULL,
							name TEXT NOT NULL);
							""")
	conn.commit()


@app.route('/viewsquad/<pagenum>')
def displaysquad(pagenum):
	curs = conn.cursor()
	offset = int(pagenum) * 11
	limit = 11
	print(offset, limit)
	curs.execute("""SELECT player_details.player_id, 
							player_details.name, 
							player_details.nickname, 
							player_details.shirt_number, 
							positions.position_name,
							teams.name 
							FROM 
							player_details 
							INNER JOIN 
							teams 
							ON 
							teams.team_id = player_details.team_id 
							INNER JOIN
							positions
							ON
							player_details.position_id = positions.position_id
							ORDER BY 
							shirt_number 
							LIMIT %s OFFSET %s"""
							, (limit, offset))
	result = curs.fetchall()
	return render_template('list_players.html', players = result, n=int(pagenum))



@app.route('/logout')
def logout():
    logout_user()
    flash('Successfully logged out.', 'success')
    return redirect(url_for('frontpage'))