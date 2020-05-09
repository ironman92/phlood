import random
import threading
import time
import urllib3



names		= []
passwords	= []
domains		= []
agents		= []

target = ''
parameters = {"username":"","password":""}



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
		agent = random.choice(agents)
		while agent['chance'] < random.randint(0, 1000)/10:
			agent = random.choice(agents)
		return (email, password, agent['agent'])

	def __init__(self, proxy_list):
		threading.Thread.__init__(self)
		self.stop_execution = False
		self.proxy_list = proxy_list
		self.start()

	def stop(self):
		self.stop_execution = True
		self.join()

	def run(self):
		while not self.stop_execution:
			print("\n\n\n")
			proxy_info = None
			try:
				address = self.proxy_list.random()
				credentials = worker.generate_credentials()
				submission = {parameters["username"]:credentials[0],parameters["password"]:credentials[1]}
				if address:
					proxy = urllib3.ProxyManager(address, num_pools=1)
					proxy_info = proxy.request('POST', target, fields=submission, timeout=15, retries=1)
				else:
					time.sleep(10)
			except:
				time.sleep(0.01)
			finally:
				time.sleep(0.01)
