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



while True:
	command = input("\n\n===================\nAvailable Commands:\n" +
					"\tExit\tStops all threads and exits program\n" +
					"\tStatus\tDisplays quick status\n"
					">").split()
	if len(command) == 0:
		continue
	if command[0].strip().lower() == 'exit':
		break
	if command[0].strip().lower() == 'status':
		print("Proxies: " + str(len(proxy.list)))



print("Exiting...")
proxy.stop()
