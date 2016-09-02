from tkinter import *
from MultiListbox import *

from subprocess import *
from multiprocessing import Process, Manager

class GUI(Frame):
	def __init__(self, netD, master=None):

		self.netD = netD

		self.alive = True

		self.color = "#111"
		self.color2 = "#1a1a1a"

		master.title("Trabalho 1 - Gerencia de redes")
		master.resizable(width=True, height=False)

		rrt = Frame.__init__(self, master, background=self.color)

		self.cab = Frame(self, rrt, bg="black")
		self.msg = Label(self.cab, text="Descoberta da Rede", background="black", fg="#2a3", font=('Verdana', '14', ''), pady="15").pack(fill='both')


		self.cab_online = Frame(self, rrt, bg=self.color)
		Label(self.cab_online, text="---------------------- HOSTS ONLINE ----------------------", fg="white", bg=self.color, pady="5").pack()
		self.frame_online = Frame(self, rrt, bg=self.color2)
		self.listbox = MultiListbox(self.frame_online, height=110, width=800, background=self.color2, bd=0, highlightthickness=0, font=('Trebuchet MS', '12', ''), fg='#aaa')
		self.listbox.config(columns=('Ip address','MAC address', 'Last Poll', 'Vendor', 'Latency'), selectbackground='black')

		self.cab_offline = Frame(self, rrt, bg=self.color)
		self.frame_offline = Frame(self, rrt, bg=self.color2)
		Label(self.cab_offline, text="---------------------- HOSTS OFFLINE ----------------------", fg="white", bg=self.color, pady="5").pack()
		self.listboxoff = MultiListbox(self.frame_offline, height=110, width=800, background=self.color2, bd=0, highlightthickness=0, font=('Trebuchet MS', '12', ''), fg='#aaa')
		self.listboxoff.config(columns=('Ip address','MAC address', 'Last Poll', 'Vendor', 'Latency'), selectbackground='black')

		self.cab_deprecated = Frame(self, rrt, bg=self.color)
		self.frame_deprecated = Frame(self, rrt, bg=self.color2, height=10)
		Label(self.cab_deprecated, text="---------------------- DEPRECATED ----------------------", fg="white", bg=self.color, pady="5").pack()
		self.listboxdep = MultiListbox(self.frame_deprecated, height=110, width=800, background=self.color2, bd=0, highlightthickness=0, font=('Trebuchet MS', '12', ''), fg='#aaa')
		self.listboxdep.config(columns=('Ip address','MAC address', 'Last Poll', 'Discovery time'), selectbackground='black')
		
		self.cab.pack(fill='both')
		self.cab_online.pack(fill='both')
		self.frame_online.pack(fill='both', expand=True)
		self.listbox.pack(side='left')

		self.yscroll = Scrollbar(self.frame_online, command=self.listbox.yview, orient=VERTICAL)
		self.yscroll.pack(side='right')
		self.listbox.configure(yscrollcommand=self.yscroll.set)

		Frame(self, rrt, bg="black", height=20).pack(fill='both')

		self.cab_offline.pack(fill='both')
		self.frame_offline.pack(fill='both', expand=True)
		self.listboxoff.pack(side='left')

		self.yscrolloff = Scrollbar(self.frame_offline, command=self.listboxoff.yview, orient=VERTICAL)
		self.yscrolloff.pack(side='right')
		self.listboxoff.configure(yscrollcommand=self.yscrolloff.set)

		Frame(self, rrt, bg="black", height=20).pack(fill='both')

		self.cab_deprecated.pack(fill='both')
		self.frame_deprecated.pack(fill='both', expand=True)
		self.listboxdep.pack(side='left')

		self.yscrolldep = Scrollbar(self.frame_deprecated, command=self.listboxdep.yview, orient=VERTICAL)
		self.yscrolldep.pack(side='right')
		self.listboxdep.configure(yscrollcommand=self.yscrolldep.set)

		self.rodape = Frame(self, rrt, bg="black", pady=10)#.pack(fill='both')
		self.textfield = Entry(self.rodape, width=21, font=('15'), borderwidth=0)
		self.textfield.grid(row=1, column=2)
		Label(self.rodape, text="Entre com o IP para forçar o poll...", bg='black', fg='white').grid(row=1,column=1)
		self.button = Button(self.rodape, text="Poll!", width=18, borderwidth=0, command=self.poll).grid(row=2, column=2, pady=5)
		self.return_poll = Label(self.rodape, text="Erro ao fazer o poll...", bg='black', fg='red')
		self.return_poll2 = Label(self.rodape, text="", bg='black', fg='red')
		self.return_poll.grid(row=1, column=3, padx=10)
		self.return_poll2.grid(row=1, column=4)
		self.return_poll.config(text="")

		self.rodape.pack(fill='both')
		self.pack(fill='both')

		self.tables = (self.listbox, self.listboxoff, self.listboxdep)
		
		

	def poll(self):
		#str(self.textfield.get())
		ip = str(self.textfield.get())
		self.return_poll.config(text="Submetendo poll ao ip '" + ip + "' .... ", fg='white')
		
		ups, downs, deps = self.netD.particular_poll(ip)
		if ups or downs or deps:
			self.update_tables(ups, downs, deps)
			self.return_poll2.config(text="Feito!!", fg='green')
		else:
			self.return_poll2.config(text="Erro!!", fg='red')

		#self.return_poll.config(text=self.textfield.get())



	def update_tables(self, ups, downs, deps):
		self.destroy_tables()

		for key in ups.keys():
			self.listbox.insert(END, str(key), str(ups[key][0]), str(ups[key][1]), str(ups[key][2]), str(ups[key][3]))

		for key in downs.keys():
			self.listboxoff.insert(END, str(key), str(downs[key][0]), str(downs[key][1]), str(downs[key][2]), str(downs[key][3]))

		for key in deps.keys():
			self.listboxdep.insert(END, str(key), str(deps[key][0]), str(deps[key][1]), str(deps[key][2]), str(deps[key][3]))

		#self.update()

	def upd(self):
		while True:
			self.update()

	def destroy_tables(self):
		for table in self.tables:
			table.delete(0,END)

	def quit(self):
		self.root.destroy()
		exit(0)
		#self.alive = False

	def is_alive(self):
		return self.alive