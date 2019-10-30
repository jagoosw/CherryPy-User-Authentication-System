import sqlite3, random, string
from cherrypy import log

user_db = 'private/site.sqlite'

conn = sqlite3.connect(user_db)
curs = conn.cursor()

print(curs.execute('''SELECT * FROM 'auth_codes' LIMIT 0,30''').fetchall())

auth_code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits +string.ascii_lowercase) for _ in range(12))
name = str(input("Name: "))

curs.execute('''INSERT INTO auth_codes(name, code) VALUES(?,?)''', (name,auth_code,))
conn.commit()

print(auth_code)
log("Authorisation code generated locally")
