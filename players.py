from flask import Blueprint, request,render_template, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from urllib.parse import urlparse
import os
import psycopg2

players_blueprint = Blueprint("players", __name__)
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


@players_blueprint.route('/addplayer', methods=['GET', 'POST'])
@login_required
def add_player_page():
	pass_through = {}

	curs.execute('SELECT name FROM teams;')
	teams_retrieved = [t[0] for t in curs.fetchall()]
	pass_through['teams']=teams_retrieved

	if request.method == 'GET':
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

