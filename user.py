from flask import Blueprint, request,render_template, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash, check_password_hash
import os
import psycopg2


user_blueprint = Blueprint("users", __name__)

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


@user_blueprint.route('/register', methods=['GET', 'POST'])
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


@user_blueprint.route('/login', methods=['GET', 'POST'])
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


