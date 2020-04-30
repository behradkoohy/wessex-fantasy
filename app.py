from flask import Flask, render_template, request, jsonify, flash, url_for, session, logging, redirect
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from views import frontpage
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash, check_password_hash
import os
import psycopg2
from models import User




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
							name varchar NOT NULL, 
							nickname varchar,
							shirt_number int, 
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
# Adding teams to the teams db
for x, t in enumerate(wessex_teams):
	curs = conn.cursor()
	curs.execute("INSERT INTO teams (name) SELECT (%s) WHERE NOT EXISTS (SELECT name FROM teams WHERE name = %s);", (t, t))
	conn.commit()


# start the website and set up the secret key
# key is already set up on the heroku
app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ['SECRET_KEY']

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



@app.route('/addplayer', methods=['GET', 'POST'])
@login_required
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

		#REMOVE THIS WHEN DEBUG OVER
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

@app.route('/register', methods=['GET', 'POST'])
def register():
	curs = conn.cursor()
	if request.method == "POST":
		name=request.form.get("name")
		email=request.form.get("email")
		password=request.form.get("password")
		if len(password) <= 6:
			flash('Password needs to be greater than 6 characters please.', 'danger')
			return render_template('register.html')
		#REMOVE THIS WHEN DEBUG OVER
		if name == 'reset':
			reset_table()
			return render_template('register.html')

		confirm=request.form.get("confirm")
		if password != confirm:
			flash('Please double check your passwords match', 'danger')
			return render_template('register.html')
		hashed_password = generate_password_hash(password)
		curs.execute("SELECT email FROM users WHERE email = %s;", (email, ))
		matching_emails = curs.fetchone()
		if matching_emails is not None:
			flash('This email is already registered, please talk to behrad if you can\'t log on.', 'danger')
		else:
			curs.execute("INSERT INTO users (email, password_hash, name) VALUES (%s, %s, %s);", (email, hashed_password, name))
			conn.commit()
			flash('Successfully registered account.', 'success')
	return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		curs = conn.cursor()
		curs.execute("SELECT email, password_hash, name, user_id FROM users WHERE email = %s;", (email, ))
		account = curs.fetchone()
		if account is not None:
			if check_password_hash(account[1], password):
				user = user_loader_email(account[0])
				print('logging in:',user)
				login_user(user)
				print(user)
				return redirect(request.args.get('next') or url_for('frontpage'))
			else:
				flash('Incorrect username or password', 'danger')
		else:
			flash('Incorrect username or password', 'danger')
	return render_template('login.html')




@app.route('/viewsquad/<pagenum>')
def displayitems(pagenum):
	curs = conn.cursor()
	offset = int(pagenum) * 11
	limit = 11
	print(offset, limit)
	curs.execute("""SELECT player_details.player_id, 
							player_details.name, 
							player_details.nickname, 
							player_details.shirt_number, 
							teams.name 
							FROM 
							player_details INNER JOIN teams 
							ON 
							teams.team_id = player_details.team_id 
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