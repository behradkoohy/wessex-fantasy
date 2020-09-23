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
	# passthrough['players_gk'] = []
	# passthrough['players_df'] = []
	# passthrough['players_md'] = []
	# passthrough['players_fw'] = []
	for s in ['players_gk', 'players_df', 'players_md', 'players_fw']:
		for x in range(1,6):
			passthrough[s + "_" + str(x)] = []
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
			if p[2] == 1:
				passthrough['players_fw_1'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 2:
				passthrough['players_fw_2'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 3:
				passthrough['players_fw_3'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 4:
				passthrough['players_fw_4'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 5:
				passthrough['players_fw_5'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})

		if p[3] == 2:
			if p[2] == 1:
				passthrough['players_md_1'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 2:
				passthrough['players_md_2'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 3:
				passthrough['players_md_3'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 4:
				passthrough['players_md_4'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 5:
				passthrough['players_md_5'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})

		if p[3] == 3:
			if p[2] == 1:
				passthrough['players_df_1'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 2:
				passthrough['players_df_2'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 3:
				passthrough['players_df_3'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 4:
				passthrough['players_df_4'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 5:
				passthrough['players_df_5'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})

		if p[3] == 4:
			if p[2] == 1:
				passthrough['players_gk_1'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 2:
				passthrough['players_gk_2'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 3:
				passthrough['players_gk_3'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 4:
				passthrough['players_gk_4'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})
			elif p[2] == 5:
				passthrough['players_gk_5'].append({
					player_details[0]: p[0], 
					player_details[1]: p[1], 
					player_details[2]: p[2], 
					player_details[3]: p[3],
					player_details[4]: p[4].replace('£','')
				})

	#return jsonify(passthrough)
	if request.method == "POST":
		# Checks we need to do
		# 1. Cost is below the specified amount
		# 2. No player is bought more than once
		# 3. You have less than 3 players from each team
		gk = request.form['gk']

		def1 = request.form['def1']
		def2 = request.form['def2']
		def3 = request.form['def3']
		def4 = request.form['def4']

		mid1 = request.form['mid1']
		mid2 = request.form['mid2']
		mid3 = request.form['mid3']

		fwd1 = request.form['fwd1']
		fwd2 = request.form['fwd2']
		fwd3 = request.form['fwd3']

		players_selected = [gk, def1, def2, def3, def4, mid1, mid2, mid3, fwd1, fwd2, fwd3]


		# Check 1
		p_sum = 0
		for player in players_selected:
			curs.execute("""
			SELECT  
				value
			FROM 
				player_details_full
			WHERE
			player_id = %s;
			""", (player, ))
			p_sum += float(curs.fetchone()[0].replace('£',''))

		if p_sum > 20000000:
			pass
			# Flash error here

		# Check 2
		if len(list(set(players_selected))) < len(players_selected):
			pass
			# flash error here


		return jsonify(request.form)
	return render_template('pickteam.html', data=passthrough)