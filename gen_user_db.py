import sqlite3

sqlite_file = 'private/site.sqlite'

conn = sqlite3.connect(sqlite_file)
curs = conn.cursor()

curs.execute('''
		CREATE TABLE users(id INTEGER PRIMARY KEY unique, email TEXT unique, verifier TEXT, salt TEXT, confirmed NUMBER, locked NUMBER, name TEXT)
''')
curs.execute('''
		CREATE TABLE password_reset(id INTEGER PRIMARY KEY unique, email TEXT, verifier TEXT, used NUMBER, start NUMBER)
''')