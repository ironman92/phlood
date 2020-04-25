import threading
from bs4 import BeautifulSoup
import random
import urllib3
import json
import time



class proxy_list:
	def __init__(self):
		threading.Thread.__init__(self)
		self.active_proxy_list_lock = threading.RLock()
		self.source_lock = threading.RLock()
		self.stop_execution = True
		self.active_proxy_list = []
		self.source_list = []
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
			if address in self.active_proxy_list and not proxy_valid:
				with self.active_proxy_list_lock:
					self.active_proxy_list.remove(address)
			if address not in self.active_proxy_list and proxy_valid:
				with self.active_proxy_list_lock:
					self.active_proxy_list.append(address)
		return proxy_valid

	def run_clean_list(self):
		index = 0
		while not self.stop_execution:
			time.sleep(0)
			with self.active_proxy_list_lock:
				if index >= len(self.active_proxy_list):
					index = 0
					time.sleep(1)
					continue
				record = self.active_proxy_list[index]
			if self.test_proxy(record):
				index = index + 1

	def run_proxy_add(self):
		http = urllib3.PoolManager(num_pools=1)
		index = 0
		while not self.stop_execution:
			time.sleep(0.01)
			with self.source_lock:
				if index >= len(self.source_list):
					index = 0
					continue
				source = self.source_list[index]
			index = index + 1
			r = http.request('GET', source['url'])
			if r.status != 200:
				self.remove_source(source['url'])
				continue
			page = BeautifulSoup(r.data, 'html.parser')
			acknowledged_unknown_protocols = []
			for record in page.select(source['record']):
				if self.stop_execution:
					break
				time.sleep(0)
				address = ''
				if source['protocol']:
					if source['protocol_dictionary']:
						if record.select_one(source['protocol']).text not in source['protocol_dictionary']:
							self.remove_source(source['url'])
							break
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
			if source in self.source_list:
				return False
			self.source_list.append(source)
			return True

	def remove_source(self, url):
		with self.source_lock:
			for source in self.source_list:
				if source['url'] == url:
					self.source_list.remove(source)

	def random(self):
		with self.active_proxy_list_lock:
			if len(self.active_proxy_list) == 0:
				return None
			return random.choice(self.active_proxy_list)
