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
				"Help\tDisplay this help text\n" +
				"Status\tDisplays quick status\n" +
				"Exit\tStops all threads and exits program\n")
		continue
	if command[0] == 'status':
		print("Status")
		print("\tIP: " + proxy.my_ip)
		print("\tProxies: " + str(len(proxy.list)))
		continue
	print("Unknown command: " + command)



print("Exiting...")
proxy.stop()
