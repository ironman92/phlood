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
import os
import json
import worker



# Parse Command Line Arguments
parser = argparse.ArgumentParser(description='''
	CNS 210 Class Project
	PHlood 2020-05-09
	CIS 210 2020
	Morgan Matchette & Ryan Stark''')
argument = parser.parse_args()



# Load persistence
persistence = {
	'names': [],
	'passwords': [],
	'domains': [],
	'agents': [],
	'sources': [],
	'proxies': []
}
if os.path.isfile('persistence.json'):
	with open('persistence.json', 'r') as persist:
		persistence = json.loads(persist.read())
worker.names        = persistence['names']
worker.passwords    = persistence['passwords']
worker.domains      = persistence['domains']
worker.agents       = persistence['agents']



proxy = proxy_list.proxy_list()
proxy.source_list = persistence['sources']
proxy.potential_proxy_list = persistence['proxies']
proxy.start()


worker_list = []


print("Ready")
while True:
	raw_command = input("\nPHlood>")
	command = raw_command.split()
	for i in range(len(command)):
		command[i] = command[i].strip().lower()
	if len(command) == 0:
		continue

	if command[0] == 'exit':
		break

	if command[0] == 'help':
		print(	"Help     Display this help text\n" +
				"Status   Displays quick status\n" +
				"Source   Manage proxy sources\n" +
				"Proxy    Manage proxies\n" +
				"worker	  Manage worker threads\n" +
				"Sample n Sample crential(s). Optionally add number to fetch n samples\n" +
				"Exit     Stops all threads and exits program")
		continue

	if command[0] == 'status':
		print("IP: " + proxy.my_ip)
		with proxy.source_lock:
			print("Proxy Sources:     " + str(len(proxy.source_list)))
		with proxy.potential_proxy_list_lock:
			print("Potential Proxies: " + str(len(proxy.potential_proxy_list)))
		with proxy.active_proxy_list_lock:
			print("Active Proxies:    " + str(len(proxy.active_proxy_list)))
		print("Names:     " + str(len(persistence['names'])))
		print("Passwords: " + str(len(persistence['passwords'])))
		print("Domains:   " + str(len(persistence['domains'])))
		print("Agents:    " + str(len(persistence['agents'])))
		print("Workers:   " + str(len(worker_list)))
		continue

	if command[0] == 'source':
		if len(command) < 2 or command[1] == 'help':
			print(	"Source Help        Display this help text\n" +
					"Source List        Lists all options\n" +
					"Source Add         Add source ( interactive )\n" +
					"Source Remove url  Remove source")
			continue
		if command[1] == 'list':
			with proxy.source_lock:
				for source in proxy.source_list:
					print(source['url'])
			continue
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
		if command[1] == 'remove':
			if len(command) < 3:
				print("Missing url")
			proxy.remove_source(command[2])
			continue
		print("Unknown command: " + command[1])
		continue

	if command[0] == 'proxy':
		if len(command) < 2 or command[1] == 'help':
			print(	"Proxy Help         Display this help text\n" +
					"Proxy List type    List proxies. Substitute type for Potential or Active\n" +
					"Proxy Drop url     Drop proxy with given address\n" +
					"Proxy Add url      Add potential proxy with given address\n" +
					"Proxy Purge        Purge all proxies")
			continue
		if command[1] == 'list':
			if len(command) < 3:
				print("Missing type")
				continue
			if command[2] == 'potential':
				with proxy.potential_proxy_list_lock:
					for prox in proxy.potential_proxy_list:
						print(prox)
				continue
			if command[2] == 'active':
				with proxy.active_proxy_list_lock:
					for prox in proxy.active_proxy_list:
						print(prox)
				continue
			print("Unknown type: " + command[2])
			continue
		if command[1] == 'add':
			if len(command) < 3:
				print("Missing url")
				continue
			with proxy.potential_proxy_list_lock:
				if command[2] not in proxy.potential_proxy_list:
					proxy.potential_proxy_list.append(command[2])
			continue
		if command[1] == 'drop':
			if len(command) < 3:
				print("Missing url")
				continue
			with proxy.potential_proxy_list_lock:
				if command[2] in proxy.potential_proxy_list:
					proxy.potential_proxy_list.remove(command[2])
					with proxy.active_proxy_list_lock:
						if command[2] in proxy.active_proxy_list:
							proxy.active_proxy_list.remove(command[2])
				else:
					print("Proxy does not exist")
			continue
		if command[1] == 'purge':
			with proxy.potential_proxy_list_lock, proxy.active_proxy_list_lock:
				proxy.active_proxy_list = []
				proxy.potential_proxy_list = []
			continue
		print("Unknown command: " + command[1])
		continue

	if command[0] == 'worker':
		if len(command) < 2 or command[1] == 'help':
			print(	"Worker Help	Display this help text\n" +
					"Worker Start n	Starts n Worker threads\n" +
					"Worker Kill n	Kills n Worker threads")
			continue
		if command[1] == 'start':
			n = 1
			if len(command) > 2:
				n = int(command[2])
			for i in range(n):
				worker_list.append(worker.worker())
			continue
		if command[1] == 'kill':
			n = 1
			if len(command) > 2:
				n = int(command[2])
			while n > 0 and len(worker_list):
				n = n - 1
				worker_list.pop().stop()
			continue
		print("Unknown command " + command[1])
		continue

	if command[0] == 'sample':
		size = 1
		if len(command) > 1:
			try:
				size = int(command[1])
			except:
				print("Invalid input: " + command[1] + " must be an integer")
				continue
		for i in range(size):
			sample = worker.worker.generate_credentials()
			print("\nEmail:      " + sample[0])
			print("Password:   " + sample[1])
			print("User Agent: " + sample[2])
		continue

	print("Unknown command: " + command[0])



print("Exiting...")
proxy.stop()
with open('persistence.json', 'w') as persist:
	json.dump(persistence, persist)
while len(worker_list):
	worker_list.pop().stop()
