import Tkinter
from Tkinter import *
from random import *
import random
import math

root = Tk()

def hello():
    pass

class Simulation:
	def __init__(self):
		self.Particle_List = []
		self.Iteration_Rate = 1.0
		self.Current_Instance = 0.0
		self.Active_Particles = 0
		self.Particle_Iter = 0
		self.Paused = True
		self.Gravitational_Constant = 0.00125
		
	def Clear_Particle_List(self):
		self.Particle_List = []
		self.Current_Instance = 0.0
		self.Paused = True
		Universe.space.delete(ALL)
		Universe.status_bar.update()
		
	def Get_Force_Distance(self):	#Check my map
		for p in self.Particle_List:
			Other_List = p.Get_Other_Particles()
			p.xforce = p.yforce = 0
			p.distance_list = []
			for o in Other_List:
				p.Find_Force(o)

	def Fuse(self, Parent_1, Parent_2, Child):
		self.Particle_List.remove(Parent_1)
		self.Particle_List.remove(Parent_2)
		self.Particle_List.append(Child)

	def Create_Satellite(self, centerParticle, DistanceMassTupleList):
		New_List = DistanceMassTupleList
		center = centerParticle
		for Tuple in New_List:
			Distance = Tuple[0]
			Mass = Tuple[1]
			New_X = center.x + Distance
			New_Y = center.y
			Satellite = Particle(New_X, New_Y, 0, 0, Mass)
			Other_List = Satellite.Get_Other_Particles()
			for o in Other_List:
				Satellite.Find_Force(o)
			Satellite.yvel = Satellite.xvel * (-1)
			Satellite.xvel = 0

	def One_Step(self):
		self.Current_Instance += self.Iteration_Rate
		self.Get_Force_Distance()
		for p in self.Particle_List:
			Universe.status_bar.update()
			p.Get_Instance()
			p.Update_Position()
			p.Detect_Collision(p)
			p.Get_Instance()

sim = Simulation()

class Particle:
	def __init__(self, x, y, xvel, yvel, mass): #No return
		self.x = x
		self.y = y
		self.xvel = xvel
		self.yvel = yvel
		self.xaccel = 0
		self.yaccel = 0
		self.xforce = 0
		self.yforce = 0
		self.mass = float(mass)
		self.radius = math.sqrt(self.mass)
		self.instance = 0
		self.name = 0
		self.genname()
		self.distance_list = []
		#bbox Coordinates for drawing particles around center point
		self.x0 = self.x - self.radius
		self.y0 = self.y - self.radius
		self.x1 = self.x + self.radius
		self.y1 = self.y + self.radius

	def genname(self): # Check me
		sim.Particle_Iter += 1
		self.name = sim.Particle_Iter
		
	def update_bbox_coords(self):
		self.x0 = (self.x - self.radius)
		self.y0 = (self.y - self.radius)
		self.x1 = (self.x + self.radius)
		self.y1 = (self.y + self.radius)

	def Get_Other_Particles(self):
		O_List = []
		for p in sim.Particle_List:
			if self.name != p.name:
				O_List.append(p)
			else:
				continue
		return O_List

	def Find_Force(self, Other_Particle): #No return, Updates particle
		xdiff = float(self.x - Other_Particle.x)
		ydiff = float(self.y - Other_Particle.y)
		Distance = abs(math.sqrt((xdiff**2)+(ydiff**2)))
		if Distance < ((self.radius * 2) + (Other_Particle.radius * 2)):
			self.distance_list.append((Other_Particle,Distance))
		Force = (sim.Gravitational_Constant * self.mass * Other_Particle.mass) / Distance**2
		Acceleration = Force / self.mass
		self.xaccel = (xdiff/float(Distance) * Acceleration)
		self.xvel -= self.xaccel * sim.Iteration_Rate
		self.yaccel = (ydiff/float(Distance) * Acceleration)
		self.yvel -= self.yaccel * sim.Iteration_Rate

	def Inelastic_Collision(self, mate):	#FIX ME
		New_Mass = self.mass + mate.mass
		XDiff = self.x - mate.x
		YDiff = self.y - mate.y
		Distance = abs(math.sqrt((XDiff**2)+(YDiff**2)))
		if self.mass >= mate.mass:
			pass
		else:
			XDiff = XDiff * (-1)
			YDiff = YDiff * (-1)
		New_X = mate.x + (XDiff/Distance * self.radius)
		New_Y = mate.y + (YDiff/Distance * self.radius)
		New_Xvel = ((self.mass * self.xvel) + (mate.mass * mate.xvel)) / (self.mass + mate.mass)
		New_Yvel = ((self.mass * self.yvel) + (mate.mass * mate.yvel)) / (self.mass + mate.mass)
		z = Particle(New_X, New_Y, New_Xvel, New_Yvel, New_Mass)
		return z

	def Detect_Collision(self,p):
		for i in self.distance_list:
			Universe.status_bar.update()
			P = i[0]
			D = i[1]
			if D <= (self.radius + P.radius):
				z = self.Inelastic_Collision(P)
				try:
					sim.Fuse(p, P, z)
				except ValueError:
					continue
				z.Get_Instance()
				z.Detect_Collision(z)

	def Update_Position(self):
		self.x += self.xvel * sim.Iteration_Rate
		self.y += self.yvel * sim.Iteration_Rate

	def Get_Instance(self):
		self.instance = sim.Current_Instance

class Status_Bar:
	def __init__(self, master,iteration,num):
		self.label = Label(master, text="Iteration: %f" %(iteration), bd=1, relief=SUNKEN, anchor=SE)
		self.label2 = Label(master, text="Active Particles: %d" %(num), bd=1,relief=SUNKEN, anchor=SE)
		self.label.pack(side=RIGHT,padx=5)
		self.label2.pack(side=LEFT,padx=5)

	def update(self):
		iteration = sim.Current_Instance
		self.label.config(text='Iteration: %f' %(round(iteration,2)))
		sim.Active_Particles = len(sim.Particle_List)
		self.label2.config(text='Active Particles: %d' %(sim.Active_Particles))
		self.label.update_idletasks()
		self.label2.update_idletasks()

class Main_Window:
	def __init__(self, root):
		root.wm_title("Gravity Simulator")
		menubar = Menu(root)
		
		playmenu = Menu(menubar, tearoff=0)
		playmenu.add_command(label="Run", command=Run)
		playmenu.add_command(label="Pause", command=Pause)
		menubar.add_cascade(label="Playback", menu=playmenu)

		particlemenu = Menu(menubar, tearoff=0)
		particlemenu.add_command(label="Add Particle", command=self.Make_Particle_PopUp)
		particlemenu.add_command(label="Generate Particles", command=self.Generate_Random_Particles_PopUp)
		particlemenu.add_command(label="Set Iteration Rate", command=self.Set_Iteration_Rate_PopUp)
		particlemenu.add_command(label="Clear Particles", command=sim.Clear_Particle_List)
		menubar.add_cascade(label="Simulation Management", menu=particlemenu)

		helpmenu = Menu(menubar, tearoff=0)
		helpmenu.add_command(label="How this program works (Does Nothing)", command=self.How_Program_Works_PopUp)
		helpmenu.add_command(label="How to use this program (Does Nothing)", command=self.How_To_Use_Program_PopUp)
		menubar.add_cascade(label="Help", menu=helpmenu)
		
		menubar.add_command(label="About (Does Nothing)", command=self.About_PopUp)
		
		# display the menu
		root.config(menu=menubar)
		self.space = Canvas(root, width=500, height=500, bg="black")
		self.space.pack(fill=BOTH, expand=YES)
		self.status_bar = Status_Bar(root,0,0)

	def How_Program_Works_PopUp(self):
		Type = "How_Program_Works"
		Pop_Up = Toplevel()
		Dialog = PopUp_Window(Pop_Up, Type)
		Pop_Up.mainloop()
		
	def How_To_Use_Program_PopUp(self):
		Type = "How_To_Use_Program"
		Pop_Up = Toplevel()
		Dialog = PopUp_Window(Pop_Up, Type)
		Pop_Up.mainloop()

	def About_PopUp(self):
		Type = "About"
		Pop_Up = Toplevel()
		Dialog = PopUp_Window(Pop_Up, Type)
		Pop_Up.mainloop()
		
	def Make_Particle_PopUp(self):
		Type = "Make_Particle"
		Pop_Up = Toplevel()
		Dialog = PopUp_Window(Pop_Up, Type)
		Pop_Up.mainloop()
		
	def Generate_Random_Particles_PopUp(self):
		Type = "Generate_Random_Particles"
		Pop_Up = Toplevel()
		Dialog = PopUp_Window(Pop_Up, Type)
		Pop_Up.mainloop()
	
	def Set_Iteration_Rate_PopUp(self):
		Type = "Set_Iteration_Rate"
		Pop_Up = Toplevel()
		Dialog = PopUp_Window(Pop_Up, Type)
		Pop_Up.mainloop()

class PopUp_Window:	

	def __init__(self, master, PopUp_Type):
		self.PopUp_Type = PopUp_Type
		self.master = master
		self.g = []
		self.z = []
		self.b = ""
		
		if PopUp_Type is "Set_Iteration_Rate":
			self.z = ["Iteration Rate: "]
			self.IR = DoubleVar()
			self.g = [self.IR]
			self.b = "Set!"
			for i in self.z:
				Pos_in_List = self.z.index(i)
				Label(master, text=self.z[Pos_in_List]).grid(row=Pos_in_List, sticky=W)
				Entry(master, textvariable=self.g[Pos_in_List]).grid(row=Pos_in_List, column=1)
				
			Make_Button = Tkinter.Button(self.master, text=self.b, command=self.getAttributes).grid(row=7)
	
		elif PopUp_Type is "Make_Particle":
			self.z = ["X - Coordinate: ",
			     "Y - Coordinate: ",
			     "X - Velocity: ",
			     "Y - Velocity: ",
			     "Mass: "]

			self.x = DoubleVar()
			self.y = DoubleVar()
			self.xvel = DoubleVar()
			self.yvel = DoubleVar()
			self.mass = DoubleVar()
			
			self.g = [self.x, self.y, self.xvel, self.yvel, self.mass]
			self.b = "Make!"
			for i in self.z:
				Pos_in_List = self.z.index(i)
				Label(master, text=self.z[Pos_in_List]).grid(row=Pos_in_List, sticky=W)
				Entry(master, textvariable=self.g[Pos_in_List]).grid(row=Pos_in_List, column=1)
				
			Make_Button = Tkinter.Button(self.master, text=self.b, command=self.getAttributes).grid(row=7)
		
		elif PopUp_Type is "Generate_Random_Particles":
			self.z = ["# of Particles: ",
			 "Lowest Mass: ",
			  "Highest Mass: ",
			  "Lowest Initial X",
			   "Highest Initial X: ",
			    "Lowest Initial Y",
			     "Highest Initial Y", "Min Xvel","Max Xvel","Min Yvel","Max Yvel"]
			self.n = IntVar()
			self.MinMass = DoubleVar()
			self.MaxMass = DoubleVar()
			self.MinX = DoubleVar()
			self.MaxX = DoubleVar()
			self.MinY = DoubleVar()
			self.MaxY = DoubleVar()
			self.MinXvel = DoubleVar()
			self.MaxXvel = DoubleVar()
			self.MinYvel = DoubleVar()
			self.MaxYvel = DoubleVar()
			
			self.g = [self.n, self.MinMass, self.MaxMass, self.MinX, self.MaxX, self.MinY, self.MaxY, self.MinXvel, self.MaxXvel, self.MinYvel, self.MaxYvel]
			self.b = "Make!"
			for i in self.z:
				Pos_in_List = self.z.index(i)
				Label(master, text=self.z[Pos_in_List]).grid(row=Pos_in_List, sticky=W)
				Entry(master, textvariable=self.g[Pos_in_List]).grid(row=Pos_in_List, column=1)
			Make_Button = Tkinter.Button(self.master, text=self.b, command=self.getAttributes).grid(row=11)
			
		elif PopUp_Type is "How_Program_Works":
			pass
		
		elif PopUp_Type is "How_To_Use_Program":
			pass

		elif PopUp_Type is "Data_Viewer":
			pass

		elif PopUp_Type is "About":
			pass
		
	def getAttributes(self):
		if self.PopUp_Type is "Set_Iteration_Rate":
			sim.Iteration_Rate = self.IR.get()
			self.master.destroy()
	
		elif self.PopUp_Type is "Make_Particle":
			x = self.x.get()
			y = self.y.get()
			xvel = self.xvel.get()
			yvel = self.yvel.get()
			mass = self.mass.get()
			newParticle = Particle(x,y,xvel,yvel,mass)
			sim.Particle_List.append(newParticle)
			Universe.space.create_oval(newParticle.x0, newParticle.y0,newParticle.x1,newParticle.y1, fill="white")
			Universe.status_bar.update()
			Universe.space.update()
			self.master.destroy()
		
		elif self.PopUp_Type is "Generate_Random_Particles":
			n = self.n.get()
			MinMass = self.MinMass.get()
			MaxMass = self.MaxMass.get()
			MinX = self.MinX.get()
			MaxX = self.MaxX.get()
			MinY = self.MinY.get()
			MaxY = self.MaxY.get()
			MinXvel = self.MinXvel.get()
			MaxXvel = self.MaxXvel.get()
			MinYvel = self.MinYvel.get()
			MaxYvel = self.MaxYvel.get()
			self.master.destroy()
			for i in range(n):
				p = Particle(uniform(MinX, MaxX), (uniform(MinY, MaxY)), randint(-1,1)*(uniform(MinXvel,MaxXvel)),randint(-1,1)*(uniform(MinYvel,MaxYvel)),uniform(MinMass,MaxMass))
				sim.Particle_List.append(p)
				Universe.space.create_oval(p.x0, p.y0, p.x1, p.y1, fill="white")
				Universe.space.update()
				Universe.status_bar.update()
			for p in sim.Particle_List:
				Universe.status_bar.update()
				Other_List = p.Get_Other_Particles()
				for o in Other_List:
					xdiff = float(p.x - o.x)
					ydiff = float(p.y - o.y)
					Distance = abs(math.sqrt((xdiff**2)+(ydiff**2)))
					if Distance < ((p.radius * 2) + (o.radius * 2)):
						p.distance_list.append((o,Distance))
					else:
						continue
				p.Detect_Collision(p)

def Run():
	sim.Paused = False
	while sim.Paused is False:
		sim.One_Step()
		Universe.status_bar.update()
		Universe.space.delete(ALL)
		for i in sim.Particle_List:
			i.update_bbox_coords()
			Universe.space.create_oval(i.x0, i.y0, i.x1, i.y1, fill="white") #change color to i.color #setl in make_particle function
		Universe.space.update()

def Pause():
	sim.Paused = True

Universe = Main_Window(root)
mainloop()
