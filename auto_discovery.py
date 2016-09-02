from subprocess import *
from multiprocessing import Process, Manager
import sys
import time

import requests
import datetime
import netifaces
import ipaddress


from gui import GUI
import tkinter


class Host():

	__vendors_url =  "http://api.macvendors.com/"

	def __init__(self, ip):
		self.ip = ip
		self.discovery_time = "Unknown"
		self.last_discovery_time = "Unknown"
		self.mac_address = "Unknown"
		self.last_mac_address = "Unknown"
		self.vendor = "Unknown"
		self.state = "Unknown"
		self.latency = 0

	def define_server_host(self):
		self.latency = 0;
		self._get_vendor()
		self.state("Up")

	def _teste(self):
		print(self.ip)
		self.ip = "192.168.25.2"

	def _get_mac_address(self, deprecateds):
		cmd = "arp -n " + self.ip
		process = Popen(cmd, shell=True, stdout=PIPE)
		saida, erro = process.communicate()
		if len(saida.split()) < 8:
			print("Erro ao pegar MAC de " + self.ip)
			self.mac_address = "Unknown"
			return

		mac_address = saida.split()[8].decode()

		if self.mac_address == "Unknown":
			self.mac_address = mac_address
		elif self.mac_address == mac_address:
			return
		else:
			self._deprecate(deprecateds)
			self.mac_address = mac_address
			self.discovery_time = datetime.datetime.now()
		self._get_vendor()


	def _deprecate(self, deprecateds):
		if self.last_mac_address not in deprecateds:
			deprecateds[self.mac_address] = ([self.ip], [self.last_polled], [self.discovery_time])
		else:
			deprecateds[self.mac_address][1].append(self.ip)
			deprecateds[self.mac_address][2].append(self.last_polled)
			deprecateds[self.mac_address][3].append(self.discovery_time)


	def _set_state(self, state, ups, downs):
		if self.ip in ups.keys() and state == "Down":
			ups.pop(self.ip)
			downs[self.ip] = self.get_state()

		elif self.ip in downs.keys() and state == "Up":
			downs.pop(self.ip)
			ups[self.ip] = self.get_state()

		elif state == "Up":
			ups[self.ip] = self.get_state()

		elif state == "Down" or state == "Unknown":
			downs[self.ip] = self.get_state()

		self.state = state


	def get_state(self):
		return (self.mac_address, self.last_polled, self.vendor, self.latency)


	def poll(self, ups, downs, deprecateds):
		ping = Popen("ping -c 1 "+self.ip, shell=True, stdout=PIPE)
		saida, erro = ping.communicate()
		latency = saida.split()[13].decode()
		self.last_polled = datetime.datetime.now()
		if "errors" in saida.decode():
			self.latency = 0
			self._set_state("Down", ups, downs)
		elif "1 received" in saida.decode():
			self._get_mac_address(deprecateds)
			self.latency = float(latency[5:])
			self._set_state("Up", ups, downs)
		else:
			self.latency = 0
			self._set_state("Unknown", ups, downs)


	def _get_elapsed_time(self):
		td = datetime.datetime.now() - self.last_polled
		if td.days > 0:
			time_delta_string = ">1 day ago"
		elif td.seconds > 3600:
			hours = td.seconds / 3600
			if hours >= 2:
				time_delta_string = str(int(hours)) + " hours ago"
			else:
				time_delta_string = str(int(hours)) + " hour ago"
		elif td.seconds > 60:
			minutes = td.seconds / 60
			if minutes >= 2:
				time_delta_string = str(int(minutes)) + " minutes ago"
			else:
				time_delta_string = str(int(minutes)) + " minute ago"
		else:
			time_delta_string = str(td.seconds) + " seconds ago"

		return time_delta_string


	def _get_vendor(self):
		if self.mac_address == "Unknown":
			self.vendor = "Unknown"
			return

		request = requests.get(self.__vendors_url+self.mac_address)

		if request.status_code == 200:
			self.vendor = request.content.decode()
		else:
			self.vendor = "Unknown"


	def __str__(self):
		if (self.state == "Up"):
			return self.ip + " " + self.mac_address + " " + self.vendor + " " + str(self.router) + " " + self.state + " " + self._get_elapsed_time()
		else:
			return self.ip + " " + self.state + " " + self._get_elapsed_time()

####################################################################################################################################

class Net_Infos():

	def __init__(self):
		self.requester_ip = "Unknown"
		self.requester_mac = "Unknown"
		self.net_conf = "Unknown"
		self.net_mask = "Unknown"
		self.net_gateway = "Unknown"
		self._get_operational_interface()
	
	def _get_operational_interface(self):
		avaible_interfaces = netifaces.interfaces()
		for interface in avaible_interfaces:
			if interface == "eth0" or interface == "wlan0":
				interface_info = netifaces.ifaddresses(interface)
				if netifaces.AF_INET in interface_info.keys():
					target_interface = interface_info[netifaces.AF_INET][0]
					net_conf_prepare = target_interface['addr'].split('.')
					self.requester_mac = interface_info[netifaces.AF_LINK][0]['addr']
					self.requester_ip = target_interface['addr']
					self.net_conf = net_conf_prepare[0] + "." + net_conf_prepare[1] + "." + net_conf_prepare[2] + ".0"
					self.net_mask = target_interface['netmask']
					self.net_gateway = netifaces.gateways()[netifaces.AF_INET][0][0]
					break
		

	def __str__(self):
		return self.net_conf + " " + self.net_mask + " " + self.net_gateway

####################################################################################################################################

class NetController():

	def __init__(self):
		self._initialize_net_infos()
		manager = Manager()
		self.up_devices = manager.dict()
		self.down_devices = manager.dict()
		self.deprecated_devices = manager.dict()
		self.alive = True
		self.gui = GUI()
		self._start_gui()
		self._start_hosts()

	def _start_gui(self):
		self.gui.update()
		#proc = Process(target=self._gui_loop, args=(self.gui))
		#proc.start()

	def _gui_loop(self, gui):
		#self.gui = GUI()
		gui.mainloop()
		#alive = False
		#como parar o outro processo?
		print("It's dead")

	def _initialize_net_infos(self):
		self.net_infos = Net_Infos()
		if self.net_infos.net_conf == "Unknown":
			print("Invalid network.")
			exit(0)

		self.network_ips = ipaddress.ip_network(self.net_infos.net_conf + "/" + self.net_infos.net_mask).hosts()

	def _start_hosts(self):
		self.hosts = []
		c = 1
		for host_ip in self.network_ips:
			if str(host_ip) == self.net_infos.requester_ip:
				continue

			host = Host(str(host_ip))
			self.hosts.append(host)
			c += 1
			if c == 5:
				break

	def regular_check(self, poll_frequency):
		while True:
			procs = []
			for host in self.hosts:
				if host.ip == self.net_infos.requester_ip:
					continue
				proc = Process(target=host.poll, args=(self.up_devices, self.down_devices, self.deprecated_devices))
				proc.start()
				procs.append(proc)

			for proc in procs:
				proc.join()
			
			#self.print_tables()
			
			try:
				self.update_tables()
			except:
				break
			

			time.sleep(poll_frequency)

		print("System is dead, I'm now exiting...")

	def update_tables(self):
		self.gui.update_tables(self.up_devices, self.down_devices, self.deprecated_devices)

	def print_tables(self):
		################Testes####################
		print("\n\n\n")

		for host in self.up_devices.keys():
			print(host + str(self.up_devices[host]))

		print("\n\n\n")

		for host in self.down_devices.keys():
			print(host + str(self.down_devices[host]))

		print("\n\n\n")

		for host in self.deprecated_devices.keys():
			print(host + str(self.deprecated_devices[host]))
		#########################################





#######################################################################################################################
if len(sys.argv) != 2:
	print("Usage: python3 auto_discovery.py <poll frequency(seconds)>")
	print("Example: python3 auto_discovery.py 60")
	exit(0)

poll_frequency = int(sys.argv[1])

nc = NetController()
nc.regular_check(poll_frequency)

#teste = GUI()
#mainloop