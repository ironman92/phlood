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
persistence = {}
if os.path.isfile('persistence.json'):
	with open('persistence.json', 'r') as persist:
		persistence = json.loads(persist.read())
worker.names        = persistence['names']
worker.passwords    = persistence['passwords']
worker.domains      = persistence['domains']
worker.agents       = persistence['agents']



proxy = proxy_list.proxy_list()
proxy.source_list = persistence['sources']



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
		print(	"Help   Display this help text\n" +
				"Status Displays quick status\n" +
				"Source Manage proxy sources\n" +
				"Exit   Stops all threads and exits program\n")
		continue
	if command[0] == 'status':
		print("\tIP: " + proxy.my_ip)
		print("\tProxies: " + str(len(proxy.active_proxy_list)))
		with proxy.source_lock:
			print("\tProxy Sources: " + str(len(proxy.source_list)))
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
		continue
	print("Unknown command: " + command[0])



print("Exiting...")
proxy.stop()
with open('persistence.json', 'w') as persist:
	json.dump(persistence, persist)
