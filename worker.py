import random
import threading
import time



class worker(threading.Thread):
	def generate_credentials():
		domain = random.choice(domains)
		choices = [
			domain,
			random.choice(domains),
			random.choice(names),
			random.choice(names),
			random.choice(names),
			random.choice(names),
			random.choice(passwords)
		]
		email = ''
		while len(email) < 6: # TODO : further validation
			email = ''
			while random.randint(0, 2):
				choice = random.choice(choices)
				start = random.randint(0, len(choice))
				stop = random.randint(start, len(choice))
				email = email + choice[start:stop]
		email = email.lower() + '@' + domain.lower()
		password = ''
		while len(password) < 8:
			password = ''
			while random.randint(0, 4):
				choice = random.choice(choices)
				start = random.randint(0, len(choice))
				stop = random.randint(start, len(choice))
				password = password + choice[start:stop]
		return (email, password)

	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		time.sleep(0)