import threading
from bs4 import BeautifulSoup
import random
import urllib3
import json
import time



class proxy_list:
	def __init__(self):
		threading.Thread.__init__(self)
		self.list_lock = threading.RLock()
		self.source_lock = threading.RLock()
		self.stop_execution = True
		self.list = []
		self.sources = []
		self.update_my_ip()
		self.clean_list_thread = threading.Thread(target=self.run_clean_list)
		self.proxy_add_thread = threading.Thread(target=self.run_proxy_add)

	def start(self):
		self.stop_execution = False
		self.proxy_add_thread.start()
		self.clean_list_thread.start()

	def stop(self):
		self.stop_execution = True
		self.clean_list_thread.join()
		self.proxy_add_thread.join()

	def update_my_ip(self):
		http = urllib3.PoolManager(num_pools=1)
		self.my_ip = json.loads(http.request('GET', 'http://httpbin.org/ip').data)['origin']
		self.my_ip_updated = time.time()

	def test_proxy(self, address):
		if self.my_ip_updated + 60 < time.time():
			self.update_my_ip()
		proxy_valid = False
		try:
			proxy = urllib3.ProxyManager(address, num_pools=1)
			proxy_info = proxy.request('GET', 'http://httpbin.org/ip')
			if proxy_info.status == 200 and json.loads(proxy_info.data)['origin'] != self.my_ip:
				proxy_valid = True
		except:
			proxy_valid = False
		finally:
			if address in self.list and not proxy_valid:
				with self.list_lock:
					self.list.remove(address)
			if address not in self.list and proxy_valid:
				with self.list_lock:
					self.list.append(address)
		return proxy_valid

	def run_clean_list(self):
		index = 0
		while not self.stop_execution:
			time.sleep(0)
			with self.list_lock:
				if index >= len(self.list):
					index = 0
					time.sleep(1)
					continue
				record = self.list[index]
			if self.test_proxy(record):
				index = index + 1

	def run_proxy_add(self):
		http = urllib3.PoolManager(num_pools=1)
		while not self.stop_execution:
			time.sleep(0)
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
							if record.select_one(source['protocol']).text not in source['protocol_dictionary']:
								print("Unknown protocol: " + record.select_one(source['protocol']).text)
								continue
							address = address + source['protocol_dictionary'][record.select_one(source['protocol']).text]
						else:
							address = address + record.select_one(source['protocol']).text
					address = address + record.select_one(source['ip']).text
					if source['port']:
						address = address + ':' + record.select_one(source['port']).text
					self.test_proxy(address)

	def add_source(self, url, record, ip, port='', protocol='', protocol_dictionary={}):
		source = {
			'url':					url,
			'record':				record,
			'ip':					ip,
			'port':					port,
			'protocol':				protocol,
			'protocol_dictionary':	protocol_dictionary
		}
		with self.source_lock:
			if source in self.sources:
				return False
			self.sources.append(source)
			return True

	def random(self):
		with self.list_lock:
			if len(self.list) == 0:
				return None
			return random.choice(self.list)
