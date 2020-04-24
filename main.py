print("Loading...")



# Version Check
from platform import python_version
if python_version()[0] != '3':
	print("Must be run with python 3")
	exit()



# Imports
import argparse
import time
import proxy_list
import random



# Parse Command Line Arguments
parser = argparse.ArgumentParser(description='''
	CNS 210 Class Project
	PHlood 2020-05-09
	CIS 210 2020
	Morgan Matchette & Ryan Stark''')
argument = parser.parse_args()



proxy = proxy_list.proxy_list()
proxy.add_source("https://free-proxy-list.net",		"#proxylisttable tbody tr",	"td:nth-child(1)",	"td:nth-child(2)",	"td:nth-child(7)",	{'no':'http://','yes':'https://'}	)
#proxy.add_source("https://us-proxy.org",			"",	"",	""	)
#proxy.add_source("https://hidemy.name/proxy-list",	"",	"",	""	)
#proxy.add_source("https://socks-proxy.net",			"",	"",	""	)
#proxy.add_source("https://sslproxies.org",			"",	"",	""	)
proxy.start()



with open('names.txt', 'r') as name_list:
	names = name_list.read().splitlines()
with open('passwords.txt', 'r') as password_list:
	passwords = password_list.read().splitlines()
with open('domains.txt', 'r') as domain_list:
	domains = domain_list.read().splitlines()



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
	while len(password) < 8: # TODO : further validation
		password = ''
		while random.randint(0, 4):
			choice = random.choice(choices)
			start = random.randint(0, len(choice))
			stop = random.randint(start, len(choice))
			password = password + choice[start:stop]
	return (email, password)



print("Ready")
while True:
	raw_command = input("\n>")
	command = raw_command.split()
	for i in range(len(command)):
		command[i] = command[i].strip().lower()
	if len(command) == 0:
		continue
	if command[0] == 'exit':
		break
	if command[0] == 'help':
		print(	"Available Commands:\n" +
				"===================\n" +
				"Help	Display this help text\n" +
				"Status	Displays quick status\n" +
				"Source	Manage proxy sources\n" +
				"Exit	Stops all threads and exits program\n")
		continue
	if command[0] == 'status':
		print("Status")
		print("\tIP: " + proxy.my_ip)
		print("\tProxies: " + str(len(proxy.list)))
		print("\tProxy Sources: " + str(len(proxy.sources)))
		continue
	if command[0] == 'source':
		if len(command) < 2 or command[1] == 'help':
			print(	"Source Information\n" +
					"Options===========\n" +
					"Help	Display this help text\n" +
					"List	Lists all options\n" +
					"Add	Add source ( interactive )\n" +
					"Drop	Remove source")
			continue
		if command[1] == 'list':
			for source in proxy.sources:
				print(source['url'])
		if command[1] == 'add':
			url					= input("URL: ").strip()
			record				= input("CSS Record Selector: ").strip()
			ip					= input("                 IP: ").strip()
			port				= input("               Port: ").strip()
			protocol			= input("           Protocol: ").strip()
			protocol_dictionary = {}
			while True:
				protocol_lookup = input("Protocol Interpretation: ").strip()
				if not protocol_lookup:
					break
				p = protocol_lookup.split()
				if len(p) != 2:
					continue
				protocol_dictionary[p[0]] = p[1]
			confirm = input("Confirm Add of above information [Yes|No]: ")
			if len(confirm) > 0 and confirm[0].lower() == 'y':
				proxy.add_source(url, record, ip, port, protocol, protocol_dictionary)
		continue
	print("Unknown command: " + command[0])



print("Exiting...")
proxy.stop()
