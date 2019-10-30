import cherrypy, random, sqlite3, hashlib, binascii, os, json, random, html, time, shutil
from cherrypy import log
from private import mail
from cherrypy.lib import file_generator
import networkx as nx

site_name = "Website"
site_url = "example.com"
admin_email = "example@example"

user_db = 'private/site.sqlite'

def check_password(password):
	valids = list()

	valids.append(any(c.islower() for c in password))
	valids.append(any(c.isupper() for c in password))
	valids.append(any(c.isdigit() for c in password))
	#valids.append(any(not c.isalnum() for c in password))

	if 8<=len(password)<128:
		valids.append(True)
	else:
		valids.append(False)

	valid = True
	for c in valids:
		if c != True:
			valid = False

	return valid

def authenticate():
	try:
		auth = cherrypy.session['authenticated']
	except:
		auth = cherrypy.session['authenticated'] = False
		cherrypy.session['user'] = None

	return auth

def protect(page):
	auth = authenticate()
	if auth == True:
		out = page
	else:
		out = str.encode(open("template.html").read()%("Authentication Failure", "none.js", "Authentication Failure",  "You must be logged in to view this page, please log in or sign up above to continue"))
	return out

def page(short_title, title, content, script=None):
	if script == None:
		script = "none.js"

	return str.encode(open("template.html").read()%(short_title, script, title, content))

@cherrypy.expose
class Site(object):
	@cherrypy.expose
	def index(self):
		if authenticate() == True:
			out = page("Home","Home",open("private/protected_list.html").read())
		else:
			out = page("Home","Home",open(os.path.join("index.html")).read())
		return out

	@cherrypy.expose
	def authentication(self, confirm=None, id=None, string=None, reset=None):
		if authenticate() == True:
			raise cherrypy.HTTPRedirect("/account")
		else:
			out = page("Login and Sign Up", "Login and Sign Up", open("private/authentication_content.html").read(), "authentication.js")
		return out

	#This is a not protected page and can be used ass an example
	@cherrypy.expose
	def account(self, ):
		return protect(page("Account", "Account Settings", open("private/account_content.html").read(), "account.js"))

	#Protected page example
	@cherrypy.expose
	def some_protected_content(self):
		#do some stuff here
		return protect(page("Some protected page", "Protected page", open("private/some_protected_content.html").read(), "none.js"))

	#this is an example of some protected content, like an image
	@cherrypy.expose
	def pretty_picture(self):
		if authenticate() == True:
			cherrypy.response.headers['Content-Type']= "image/png" 
			f = open("private/pretty_picture.jpeg", "rb") 
			out = f.read() 
			f.close()
		else:
			raise cherrypy.HTTPRedirect("/")
		return out

@cherrypy.expose
class Login(object):
	def POST(self, email=None, password=None):
		#will return - 0 for success, 1 for failure, 2 for need to confirm, 3 not meant to be here
		Failure = "The information you entered was invalid"
		if email == None or password == None:
			out = Failure
		else:
			time.sleep(random.randint(10,500)/1000)
			conn = sqlite3.connect(user_db)
			curs = conn.cursor()

			checks = curs.execute('''SELECT verifier, salt, confirmed, locked FROM users WHERE email=?''', (email,)).fetchone()

			if checks == None:
				out = Failure
				log("Access:{user:\""+email+"\",type:\"Incorrect email\",ip:\""+cherrypy.request.remote.ip+"\"}")
			else:
				check_verifier = hashlib.sha512((checks[1]+password).encode()).hexdigest()
				if str(checks[0]) != check_verifier:
					out = Failure
					log("Access:{user:\""+email+"\",type:\"Incorrect password\",ip:\""+cherrypy.request.remote.ip+"\"}")
				else:
					"""
					May make this work at some point
					if checks[2] != 1:
						out = "You need to confirm your email before you can login"
						log("Access:{user:\""+email+"\",type:\"Not confirmed\",ip:\""+cherrypy.request.remote.ip+"\"}")
					else:
						if checks[3] != 0:
							out = "Your account is locked, contact an administrator"
							log("Access:{user:\""+email+"\",type:\"Account locked\",ip:\""+cherrypy.request.remote.ip+"\"}")
						else:"""
					cherrypy.session["authenticated"] = True
					cherrypy.session["user"] = email
					log("Access:{user:\""+email+"\",type:\"User logged in\",ip:\""+cherrypy.request.remote.ip+"\"}")
					out = str(0)
		return out

@cherrypy.expose
class Reset(object):
	def POST(self, email=None, string=None, password=None, password_conf=None):
		out = dict()
		#will return - 0 for success, 1 for failure, 2 for need to confirm, 3 not meant to be here
		Failure = "The information you entered was invalid"
		if email == None:
			out["status"] = Failure

		#Deals with question answers
		elif string==None:
			conn = sqlite3.connect(user_db)
			curs = conn.cursor()
			#there was a method for having authentication questions but they're annoying and no one likes them so I took them away but there might still be some reminance... sorry
			if checks == None:
				out["status"] = "There has been an error, please start again"
			else:
				out["status"] = "0"
				reset_string = binascii.hexlify(os.urandom(64)).decode()
				reset_time = time.time()

				old_resets = curs.execute('''SELECT used FROM password_reset WHERE email=?''', (email,)).fetchone()

				if old_resets != None:
					curs.execute('''DELETE FROM password_reset WHERE email=?''', (email,))

				curs.execute('''INSERT INTO password_reset(email, verifier, used, start) VALUES(?,?,?,?)''', (email, reset_string, 0, reset_time))
					
				curs.execute('''UPDATE users SET locked=1 WHERE email=?''', (email,))

				conn.commit()

				log("Access:{user:\""+email+"\",type:\"Password reset email sent\",ip:\""+cherrypy.request.remote.ip+"\"}")
				##mail.send((email,"Password reset for "+site_name, "Hi!\n\nHeres the password reset string for "+site_name+"\nPlease got to back to the page where you requested the reset and enter the following code:\n\n"+reset_string+"\n\nThanks, "+site_name+" team")

		#Deals with reset string
		elif string!=None:
			conn = sqlite3.connect(user_db)
			curs = conn.cursor()

			checks = curs.execute('''SELECT	email, verifier, used, start FROM password_reset WHERE email=?''', (email,)).fetchone()
			salt = curs.execute('''SELECT	salt FROM users WHERE email=?''', (email,)).fetchone()
			if checks[0] != email:
				status = Failure

			elif checks[1] != string:
				status = "Reset string invalid"
				log("Access:{user:\""+email+"\",type:\"Password reset, step 3, incorrect reset string\",ip:\""+cherrypy.request.remote.ip+"\"}")

			elif checks[2] != 0:
				status = "Reset string used, please start again"
				log("Access:{user:\""+email+"\",type:\"Password reset, step 3, reset string already used\",ip:\""+cherrypy.request.remote.ip+"\"}")

			elif (int(checks[3])+600) < time.time():
				print(checks[3], time.time())
				status = "Reset string expired, please start again"
				log("Access:{user:\""+email+"\",type:\"Password reset - reset string expired\",ip:\""+cherrypy.request.remote.ip+"\"}")

			elif password != password_conf:
				status = "The passwords do not match"

			elif check_password(password) != True:
				status = "Your password was not suitable, it must contain an upper and lower case letter, a number, a special character (e.g. # or @ or /) and be between 10 and 128 characters long"

			else:
				status = "0"
				cherrypy.session["authenticated"] = True
				cherrypy.session["user"] = email
				verifier = hashlib.sha512((salt[0]+password).encode()).hexdigest()
				#mail.send((email, "Password has been reset for "+site_name, "Hi,\n\nJust to let you know the password for your account was reset at "+time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())+". If this was not you please contact the site administrator.\n\nThanks, "+site_name+" team")
				curs.execute('''UPDATE users SET locked=0, verifier=? WHERE email=?''', (verifier, email))
				log("Access:{user:\""+email+"\",type:\"Password reset success\",ip:\""+cherrypy.request.remote.ip+"\"}")
				conn.commit()

			out["status"] = status

		return json.dumps(out)

@cherrypy.expose
class Signup(object):
	def POST(self, email=None, email_conf=None, password=None, password_conf=None, name=None):
		#will return - 0 for success, 1 for email taken, 2 for password in adequate, 3 for no entry
		if email == None or password == None or email_conf == None or password_conf == None or name == None:
			out = "Not all vales entered, this should not happen"

		if email != email_conf:
			out = "Emails do not match"
		elif password != password_conf:
			out = "Passwords do not match"
		else:
			conn = sqlite3.connect(user_db)
			curs = conn.cursor()
			checks = curs.execute('''SELECT id FROM users WHERE email=?''', (email,)).fetchone()
			if checks != None:
				out = "That email is already taken, please try logging in or a different email"
			elif len(name) > 10:
				out = "Display name too long, it must be 10 characters or less"
			elif check_password(password) != True:
				out = "Your password was not suitable, it must contain an upper and lower case letter, a number and be between 10 and 128 characters long"
			else:
				salt = binascii.hexlify(os.urandom(64)).decode()
				confirmer = binascii.hexlify(os.urandom(64)).decode()
				verifier = hashlib.sha512((salt+password).encode()).hexdigest()
				curs.execute('''INSERT INTO users(email, verifier, salt, confirmed, locked, name) VALUES(?,?,?,?,?,?)''', (email, verifier, salt, confirmer, 1, name))
				conn.commit()
				#confirm_url = cherrypy.request.base+"/authentication?confirm=0&id="+str(curs.lastrowid)+"&string="+confirmer
				#print(confirm_url)
				log("Access:{user:\""+email+"\",type:\"User signed up\",ip:\""+cherrypy.request.remote.ip+"\"}")
				##mail.send((email,'Confirm sign up for '+site_name, "Hi!\n\nThanks for signing up to "+site_name+"\nPlease got to "+confirm_url+" to complete your registration.\n\nThanks, "+site_name+" team")
				#mail.send((email,'Confirm sign up for '+site_name, "Hi!\n\nThanks for signing up to "+site_name+"\n\nThanks, "+site_name+" team")
				out = "0"						 
		
		return out

@cherrypy.expose
class Logout(object):
	def POST(self):
		email = cherrypy.session["user"]
		cherrypy.session["authenticated"] = False
		cherrypy.session["user"] = None
		log("Access:{user:\""+email+"\",type:\"User logged out\",ip:\""+cherrypy.request.remote.ip+"\"}")
		return "0"

"""
Not been maintained at the moment, will make work at some point
@cherrypy.expose
class Confirm(object):
	def POST(self, id=None, confirm=None):
		#Status'- 0 = Success, 1 = Incorrect id, 2 = Incorrect confirmer, 3= No Data, 4 = Already done
		Failure = "You have followed an invalid confirmation link, please try something else or contact the administrator."
		if id == None or confirm == None:
			out = Failure
		else:
			conn = sqlite3.connect(user_db)
			curs = conn.cursor()

			checks = curs.execute('''SELECT confirmed, email FROM users WHERE id=?''', (id,)).fetchone()
			
			if checks == None:
				out = Failure
			elif checks[0] == 1:
				out = "You have already confirmed your email"
			else:
				if str(checks[0]) == confirm:
					out = "Email confirmation successful, you are now logged in."
					curs.execute('''UPDATE users SET confirmed = ? WHERE id = ? ''',(1, id))
					conn.commit()
					cherrypy.session["authenticated"] = True
					cherrypy.session["user"] = checks[1]
					log("Access:{user:\""+checks[1]+"\",type:\"User confirmed email\",ip:\""+cherrypy.request.remote.ip+"\"}")
				else:
					out = Failure
		return out"""

@cherrypy.expose
class ChangePassword(object):
	def POST(self, password=None, new_password=None, new_password_conf=None):
		#will return - 0 for success, 1 for failure, 2 for need to confirm, 3 not meant to be here
		Failure = "The information you entered was invalid"

		try:
			email = cherrypy.session["user"]
		except:
			out = Failure
			email = None

		if new_password == None or password == None or new_password_conf == None or email == None:
			out = "You need to fill in all the boxes"
		else:
			conn = sqlite3.connect(user_db)
			curs = conn.cursor()

			checks = curs.execute('''SELECT verifier, salt FROM users WHERE email=?''', (email,)).fetchone()

			if checks == None:
				out = "No user found"
				log("Access:{user:\""+email+"\",type:\"Change password, incorrect password\",ip:\""+cherrypy.request.remote.ip+"\"}")
			else:
				check_verifier = hashlib.sha512((checks[1]+password).encode()).hexdigest()
				if str(checks[0]) != check_verifier:
					out = "Current password incorrect"

				else:
					if new_password != new_password_conf:
						out = "Passwords do not match"
					elif check_password(new_password) != True:
						out = "Your password was not suitable, it must contain an upper and lower case letter, a number, a special character (e.g. # or @ or /) and be between 10 and 128 characters long"
					else:
						out = "0"
						new_verifier = hashlib.sha512((checks[1]+new_password).encode()).hexdigest()
						curs.execute('''UPDATE users SET verifier=? WHERE email=?''', (new_verifier, email))
						log("Access:{user:\""+email+"\",type:\"Password changed\",ip:\""+cherrypy.request.remote.ip+"\"}")
						#mail.send((email, "Password change for "+site_name, "Hi,\n\nJust to let you know your password was changed at "+time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())+". If this was not you please contact the site administrator.\n\nThanks, "+site_name+" team")
						conn.commit()

		return out

@cherrypy.expose
class ChangeEmail(object):
	def POST(self, password=None, new_email=None, new_email_conf=None):
		#will return - 0 for success, 1 for failure, 2 for need to confirm, 3 not meant to be here
		Failure = "The information you entered was invalid"

		try:
			current_email = cherrypy.session["user"]
		except:
			out = "No user found"
			current_email = None
		if new_email == "" or password == None or new_email_conf == "" or current_email == None:
			out = "All information needs to be entered"
		else:
			conn = sqlite3.connect(user_db)
			curs = conn.cursor()

			checks = curs.execute('''SELECT verifier, salt FROM users WHERE email=?''', (current_email,)).fetchone()

			if checks == None:
				out = "No user found"
			else:
				check_verifier = hashlib.sha512((checks[1]+password).encode()).hexdigest()
				if str(checks[0]) != check_verifier:
					out = "Incorrect password"
					log("Access:{user:\""+current_email+"\",type:\"Change email, incorrect password\",ip:\""+cherrypy.request.remote.ip+"\"}")
				else:
					checks = curs.execute('''SELECT id FROM users WHERE email=?''', (new_email,)).fetchone()
					if new_email != new_email_conf:
						out = "Emails do not match"
					elif checks != None:
						out = "That email is taken"
					else:
						out = "0"
						log("Access:{user:\""+current_email+"\",type:\"Email changed\",ip:\""+cherrypy.request.remote.ip+"\"}")
						curs.execute('''UPDATE users SET email=? WHERE email=?''', (new_email, current_email))
						#mail.send((current_email, "Email change for "+site_name, "Hi,\n\nJust to let you know your email was changed at "+time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())+" to "+new_email+". If this was not you please contact the site administrator.\n\nThanks, "+site_name+" team")
						cherrypy.session["user"] = new_email
						conn.commit()

		return out

@cherrypy.expose
class Authcheck(object):
	def POST(self):
		try:
			auth = cherrypy.session['authenticated']
		except:
			auth = cherrypy.session['authenticated'] = False

		return str(auth)

if __name__ == '__main__':
	conf = {
				'/': {
						'tools.staticdir.on': True,
						'tools.staticdir.dir': os.getcwd()+"/public"
				},
				'/static': {
						'tools.staticdir.on': True,
						'tools.staticdir.dir': os.getcwd()+"/public"
				},
				'/login': {
						'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
						'tools.response_headers.on': True,
						'tools.response_headers.headers': [('Content-Type', 'text/plain')],
				},
				'/signup': {
						'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
						'tools.response_headers.on': True,
						'tools.response_headers.headers': [('Content-Type', 'text/plain')],
				},
				'/confirm': {
						'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
						'tools.response_headers.on': True,
						'tools.response_headers.headers': [('Content-Type', 'text/plain')],
				},
				'/reset': {
						'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
						'tools.response_headers.on': True,
						'tools.response_headers.headers': [('Content-Type', 'text/plain')],
				},
				'/logout': {
						'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
						'tools.response_headers.on': True,
						'tools.response_headers.headers': [('Content-Type', 'text/plain')],
				},
				'/changepassword': {
						'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
						'tools.response_headers.on': True,
						'tools.response_headers.headers': [('Content-Type', 'text/plain')],
				},
				'/changeemail': {
						'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
						'tools.response_headers.on': True,
						'tools.response_headers.headers': [('Content-Type', 'text/plain')],
				},
				'/authcheck': {
						'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
						'tools.response_headers.on': True,
						'tools.response_headers.headers': [('Content-Type', 'text/plain')],
				}
		}

	site = Site()
	site.login = Login()
	site.signup = Signup()
#	site.confirm = Confirm()
	site.reset = Reset()
	site.logout= Logout()
	site.authcheck = Authcheck()
	site.changepassword = ChangePassword()
	site.changeemail = ChangeEmail()
	cherrypy.server.ssl_module = 'builtin'
	cherrypy.server.ssl_certificate = "cert.pem"
	cherrypy.server.ssl_private_key = "privkey.pem"
	cherrypy.server.thread_pool = 30
	cherrypy.config.update({
		'server.socket_port': 8080,
		'server.socket_host': '0.0.0.0',
		'log.error_file' : "error.log",
		'log.screen' : True,
		'tools.sessions.on': True,
		})
	cherrypy.quickstart(site, '/', conf)
