from tkinter import *
from MultiListbox import *

class GUI(Frame):
	def __init__(self, master=None):

		self.alive = True

		self.color = "#111"
		self.color2 = "#1a1a1a"

		Frame.__init__(self, master, background=self.color)
		
		self.cab = Frame(self, master, bg="black")
		self.msg = Label(self.cab, text="t1 - gerencia de redes", background="black", fg="#2a3", font=('Verdana', '14', ''), pady="15").pack(fill='both')


		self.cab_online = Frame(self, master, bg=self.color)
		Label(self.cab_online, text="---------------------- HOSTS ONLINE ----------------------", fg="white", bg=self.color, pady="5").pack()
		self.frame_online = Frame(self, master, bg=self.color2)
		self.listbox = MultiListbox(self.frame_online, height=150, width=800, background=self.color2, bd=0, highlightthickness=0, font=('Trebuchet MS', '12', ''), fg='#aaa')
		self.listbox.config(columns=('Ip address','MAC address', 'Last Poll', 'Vendor', 'Latency'), selectbackground='black')

		self.cab_offline = Frame(self, master, bg=self.color)
		self.frame_offline = Frame(self, master, bg=self.color2)
		Label(self.cab_offline, text="---------------------- HOSTS OFFLINE ----------------------", fg="white", bg=self.color, pady="5").pack()
		self.listboxoff = MultiListbox(self.frame_offline, height=150, width=800, background=self.color2, bd=0, highlightthickness=0, font=('Trebuchet MS', '12', ''), fg='#aaa')
		self.listboxoff.config(columns=('Ip address','MAC address', 'Last Poll', 'Vendor', 'Latency'), selectbackground='black')

		self.cab_deprecated = Frame(self, master, bg=self.color)
		self.frame_deprecated = Frame(self, master, bg=self.color2, height=10)
		Label(self.cab_deprecated, text="---------------------- DEPRECATED ----------------------", fg="white", bg=self.color, pady="5").pack()
		self.listboxdep = MultiListbox(self.frame_deprecated, height=150, width=800, background=self.color2, bd=0, highlightthickness=0, font=('Trebuchet MS', '12', ''), fg='#aaa')
		self.listboxdep.config(columns=('Ip address','MAC address', 'Last Poll', 'Discovery time'), selectbackground='black')
		
		self.cab.pack(fill='both')
		self.cab_online.pack(fill='both')
		self.frame_online.pack(fill='both', expand=True)
		self.listbox.pack(side='left')

		self.yscroll = Scrollbar(self.frame_online, command=self.listbox.yview, orient=VERTICAL)
		self.yscroll.pack(side='right')
		self.listbox.configure(yscrollcommand=self.yscroll.set)

		Frame(self, master, bg="black", height=20).pack(fill='both')

		self.cab_offline.pack(fill='both')
		self.frame_offline.pack(fill='both', expand=True)
		self.listboxoff.pack(side='left')

		self.yscrolloff = Scrollbar(self.frame_offline, command=self.listboxoff.yview, orient=VERTICAL)
		self.yscrolloff.pack(side='right')
		self.listboxoff.configure(yscrollcommand=self.yscrolloff.set)

		Frame(self, master, bg="black", height=20).pack(fill='both')

		self.cab_deprecated.pack(fill='both')
		self.frame_deprecated.pack(fill='both', expand=True)
		self.listboxdep.pack(side='left')

		self.yscrolldep = Scrollbar(self.frame_deprecated, command=self.listboxdep.yview, orient=VERTICAL)
		self.yscrolldep.pack(side='right')
		self.listboxdep.configure(yscrollcommand=self.yscrolldep.set)

		Frame(self, master, bg="black", height=20).pack(fill='both')


		self.pack(fill='both')


		self.tables = (self.listbox, self.listboxoff, self.listboxdep)
		
	
	def update_tables(self, ups, downs, deps):
		self.destroy_tables()

		for key in ups.keys():
			self.listbox.insert(END, str(key), str(ups[key][0]), str(ups[key][1]), str(ups[key][2]), str(ups[key][3]))

		for key in downs.keys():
			self.listboxoff.insert(END, str(key), str(downs[key][0]), str(downs[key][1]), str(downs[key][2]), str(downs[key][3]))

		for key in deps.keys():
			self.listboxdep.insert(END, str(key), str(deps[key][0]), str(deps[key][1]), str(deps[key][2]), str(deps[key][3]))

		self.update()

	def destroy_tables(self):
		for table in self.tables:
			table.delete(0,END)

	def quit(self):
		self.root.destroy()
		#self.alive = False

	def is_alive(self):
		return self.alive