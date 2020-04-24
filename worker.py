import random
import threading
import time



with open('names.txt', 'r') as name_list:
	names = name_list.read().splitlines()
with open('passwords.txt', 'r') as password_list:
	passwords = password_list.read().splitlines()
with open('domains.txt', 'r') as domain_list:
	domains = domain_list.read().splitlines()



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