from flask import Flask, render_template
from views import frontpage
import os

app = Flask(__name__, template_folder='templates')

@app.route('/')
def hello_world():
	return render_template('front.html')