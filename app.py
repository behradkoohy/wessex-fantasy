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
from teams import teams_blueprint
# from fixtures import fixtures_blueprint


wessex_teams = ['1st XI', '2nd XI', '3rd XI', '4th XI', '5th XI (Development Squad)']
positions = ['Forward', 'Midfield', 'Defence', 'Goalkeeper']
test_teams = ['team1', 'team2', 'team3']

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
							value money NOT NULL,
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
curs.execute("""CREATE TABLE IF NOT EXISTS opposition_teams
							(team_id serial PRIMARY KEY,
							name varchar);
						""")
conn.commit()
curs.execute("""CREATE TABLE IF NOT EXISTS fixtures_team
							(fixture_id serial PRIMARY KEY,
							team_id int REFERENCES teams (team_id),
							opp_id int REFERENCES opposition_teams (team_id),
							players varchar,
							wessex_goals int,
							opposition_goals int,
							fixture_date date);
						""")
conn.commit()
curs.execute("""CREATE TABLE IF NOT EXISTS fixtures_individual
							(player_id int REFERENCES player_details (player_id),
							fixture_id int REFERENCES fixtures_team (fixture_id),
							goals int,
							d_flicks int,
							assists int,
							greens int,
							yellows int,
							reds int,
							p_flicks_scored int,
							p_flicks_missed int,
							p_flicks_awarded int,
							wasMidOrDef boolean,
							gkgoals_conc int,
							PRIMARY KEY(player_id, fixture_id));
						""")
conn.commit()
curs.execute("""CREATE TABLE IF NOT EXISTS user_team
							(user_id int REFERENCES users (user_id),
							team_name varchar,
							gk int REFERENCES player_details (player_id) NOT NULL,
							def1 int REFERENCES player_details (player_id) NOT NULL,
							def2 int REFERENCES player_details (player_id) NOT NULL,
							def3 int REFERENCES player_details (player_id) NOT NULL,
							def4 int REFERENCES player_details (player_id) NOT NULL,
							mid1 int REFERENCES player_details (player_id) NOT NULL,
							mid2 int REFERENCES player_details (player_id) NOT NULL,
							mid3 int REFERENCES player_details (player_id) NOT NULL,
							fwd1 int REFERENCES player_details (player_id) NOT NULL,
							fwd2 int REFERENCES player_details (player_id) NOT NULL,
							fwd3 int REFERENCES player_details (player_id) NOT NULL,
							score int,
							weekly_score int,
							leftover_value money);
	""")
conn.commit()
curs.execute("""CREATE OR REPLACE VIEW player_details_full AS
				SELECT
					player_details.player_id,
					player_details.name,
					player_details.nickname,
					player_details.shirt_number,
					player_details.value,
					teams.team_id,
					teams.name AS "team_name",
					positions.position_id,
					positions.position_name AS "position"
				FROM player_details
					INNER JOIN 
					teams
					ON
					teams.team_id = player_details.team_id
					INNER JOIN
					positions
					ON
					positions.position_id = player_details.position_id
				;
				 """)
conn.commit()
# mikey's inner join attempt
# needs to include players
# Note to self: the attributes after 'SELECT' are the columns that will be in the view (virtual table)? So it doesn't need all the attributes, just the ones you want in the view
curs.execute("""CREATE OR REPLACE VIEW fixtures_details_full AS
				SELECT
				fixtures_individual.goals,
				fixtures_individual.d_flicks,
				fixtures_individual.assists,
				fixtures_individual.greens,
				fixtures_individual.yellows,
				fixtures_individual.reds,
				fixtures_individual.p_flicks_scored,
				fixtures_individual.p_flicks_missed,
				fixtures_individual.p_flicks_awarded,
				fixtures_individual.wasMidOrDef,
				fixtures_individual.gkgoals_conc,

				fixtures_team.players,
				fixtures_team.wessex_goals,
				fixtures_team.opposition_goals,
				fixtures_team.fixture_date,

				player_details.player_id,
				player_details.name,
				player_details.nickname,
				player_details.shirt_number,
				player_details.value

			FROM fixtures_individual
					INNER JOIN 
					fixtures_team
					ON
					fixtures_team.fixture_id = fixtures_individual.fixture_id
					INNER JOIN
					player_details
					ON
					player_details.team_id = fixtures_team.team_id

				;
				 """)
conn.commit()
# need another one with fixture teams on teams and opps fixtures_teams inner join teams inner join opps
curs.execute("""CREATE OR REPLACE VIEW fixtures_teams_opps AS
				SELECT

				fixtures_team.players,
				fixtures_team.wessex_goals,
				fixtures_team.opposition_goals,
				fixtures_team.fixture_date,
				-- fixtures_team.opp_id,

				teams.team_id,
				teams.name AS "team_name",

				opposition_teams.team_id AS "opposition id",
				opposition_teams.name AS "opposition_name"

			FROM fixtures_team
					INNER JOIN 
					teams
					ON
					teams.team_id = fixtures_team.team_id					
					INNER JOIN
					opposition_teams
					ON
					opposition_teams.team_id = fixtures_team.opp_id
				;
				 """)
conn.commit()


curs.execute("""CREATE OR REPLACE VIEW league_view AS
				SELECT
					users.user_id,
					users.name,

					user_team.team_name,
					user_team.gk,
					user_team.def1,
					user_team.def2,
					user_team.def3,
					user_team.def4,
					user_team.mid1,
					user_team.mid2,
					user_team.mid3,
					user_team.fwd1,
					user_team.fwd2,
					user_team.fwd3,
					user_team.score
				FROM users
					INNER JOIN
					user_team
					ON
					users.user_id = user_team.user_id
				;
				""")

# Adding teams to the teams db
for x, t in enumerate(wessex_teams):
	curs = conn.cursor()
	curs.execute("INSERT INTO teams (name) SELECT (%s) WHERE NOT EXISTS (SELECT name FROM teams WHERE name = %s);", (t, t))
	conn.commit()

for x, t in enumerate(positions):
	curs = conn.cursor()
	curs.execute("INSERT INTO positions (position_name) SELECT (%s) WHERE NOT EXISTS (SELECT position_name FROM positions WHERE position_name = %s);", (t, t))
	conn.commit()

for x, t in enumerate(test_teams):
	curs = conn.cursor()
	curs.execute("INSERT INTO opposition_teams (name) SELECT (%s) WHERE NOT EXISTS (SELECT name FROM opposition_teams WHERE name = %s);", (t, t))
	conn.commit()
	

# start the website and set up the secret key
# key is already set up on the heroku
app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ['SECRET_KEY']

app.register_blueprint(players_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(fixtures_blueprint)
app.register_blueprint(teams_blueprint)

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