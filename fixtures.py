from flask import Blueprint, request,render_template, flash, jsonify
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from urllib.parse import urlparse
import os
import psycopg2


fixtures_blueprint = Blueprint("fixtures", __name__)
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

@fixtures_blueprint.route('/report_fixture', methods=['POST', 'GET'])
@login_required
def report_fixture():
	if request.method == "POST":
		form = request.form
		curs.execute("""INSERT INTO fixtures_team 
			(team_id, opp_id, players, wessex_goals, opposition_goals, fixture_date) 
			VALUES 
			(%s, %s, %s, %s, %s, %s);
			""", 
			(form['team'], form['opp'], form['players_selected'], form['wessexGoals'], form['oppGoals'], form['fixture_date']))
		return jsonify(request.form)
	else:
		passthrough = {}
		# Player details
		curs.execute("SELECT player_id, name, nickname FROM player_details;")
		player_details_fetched = curs.fetchall()
		player_details_transformed = []
		for det in player_details_fetched:
			player_details_transformed.append({"id": det[0], "name": det[1], "data_tokens": (det[1] + " " + det[2])})

		# Team details
		curs.execute("SELECT team_id, name FROM teams;")
		team_details_fetched = curs.fetchall()
		team_details_transformed = []
		for det in team_details_fetched:
			team_details_transformed.append({"id": det[0], "name": det[1]})

		curs.execute("SELECT team_id, name FROM opposition_teams;")
		opp_details_fetched = curs.fetchall()
		opp_details_transformed = []
		for det in opp_details_fetched:
			opp_details_transformed.append({"id": det[0], "name": det[1]})


		passthrough['players'] = player_details_transformed
		passthrough['teams'] = team_details_transformed
		passthrough['opps'] = opp_details_transformed

		#return jsonify(passthrough)
		return render_template('fixture_report.html', data=passthrough)

@fixtures_blueprint.route('/report_fixture_2/<id>')
def report_fixture_2(id):
	passthrough = {}
	curs.execute('SELECT players, wessex_goals, opposition_goals FROM fixtures_team WHERE fixture_id = %s', (id, ))
	fixture_info = curs.fetchone()
	fixture_info = {'players': fixture_info[0], 'wessex_goals': fixture_info[1], 'opposition_goals': fixture_info[2]}
	
	passthrough['wessex_goals'] = fixture_info['wessex_goals']

	player_list = fixture_info['players'].split(",")
	player_info = []
	for player in player_list:
		curs.execute("SELECT player_id, name, nickname FROM player_details WHERE player_id = %s;", (player, ))
		p = curs.fetchone()
		player_info.append({'id': p[0], 'name': p[1], 'data_tokens': p[1] + " " + p[2]})


	return jsonify(player_info)





