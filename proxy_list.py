import threading
from bs4 import BeautifulSoup
import random
import urllib3
import json
import time



class proxy_list:
	def __init__(self):
		threading.Thread.__init__(self)
		self.potential_proxy_list_lock = threading.RLock()
		self.active_proxy_list_lock = threading.RLock()
		self.source_lock = threading.RLock()
		self.my_ip_lock = threading.RLock()
		self.stop_execution = True
		self.potential_proxy_list = []
		self.active_proxy_list = []
		self.source_list = []
		self.my_ip = None
		self.my_ip_updated = 0
		self.update_my_ip()
		self.proxy_add_thread = threading.Thread(target=self.run_proxy_add)
		self.test_proxy_thread = threading.Thread(target=self.run_test_proxy)

	def start(self):
		self.stop_execution = False
		self.proxy_add_thread.start()
		self.test_proxy_thread.start()

	def stop(self):
		self.stop_execution = True
		self.proxy_add_thread.join()
		self.test_proxy_thread.join()

	def update_my_ip(self):
		with self.my_ip_lock:
			if self.my_ip_updated + 60 < time.time():
				http = urllib3.PoolManager(num_pools=1)
				self.my_ip = json.loads(http.request('GET', 'http://httpbin.org/ip').data)['origin']
				self.my_ip_updated = time.time()

	def daemon_test_proxy(self, address):
		self.update_my_ip()
		proxy_valid = False
		try:
			proxy = urllib3.ProxyManager(address, num_pools=1)
			proxy_info = proxy.request('GET', 'http://httpbin.org/ip', timeout=15, retries=0)
			if proxy_info.status == 200 and json.loads(proxy_info.data)['origin'] != self.my_ip:
				proxy_valid = True
		except:
			proxy_valid = False
		finally:
			with self.active_proxy_list_lock:
				if address in self.active_proxy_list and not proxy_valid:
					self.active_proxy_list.remove(address)
				if address not in self.active_proxy_list and proxy_valid:
					self.active_proxy_list.append(address)
		return proxy_valid

	def run_test_proxy(self):
		heartbeat = 0
		i_thread = 0
		i_proxy = 0
		threads = []
		while not self.stop_execution:
			time.sleep(0.1)
			heartbeat = time.time()
			with self.potential_proxy_list_lock:
				if i_proxy >= len(self.potential_proxy_list):
					i_proxy = 0
				if i_proxy < len(self.potential_proxy_list) and len(threads) < 127:
					t = threading.Thread(target=self.daemon_test_proxy, args=[self.potential_proxy_list[i_proxy]])
					t.start()
					threads.append(t)
					i_proxy = i_proxy + 1
			if i_thread >= len(threads):
				i_thread = 0
			if i_thread < len(threads):
				if not threads[i_thread].is_alive():
					threads[i_thread].join()
					threads.remove(threads[i_thread])
				i_thread = i_thread + 1

	def run_proxy_add(self):
		http = urllib3.PoolManager(num_pools=1)
		index = 0
		heartbeat = 0
		while not self.stop_execution:
			time.sleep(0.01)
			with self.source_lock:
				if index >= len(self.source_list):
					index = 0
					continue
				if index == 0 and heartbeat + 60 > time.time():
					continue
				heartbeat = time.time()
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
				with self.potential_proxy_list_lock:
					if address not in self.potential_proxy_list:
						self.potential_proxy_list.append(address)

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
