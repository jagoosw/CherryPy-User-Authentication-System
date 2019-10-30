# CherryPy User Authentication System

This is a CherryPy user authentication system. I built it and have used it on a couple quite successfully including one with quite high traffic. This code is about as far from perfect as you could imagine and isn't very neat becuase it was never written with the long term in mind. There is some refactoring and general system redesign that could be done.
## How to use
This is by no means a simple task, you will first have to spend a while learning how its doing what and then go through and make your own pages and content.

Then you need to:
1. Run `gen_user_db.py`
2. Change the email and password in mail.py and make it work, this is magical and you'd probably be better off just filling mail.send() with your own method for sending emails
3. Get some https certificates and replace the lovely ascii art with them
4. Choose a port and ip address at the bottom of main.py

## To do
This list could be nearly infinite since theres a lot that could be changed about this whole thing. In a random order some of the things I've though of so far are:
1. Add some comments to make it more usable
2. Sort out the email confirmation functionality
3. Sort out the logging, its very bad and poor for actual security puroposes and also the error log grows huge
4. Refactor the code so that it is much easier for someone that isn't me to use, think this will involve splitting the main script into lots of different things and making a proper set up code and then some way for people to add their protected and un protected content much more easily
5. Make the website look nice, the intention of this project was never the front end but for 4 to be useful then this needs to be done
