#!/usr/bin/env python

__author__ = "Saulius Bartkus"
__copyright__ = "Copyright 2017"

__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Saulius Bartkus"
__email__ = "saulius181@yahoo.com"
__status__ = "Production"

from tkinter import *
import random
import time
from threading import *
import avatar_map as map

EMPTY_COLOR = "white"
	
class game_controller(object):

	def new_game(self):
		if self.state["action"] == True:
			pass
		elif self.state["action"] == False:
			pass
		elif self.state["action"] == None:
			self.next_stage()		
			
	def quit(self):
		self.root.destroy()	
	
	def get_presence_list(self, type=[None]):
		list = {}
		
		for item in type:
			list[item] = []
		
		for key, value in self.map.items():
			if value["presence"] in type:
				list[value["presence"]].append(key)
		return list

	def get_neighbors(self, attacker):
		list = {}
		
		for key, value in self.map.items():
			if value["presence"] == attacker and value["troopCount"] > 1:
				for neighbor in value["neighbors"]:
					if self.map[neighbor]["presence"] != attacker:
						if not value["presence"] in list:
							list[ key ] = []
						list[ key ].append(neighbor)
		return list
		
	
	def next_stage(self):
		if not self.state["action"] and not self.state["turn"] and not self.state["stage"]:
			self.state["action"] = True
			self.state["turn"] = "Player"
			self.state["stage"] = "initial deployment"
			
			self.initdeployVar = self.deployVar.get()
			self.currentDeployVar = self.initdeployVar
			
			self.deployCurrentLabel.config(text="Remaining to deploy: {}".format(self.currentDeployVar))
			self.currentStageLabel.config(text="{} turn, {} stage".format(self.state["turn"], self.state["stage"]))
			
		elif self.state["action"] == True and self.state["turn"] == "Player":
			if self.state["stage"] == "initial deployment":
				self.state["action"] = False
				self.state["turn"] = "AI"
				self.state["stage"] = "initial deployment"		
				
				self.deployCurrentLabel.config(text="Remaining to deploy: {}".format(self.currentDeployVar))
				self.currentStageLabel.config(text="{} turn, {} stage".format(self.state["turn"], self.state["stage"]))				
				
				
				self.ai_deploy(self.initdeployVar)
			elif self.state["stage"] == "deployment":
				self.state["stage"] = "attack"				
				self.deployCurrentLabel.config(text="")
				self.currentStageLabel.config(text="{} turn, {} stage".format(self.state["turn"], self.state["stage"]))	
			elif self.state["stage"] == "post-attack":
				self.attacker_selected = None
				self.defender_selected = None			
				self.state["stage"] = "attack"				
				self.deployCurrentLabel.config(text="")
				self.currentStageLabel.config(text="{} turn, {} stage".format(self.state["turn"], self.state["stage"]))					
			elif self.state["stage"] == "attack":		
				self.state["stage"] = "maneuver"				
				self.deployCurrentLabel.config(text="")
				self.currentStageLabel.config(text="{} turn, {} stage".format(self.state["turn"], self.state["stage"]))	
				self.nextStageButton.config(text="End turn ->")
				
			elif self.state["stage"] == "maneuver":
				self.attacker_selected = None
				self.defender_selected = None	
				
				self.state["action"] = False
				self.state["turn"] = "AI"
				self.state["stage"] = "deployment"		
				
				self.deployCurrentLabel.config(text="Remaining to deploy: {}".format(self.currentDeployVar))
				self.currentStageLabel.config(text="{} turn, {} stage".format(self.state["turn"], self.state["stage"]))				
				
				self.ai_deploy(self.get_deploy_count("AI"))				
				
		elif self.state["action"] == False and self.state["turn"] == "AI":
			if self.state["stage"] == "initial deployment":

				self.currentDeployVar = self.get_deploy_count("Player")
				
				self.state["action"] = True
				self.state["turn"] = "Player"
				self.state["stage"] = "deployment"
				
				self.deployCurrentLabel.config(text="Remaining to deploy: {}".format(self.currentDeployVar))
				self.currentStageLabel.config(text="{} turn, {} stage".format(self.state["turn"], self.state["stage"]))		
			elif self.state["stage"] == "deployment":
				
				self.state["stage"] = "attack"
				
				self.ai_attack("AI")
				
				self.deployCurrentLabel.config(text="")
				self.currentStageLabel.config(text="{} turn, {} stage".format(self.state["turn"], self.state["stage"]))	
			elif self.state["stage"] == "attack":
				self.state["stage"] = "maneuver"
				
				self.ai_maneuver()
				
				self.deployCurrentLabel.config(text="")
				self.currentStageLabel.config(text="{} turn, {} stage".format(self.state["turn"], self.state["stage"]))	
				
			elif self.state["stage"] == "maneuver":
				self.attacker_selected = None
				self.defender_selected = None	
				
				self.state["action"] = True
				self.state["turn"] = "Player"
				self.state["stage"] = "deployment"		

				self.currentDeployVar = self.get_deploy_count("Player")
				
				self.deployCurrentLabel.config(text="Remaining to deploy: {}".format(self.currentDeployVar))
				self.currentStageLabel.config(text="{} turn, {} stage".format(self.state["turn"], self.state["stage"]))								

				self.nextStageButton.config(text="Next stage ->")
		
		self.redraw_board()
	
	def create_menu(self):
		self.divLine = self.canvas.create_line(800, 0, 800, 500, fill="black")

		self.deployVar = IntVar() 
		self.deployVar.set(5)
		
		self.startButton = Button(self.canvas, text = "New game", anchor = W, command = self.new_game)
		self.startButton.place(x=830,y=25)
		self.quitButton = Button(self.canvas, text = "Quit", anchor = W, command = self.quit)
		self.quitButton.place(x=900,y=25)	
		
		self.dice = { "attacker": {}, "defender": {} }
		
		for i in range(1):
			self.dice["attacker"][i] = {}
			self.dice["defender"][i] = {}
			
			self.dice["attacker"][i]["reference"] = self.canvas.create_rectangle(830, 250 + i*50 + i*10, 880, 300 + i*50 + i*10, fill="red")
			self.dice["attacker"][i]["dots"] = {}
			for j in range(3):
				for k in range(3):
					self.dice["attacker"][i]["dots"][3*j + k] = {}
					self.dice["attacker"][i]["dots"][3*j + k]["reference"] = self.canvas.create_oval(835 +k*10 +k*5, 255 + i*50 + i*10 +j*10 +j*5, 845 +k*10 +k*5, 265 + i*50 + i*10 +j*10 +j*5, fill="white")
				
			self.dice["defender"][i]["reference"] = self.canvas.create_rectangle(900, 250 + i*50 + i*10, 950, 300 + i*50 + i*10, fill="white")
			self.dice["defender"][i]["dots"] = {}
			for j in range(3):
				for k in range(3):
					self.dice["defender"][i]["dots"][3*j + k] = {}
					self.dice["defender"][i]["dots"][3*j + k]["reference"] = self.canvas.create_oval(905 +k*10 +k*5, 255 + i*50 + i*10 +j*10 +j*5, 915 +k*10 +k*5, 265 + i*50 + i*10 +j*10 +j*5, fill="black")
					
		self.deployInitLabel = Label(self.canvas, text="Init deploy count:")
		self.deployInitLabel.place(x=830,y=60)
		self.deployInitSlider = Scale(self.canvas, var=self.deployVar, from_=0, to=100, orient=HORIZONTAL)
		self.deployInitSlider.place(x=830,y=80)

		self.deployCurrentLabel = Label(self.canvas, text="")
		self.deployCurrentLabel.place(x=830,y=130)

		self.currentStageLabel = Label(self.canvas, text="")
		self.currentStageLabel.place(x=830,y=150)
		
		self.nextStageButton = Button(self.canvas, text = "Next stage ->", anchor = W, command = self.next_stage, state='disabled')
		self.nextStageButton.place(x=830,y=170)	
		
	def ai_deploy(self, count=0 ):
		deploy_list = self.get_presence_list([None, "AI"])

		self.deployCurrentLabel.config(text="Remaining to deploy: {}".format(count-1))

		if count:
			if deploy_list[None]:
				name = random.choice(deploy_list[None])
			else:
				name = random.choice(deploy_list["AI"])
			
			self.deploy(name, "AI", "#F00")		
			
			self.root.after(100, lambda count=count: self.ai_deploy(count-1))
		else:
			self.next_stage()

		self.redraw_board()	
	
	def ai_maneuver(self):
		self.root.after(100, self.next_stage)
		
	
	def ai_attack(self, attacker):
		attack_list = self.get_neighbors(attacker)
		if attack_list:
			self.attacker_selected = random.choice(list(attack_list.keys()))
			self.defender_selected = random.choice(attack_list[self.attacker_selected])
#			print(self.attacker_selected, self.defender_selected)

			for i in range(self.map[self.attacker_selected]["troopCount"] - 1):
				
				attacker_roll = random.randint(1, 6)
				defender_roll = random.randint(1, 6)
				
				if attacker_roll > defender_roll:
					self.map[self.defender_selected]["troopCount"] -= 1
					if self.map[self.defender_selected]["troopCount"] == 0:
						break
				else:
					self.map[self.attacker_selected]["troopCount"] -= 1
			
			if self.map[self.defender_selected]["troopCount"] == 0:
				self.map[self.defender_selected]["presence"] = "AI"				
				self.map[self.attacker_selected]["troopCount"] -= 1
				self.map[self.defender_selected]["troopCount"] += 1
				color = "#F00"
			else:
				color = "#00F"
				
			self.canvas.itemconfig(self.map[self.attacker_selected]["label"], text=self.map[self.attacker_selected]["troopCount"], fill="#F00")
			self.canvas.itemconfig(self.map[self.defender_selected]["label"], text=self.map[self.defender_selected]["troopCount"], fill=color)
			self.currentStageLabel.config(text="{} turn, {} stage".format(self.state["turn"], self.state["stage"]))	
			self.redraw_board()
			self.root.after(100, lambda attacker=attacker: self.ai_attack(attacker))
			
		else:
			self.next_stage()
	
	def deploy(self, name, type, color):
		self.map[name]["presence"] = type
		self.map[name]["troopCount"] += 1
		self.canvas.itemconfig(self.map[name]["label"], text=self.map[name]["troopCount"], fill=color)
		self.currentDeployVar -= 1	
		self.redraw_board()
					
	def get_deploy_count(self, type):
		count = 3
		for key, value in self.map.items():
			if value["presence"] == type:
				count+=1
		return count		
	
	def on_enter(self, name):
		if self.state["action"]:
			self.canvas.itemconfig(CURRENT, fill="#AAF")

				
	def on_click(self, name):
		if self.state["action"]:
			if self.state["turn"] == "Player":
				if self.state["stage"] == "initial deployment":
					if self.map[name]["presence"] in [None, "Player"] and self.currentDeployVar > 0:
					
						self.deploy(name, "Player", "#00F")
						self.deployCurrentLabel.config(text="Remaining to deploy: {}".format(self.currentDeployVar))
							
				elif self.state["stage"] == "deployment":
					if self.map[name]["presence"] in [None, "Player"] and self.currentDeployVar > 0:
					
						self.deploy(name, "Player", "#00F")
						self.deployCurrentLabel.config(text="Remaining to deploy: {}".format(self.currentDeployVar))
						
				elif self.state["stage"] == "post-attack":
					if name == self.attacker_selected:
						if self.map[self.defender_selected]["troopCount"] > 1:
							self.map[self.attacker_selected]["troopCount"] += 1
							self.map[self.defender_selected]["troopCount"] -= 1
					elif name == self.defender_selected:
						if self.map[self.attacker_selected]["troopCount"] > 1:
							self.map[self.defender_selected]["troopCount"] += 1
							self.map[self.attacker_selected]["troopCount"] -= 1	
							
					self.canvas.itemconfig(self.map[self.attacker_selected]["label"], text=self.map[self.attacker_selected]["troopCount"], fill="#00F")
					self.canvas.itemconfig(self.map[self.defender_selected]["label"], text=self.map[self.defender_selected]["troopCount"], fill="#00F")							
						
				elif self.state["stage"] == "attack":
					if self.attacker_selected:
						if self.map[self.attacker_selected]["troopCount"] >= 2 and name in self.map[self.attacker_selected]["neighbors"] and self.map[name]["presence"] in [None, "AI"]:
							
							self.defender_selected = name
							
							if self.map[self.defender_selected]["troopCount"] != 0:
								for i in range(self.map[self.attacker_selected]["troopCount"] - 1):
									
									attacker_roll = random.randint(1, 6)
									defender_roll = random.randint(1, 6)
									
									if attacker_roll > defender_roll:
										self.map[self.defender_selected]["troopCount"] -= 1
										if self.map[self.defender_selected]["troopCount"] == 0:
											break
									else:
										self.map[self.attacker_selected]["troopCount"] -= 1
							
							if self.map[self.defender_selected]["troopCount"] == 0:
								self.state["stage"] = "post-attack"
								self.map[self.defender_selected]["presence"] = "Player"				
								self.map[self.attacker_selected]["troopCount"] -= 1
								self.map[self.defender_selected]["troopCount"] += 1

								self.canvas.itemconfig(self.map[self.attacker_selected]["label"], text=self.map[self.attacker_selected]["troopCount"], fill="#00F")
								self.canvas.itemconfig(self.map[self.defender_selected]["label"], text=self.map[self.defender_selected]["troopCount"], fill="#00F")
								self.currentStageLabel.config(text="{} turn, {} stage".format(self.state["turn"], self.state["stage"]))									
								
							else:
								
								self.canvas.itemconfig(self.map[self.attacker_selected]["label"], text=self.map[self.attacker_selected]["troopCount"], fill="#00F")
								self.canvas.itemconfig(self.map[self.defender_selected]["label"], text=self.map[self.defender_selected]["troopCount"], fill="#F00")
								self.currentStageLabel.config(text="{} turn, {} stage".format(self.state["turn"], self.state["stage"]))
								
								self.attacker_selected = None
								self.defender_selected = None								

							self.redraw_board()
						else:		
							self.attacker_selected = None
					else:
						if self.map[name]["presence"] == "Player":
							self.attacker_selected = name
					self.redraw_board()
				elif self.state["stage"] == "maneuver":
					if self.attacker_selected:
						if not self.defender_selected:
							if name in self.map[self.attacker_selected]["neighbors"] and self.map[name]["presence"] == "Player":
								self.defender_selected = name
							
						if self.defender_selected:
							if name == self.attacker_selected and self.map[self.defender_selected]["troopCount"] >= 2:
								self.map[self.attacker_selected]["troopCount"] += 1
								self.map[self.defender_selected]["troopCount"] -= 1
					
							elif name == self.defender_selected and self.map[self.attacker_selected]["troopCount"] >= 2:
								self.map[self.attacker_selected]["troopCount"] -= 1
								self.map[self.defender_selected]["troopCount"] += 1
								
							self.canvas.itemconfig(self.map[self.attacker_selected]["label"], text=self.map[self.attacker_selected]["troopCount"], fill="#00F")
							self.canvas.itemconfig(self.map[self.defender_selected]["label"], text=self.map[self.defender_selected]["troopCount"], fill="#00F")
							self.redraw_board()
						else:		
							self.attacker_selected = None
					else:
						if self.map[name]["presence"] == "Player":
							self.attacker_selected = name
					self.redraw_board()					
					
					
	def on_release(self, Event=None):
		pass
		
	def redraw_board(self):
		if self.state["action"]:
			self.nextStageButton.config(state="normal")
		else:
			self.nextStageButton.config(state="disabled")
		
		for key, value in self.map.items():
			if key == self.attacker_selected:
				if self.state["turn"] == "Player":
					self.canvas.itemconfig(value["reference"], fill="#44F")
				elif self.state["turn"] == "AI":
					self.canvas.itemconfig(value["reference"], fill="#F88")
			elif key == self.defender_selected:
				if self.state["turn"] == "Player":
					self.canvas.itemconfig(value["reference"], fill="#55F")	
				elif self.state["turn"] == "AI":
					self.canvas.itemconfig(value["reference"], fill="#FAA")	
			elif self.attacker_selected and key in self.map[self.attacker_selected]["neighbors"] and not self.defender_selected:
				self.canvas.itemconfig(value["reference"], fill="#CCF")	
			elif value["presence"] == "Player":
				self.canvas.itemconfig(value["reference"], fill="#66F")	
			elif value["presence"] == "AI":
				self.canvas.itemconfig(value["reference"], fill="#F66")	
			else:
				self.canvas.itemconfig(value["reference"], fill="#AAA")					
			
	def on_leave(self, Event=None):
		if self.state["action"]:
			self.redraw_board()
		
	def __init__(self, root):
		self.root = root
		self.canvas = Canvas(root, width=1200, height=500)
		
		self.canvas.pack()	
		self.mapList = map.mapCoords()
		self.map = {}
		
		self.attacker_selected = None
		
		self.defender_selected = None
		
		for item in self.mapList:
			
			self.map[item[0]] = { "reference" :  self.canvas.create_polygon( item[1], fill=item[2], outline="black", width=2 )}
			
#			self.canvas.move(self.map[item[0]]["reference"], -150, -120)

			self.canvas.scale(self.map[item[0]]["reference"], 1, 1, 0.05, 0.05)
#			self.canvas.scale(self.map[item[0]]["reference"], 1, 1, 0.2, 0.2)

			x_center = sum( self.canvas.coords(self.map[item[0]]["reference"])[0::2] ) / float(len( self.canvas.coords(self.map[item[0]]["reference"])[0::2] ))
			y_center = sum( self.canvas.coords(self.map[item[0]]["reference"])[1::2] ) / float(len( self.canvas.coords(self.map[item[0]]["reference"])[1::2] ))
			
			self.map[item[0]]["presence"] = None
			self.map[item[0]]["troopCount"] = 0
			
#			self.canvas.create_text(x_center, y_center, text=item[0], font=("Lucida Console", 10), fill="black")
			
			self.map[item[0]]["label"] = self.canvas.create_text(x_center, y_center, text="", font=("Lucida Console", 20), fill="black")
			self.map[item[0]]["neighbors"] = item[3]
			
			self.canvas.tag_bind(self.map[item[0]]["reference"], "<Enter>", lambda event, arg=item[0]: self.on_enter(arg))
			self.canvas.tag_bind(self.map[item[0]]["reference"], "<Leave>", self.on_leave)	
			self.canvas.tag_bind(self.map[item[0]]["reference"], "<Button-1>", lambda event, arg=item[0]: self.on_click( arg ))
			self.canvas.tag_bind(self.map[item[0]]["reference"], "<ButtonRelease-1>", self.on_release)				
			
		self.create_menu()
		self.state = {"action": None, "stage": None, "turn": None}
				
if __name__ == "__main__":
	root = Tk()
	root.title("Battleships Tk")
	root.resizable(0,0)
	game = game_controller(root);
	root.mainloop()
