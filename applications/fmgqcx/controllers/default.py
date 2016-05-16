@auth.requires_login()
def index():
	return dict()

def login():
	return dict(form = auth.login())

def logout():
	return dict(form=auth.logout())
