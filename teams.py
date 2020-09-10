from flask import Blueprint, request,render_template, flash, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from urllib.parse import urlparse
import os
import psycopg2


teams_blueprint = Blueprint("teams", __name__)
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

@teams_blueprint.route('/pickteam', methods=['POST', 'GET'])
def pick_team():
	passthrough = {}
	passthrough['players_gk'] = []
	passthrough['players_df'] = []
	passthrough['players_md'] = []
	passthrough['players_fw'] = []
	player_details = ['player_id', 'name', 'team_id', 'team_name', 'value']
	curs.execute("""
		SELECT 
			player_id, 
			name, 
			team_id, 
			position_id, 
			value
		FROM 
			player_details_full;
		""")
	players = curs.fetchall()
	for p in players:
		if p[3] == 1:
			passthrough['players_fw'].append({
				player_details[0]: p[0], 
				player_details[1]: p[1], 
				player_details[2]: p[2], 
				player_details[3]: p[3],
				player_details[4]: p[4].replace('£','')
			})
		if p[3] == 2:
			passthrough['players_md'].append({
				player_details[0]: p[0], 
				player_details[1]: p[1], 
				player_details[2]: p[2], 
				player_details[3]: p[3],
				player_details[4]: p[4].replace('£','')
			})
		if p[3] == 3:
			passthrough['players_df'].append({
				player_details[0]: p[0], 
				player_details[1]: p[1], 
				player_details[2]: p[2], 
				player_details[3]: p[3],
				player_details[4]: p[4].replace('£','')
			})
		if p[3] == 4:
			passthrough['players_gk'].append({
				player_details[0]: p[0], 
				player_details[1]: p[1], 
				player_details[2]: p[2], 
				player_details[3]: p[3],
				player_details[4]: p[4].replace('£','')
			})
		print(p[3])
	#return jsonify(passthrough)
	if request.method == "POST":
		return jsonify(request.form)
	return render_template('pickteam.html', data=passthrough)