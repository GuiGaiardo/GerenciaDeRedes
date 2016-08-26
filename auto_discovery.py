from subprocess import *
import requests
import datetime

"""To do:
"""
class Host():

	def __init__(self, address):
		self.ip = address
		self.discovery_time = datetime.datetime.now()
		self.mac_address = "Unknown"
		self.poll()


	def _update_state(self, state):
		self.state = state

	def _get_mac_address(self):
		cmd = "arp -n " + self.ip
		process = Popen(cmd, shell=True, stdout=PIPE)
		saida, erro = process.communicate()
		print(saida)
		mac_address = saida.split()[8].decode()
		if self.mac_address == "Unknown":
			self.mac_address = mac_address
		elif self.mac_address == mac_address:
			return
		else:
			pass #FAZER A LOGICA DO MUDOU O DISPOSITIVO COM ESSE IP


	def poll(self):
		ping = Popen("ping -c 1 "+self.ip, shell=True, stdout=PIPE)
		saida, erro = ping.communicate()
		print(saida)
		latency = saida.split()[13].decode()
		if "time" in latency:
			self._get_mac_address()
			self.latency = float(latency[5:])
			self._update_state("Up")
		elif latency == '---':
			self._update_state("Down")
		else:
			self._update_state("Unknown")

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


	def __str__(self):
		return self.ip + " " + self.state + " " + self._get_elapsed_time()