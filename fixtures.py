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
	passthrough['players'] = player_details_transformed
	passthrough['teams'] = team_details_transformed

	#return jsonify(passthrough)
	return render_template('fixture_report.html', data=passthrough)