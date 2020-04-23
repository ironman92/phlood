import threading
from bs4 import BeautifulSoup
import random
import urllib3
#import json
import time



class proxy_list(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.lock = threading.RLock()
		self.stop_execution = True
		self.list = []
		self.sources = []

	def start(self):
		self.stop_execution = False
		threading.Thread.start(self)

	def stop(self):
		self.stop_execution = True
		self.join()

	def run(self):
		http = urllib3.PoolManager(num_pools=1)
		while not self.stop_execution:
			time.sleep(0)
			my_ip = http.request('GET', 'http://httpbin.org/ip').data
			for source in self.sources:
				if self.stop_execution:
					break
				time.sleep(0)
				r = http.request('GET', source['url'])
				if r.status != 200:
					continue
				page = BeautifulSoup(r.data, 'html.parser')
				for record in page.select(source['record']):
					if self.stop_execution:
						break
					time.sleep(0)
					address = ''
					if source['protocol']:
						if source['protocol_dictionary']:
							address = address + protocol_dictionary[record.select_one(source['protocol'])]
						else:
							address = address + record.select_one(source['protocol'])
					address = address + record.select_one(source['ip'])
					if source['port']:
						address = address + ':' + record.select_one(source['port']).text
					with self.lock:
						if address in self.list:
							continue
					proxy = urllib3.ProxyManager(address, num_pools=1)
					try:
						proxy_info = proxy.request('GET', 'http://httpbin.org/ip')
					except:
						continue
					if proxy_info.status != 200:
						continue
					if proxy_info.data == my_ip:
						continue
					with self.lock:
						self.list.append(address)
				for record in self.list:
					if self.stop_execution:
						break
					time.sleep(0)
					try:
						proxy_info = http.request('GET', 'http://httpbin.org/ip')
					except:
						with self.lock:
							self.list.remove(record)
					if proxy_info.status == 200 and proxy_info.data != my_ip:
						continue
					with self.lock:
						self.list.remove(record)

	def add_source(self, url, record, ip, port=None, protocol=None, protocol_dictionary=None):
		source = {
			'url':					url,
			'record':				record,
			'ip':					ip,
			'port':					port,
			'protocol':				protocol,
			'protocol_dictionary':	protocol_dictionary
		}
		with self.lock:
			if source in self.sources:
				return False
			self.sources.append(source)
			return True

	def random(self):
		if len(self.list) == 0:
			return None
		with self.lock:
			return random.choice(self.list)
