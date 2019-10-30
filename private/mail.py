from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

#replace this with your own method to send mail
def send(to, subject, message):
	msg = MIMEMultipart()

	password = "example"

	msg['From'] = "example@example"
	msg['To'] = to
	msg['Subject'] = subject
	msg.attach(MIMEText(message, 'plain'))

	server = smtplib.SMTP('smtp.example: 587')
	server.starttls()
	server.login(msg['From'], password)
	server.sendmail(msg['From'], msg['To'], msg.as_string())
	server.quit()

	print(message)
