from flask_login import LoginManager, UserMixin

class User(UserMixin):

    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

    def is_authenticated(self):
    	return True

    def is_anonymous(self):
    	return False

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.email)