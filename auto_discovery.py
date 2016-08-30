from subprocess import *
import requests
import datetime
import netifaces
import ipaddress
import time


class Host():

	__vendors_url =  "http://api.macvendors.com/"

	def __init__(self, *args):
		if len(args) == 2:
			self.ip = args[0]
			self.discovery_time = datetime.datetime.now()
			self.mac_address = "Unknow"
			self.last_mac_address = "Unknow"
			self.last_discovery_time = "Unknow"
			self.router = args[1]
			self.poll()
		if len(args) == 4:
			self.ip = args[0]
			self.discovery_time = args[1]
			self.mac_address = args[2]
			self.last_mac_address = "Unknow"
			self.last_discovery_time = "Unknow"
			self.router = args[3]
			self.last_polled = datetime.datetime.now()

	def define_server_host(self):
		self.latency = 0;
		self._get_vendor()
		self._update_state("Up")

	def _update_state(self, state):
		self.state = state

	def _get_mac_address(self):
		cmd = "arp -n " + self.ip
		process = Popen(cmd, shell=True, stdout=PIPE)
		saida, erro = process.communicate()
		mac_address = saida.split()[8].decode()
		if self.mac_address == "Unknow":
			self.mac_address = mac_address
		elif self.mac_address == mac_address:
			return
		else:
			self.last_mac_address = self.mac_address
			self.mac_address = mac_address
			self.last_discovery_time = self.discovery_time
			self.discovery_time = datetime.datetime.now()


	def poll(self):
		ping = Popen("ping -c 1 "+self.ip, shell=True, stdout=PIPE)
		saida, erro = ping.communicate()
		latency = saida.split()[13].decode()
		if "time" in latency:
			self._get_mac_address()
			self._get_vendor()
			self.latency = float(latency[5:])
			self._update_state("Up")
		elif latency == '---':
			self._update_state("Down")
		else:
			self._update_state("Unknow")

		self.last_polled = datetime.datetime.now()

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
		if self.mac_address == "Unknow":
			self.vendor = "Unknow"
			return

		request = requests.get(self.__vendors_url+self.mac_address)

		if request.status_code == 200:
			self.vendor = request.content.decode()
		else:
			self.vendor = "Unknow"


	def __str__(self):
		if (self.state == "Up"):
			return self.ip + " " + self.mac_address + " " + self.vendor + " " + str(self.router) + " " + self.state + " " + self._get_elapsed_time()
		else:
			return self.ip + " " + self.state + " " + self._get_elapsed_time()

####################################################################################################################################

class Net_Infos():

	def __init__(self):
		self.requester_ip = "Unknow"
		self.requester_mac = "Unknow"
		self.net_conf = "Unknow"
		self.net_mask = "Unknow"
		self.net_gateway = "Unknow"
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

class Net_Discovery():

	def __init__(self):
		self.net_infos = Net_Infos()
		self.online_devices = []
		self.offline_devices = []
		self.deprecated_devices = []
		self._first_check_devices()

	def _first_check_devices(self):
		if self.net_infos.net_conf != "Unknow":
			network_ips = ipaddress.ip_network(self.net_infos.net_conf + "/" + self.net_infos.net_mask).hosts()
			for host_ip in network_ips:
				if int(str(host_ip).split(".")[3]) < 3 or (int(str(host_ip).split(".")[3]) > 9 and int(str(host_ip).split(".")[3]) < 12): #teste delimitador
					if str(host_ip) != str(self.net_infos.requester_ip): 
						if (str(host_ip) != self.net_infos.net_gateway):
							host_check = Host(str(host_ip), False)
							print(str(host_check)) #teste
						else:
							host_check = Host(str(host_ip), True)
							print(str(host_check)) #teste
					else:
						host_check = Host(str(self.net_infos.requester_ip), datetime.datetime.now(), str(self.net_infos.requester_mac), False)
						host_check.define_server_host()
						print(str(host_check))
					if host_check.state == "Up":
						self.online_devices.append(host_check)
					else:
						self.offline_devices.append(host_check)
		else:
			print("NO NETWORK DETECTED!!")

	def check_devices(self):
		for host in self.online_devices:
			if str(host.ip) != self.net_infos.requester_ip:
				host.poll()
				if (host.state == "Up"):
					if (host.last_mac_address != "Unknow"):
						for deprecated_host in self.deprecated_devices:
							if deprecated_host.ip == host.ip and deprecated_host.mac_address == host.mac_address:
								self.deprecated_devices.remove(deprecated_host)
								break
						deprecated_host = Host(host.ip, host.last_discovery_time, host.last_mac_address, host.router)
						self.deprecated_devices.append(deprecated_host)
						host.last_mac_address = "Unknow"
						host.last_discovery_time = "Unknow"
				else:
					self.online_devices.remove(host)
					self.offline_devices.append(host)
			print(str(host)) #teste
		for host in self.offline_devices:
			host.poll()
			if (host.state == "Up"):
				self.offline_devices.remove(host)
				self.online_devices.append(host)
			print(str(host)) #teste

		##testes
		print("\n\n\n")

		for host in self.online_devices:
			print(str(host.ip))

		print("\n\n\n")

		for host in self.offline_devices:
			print(str(host.ip))

		print("\n\n\n")

		for host in self.deprecated_devices:
			print(str(host.ip))
		########


####################################################################################################################################

class Net_Checker():

	def __init__(self, poll_frequency):
		self.poll_frequency = poll_frequency
		self.check_activation = True
		self.net_data = Net_Discovery()
		self._check_routine()

	#Esse método deve ser disparado em uma thread
	def _check_routine(self):
		while self.check_activation:
			time.sleep(self.poll_frequency)
			self.net_data.check_devices()

####################################################################################################################################

teste = Net_Checker(20)