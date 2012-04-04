import Tkinter
from Tkinter import *
from random import *
import random
import math
import matplotlib
from matplotlib.figure import Figure
from matplotlib.pyplot import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import tkFileDialog
import sqlite3
import csv
import numpy

"""
This project is a merger of both my final project for this class and the final project for my introduction to programming(which is due on December 8th).  Along with Vincent Medina, my midterm project for that class was a gravity simulator.  For its final project, we have improved the simulator a great deal.  

Being that it created large sets of information with potential for analysis, for my Everyday Computer Science final project, I added to the program an "Export CSV" function.  This takes the "particle and pollision Histories"(lists that are appended information every iteration), and creates a csv for each.  I then made a function for making and loading a database from a csv.  This created two tables in the database file and fill them with entries for each line in each csv.  With the database of a given simulation's data, I made a viewer for both the entire simulation's data and the data for each particle in it.

The process to utilize the simulation viewer:
    1. Under the "Simulation Management" menu, select Generate Particles which will open a dialog.
    2. Input variables into each entry, then hit make.(the top-left corner of the screen is (0,0).  The bottom-right corner of the window before it is maximized is (500,500).)
    3. When ready, under the "Playback" menu, select Run.
          - If the simulation is running too slowly:
               + Increase the iteration rate under the "Simulation Management" menu. It's default value is 1.0
               + Reduce the number of particles
               - If each iteration is running too slowly:
                    + Reduce the distance between particles
                    + Increase the mass of each particle
    4. When ready, pause the simulation and export it to CSV by going to the "CSV Management" menu and selecting "Export to CSV".
    5. When complete(currently only indicated by processor usage), make a Database by going to the "Database Management" menu and selecting "Make and Load DB from CSV".  After selecting where you wish to save the DB file and which CSV's you wish to load, the program will create, populate, and index the DB.
    6. When complete(currently only indicated by processor usage), you may then access the Database to view information about the simulation by selecting the "Access Database" menu and selecting "Simulation Viewer".
    
    7. The Simuation Viewer function takes the longest amount of time to run. Be paitient.
    8. When complete, it opens a window with three graphs and some text.
    9. The viewer will also have an entry box with a button. By entering the integer name of a particle into the box and hitting the button, a popup will appear with information pertaining to the individual particle.  If one does not appear, either the particle has no entries because it was fused into a child particle during initial placement or there is a problem with that particle's entries in the CSV.  Note that there will be more particles in the simulation than were initially placed in it. When collisions occur in the simulation, for example, a collision between particle 5 and 6 in a 10 particle simulation would create a new particle named particle 11 and remove the two parent particles.

Hope you like it half as much as I enjoyed coding it.  This was a very fun project for a very interesting class.

I am also considering again expanding this gravity program for a yet undetermined ISP.  I'll talk to you about it when I return in January.

Each line in the particle csv averages to be about 0.00061035 Megabytes, 0.625 Kilobytes, 624 bytes per line
lines are is per particle per iteration.

"""

root = Tk()

def hello():
    pass

class Simulation:
	def __init__(self):
		self.Particle_List = []
		self.Particle_History = []
		self.Collision_History = []
		self.Iteration_Rate = 1.0
		self.Current_Instance = 0.0
		self.Active_Particles = 0
		self.Particle_Iter = 0
		self.Paused = True
		self.Gravitational_Constant = 0.00125
		self.DB = ""
		
	def Clear_Particle_List(self):
		self.Particle_List = []
		self.Current_Instance = 0.0
		self.Particle_History = []
		self.Collision_History = []
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
	
	def Update_Particle_History(self):
		for p in self.Particle_List:
			name = p.name
			instance = p.instance
			mass = p.mass
			x = p.x
			y = p.y
			xvel = p.xvel
			yvel = p.yvel
			xaccel = p.xaccel
			yaccel = p.yaccel
			xforce = p.xforce
			yforce = p.yforce
			Data = [instance,name,mass,x,y,xvel,yvel,xaccel,yaccel,xforce,yforce]
			self.Particle_History.append(Data)
			
	def One_Step(self):
		self.Update_Particle_History()
		self.Current_Instance += self.Iteration_Rate
		self.Get_Force_Distance()
		for p in self.Particle_List:
			Universe.status_bar.update()
			p.Get_Instance()
			p.Update_Position()
			p.Detect_Collision(p)
			p.Get_Instance()

	def csvExport(self):
		ParticleCSVFileHandle = tkFileDialog.asksaveasfilename(parent=root,title="Save the Particle CSV as...")
		CollisionCSVFileHandle = tkFileDialog.asksaveasfilename(parent=root,title="Save the Collision CSV as...")
		
		LineString = ""
		LineString += "Instance,Name,Mass,X,Y,Xvel,Yvel,Xaccel,Yaccel\n"
		for i in self.Particle_History:
			LineString += "%f,%d,%f,%f,%f,%f,%f,%f,%f" % (i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8])
			LineString += "\n"
		PFile = open(ParticleCSVFileHandle,'w')
		PFile.write(LineString)
		PFile.close
		
		LineString2 = ""
		LineString2 += "Instance,Parent_A,Parent_B,Child\n"
		for i in self.Collision_History:
			LineString2 += "%f,%f,%f,%f" % (i[0],i[1],i[2],i[3])
			LineString2 += "\n"
		CFile = open(CollisionCSVFileHandle,'w')
		CFile.write(LineString2)
		CFile.close

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
				Collision_List = [self.instance,self.name, P.name, z.name]
				sim.Collision_History.append(Collision_List)
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

class Data_Base():
	def __init__(self):
		sim.DB = sqlite3.Connection("")
		self.createDB(sim.DB)
	def Open_DB(self):
		DB_fh = tkFileDialog.askopenfilename(parent=root,title="Open Database...")
		sim.DB = sqlite3.Connection(DB_fh)
	def createDB(self,db):
		ParticleTable = """
CREATE TABLE IF NOT EXISTS particle (
    iteration NUMERIC,
    name NUMERIC,
    mass NUMERIC,
    xpos NUMERIC,
    ypos NUMERIC,
    xvel  NUMERIC,
    yvel NUMERIC,
    xaccel NUMERIC,
    yaccel NUMERIC
);"""
		CollisionTable = """
CREATE TABLE IF NOT EXISTS collision (
    parent_a NUMERIC,
    parent_b NUMERIC,
    child NUMERIC,
    iteration NUMERIC
);"""
		cur = db.cursor()
		cur.execute(ParticleTable)
		cur.execute(CollisionTable)
	def loadData(self,db):
		PCSV = tkFileDialog.askopenfilename(parent=root,title="Open Particle CSV...")
		FCSV = tkFileDialog.askopenfilename(parent=root,title="Open Collision CSV...")
		PFile = csv.reader(open(PCSV))
		dataIter = (i for i in PFile)
		dataIter.next() #skip header
		cur = db.cursor()
		cur.executemany("INSERT INTO particle VALUES (?,?,?,?,?,?,?,?,?)", dataIter)
		CFile = csv.reader(open(FCSV))
		dataIter = (i for i in CFile)
		dataIter.next() #skip header
		cur.executemany("INSERT INTO collision VALUES (?,?,?,?)", dataIter)
		cur.execute('CREATE INDEX IF NOT EXISTS ParticleIDX1 ON particle(name)')
		cur.execute('CREATE INDEX IF NOT EXISTS ParticleIDX2 ON	particle(iteration)')
		cur.execute('CREATE INDEX IF NOT EXISTS ParticleIDX3 ON	particle(xvel)')
		cur.execute('CREATE INDEX IF NOT EXISTS ParticleIDX4 ON	particle(yvel)')
		cur.execute('CREATE INDEX IF NOT EXISTS ParticleIDX5 ON	particle(xaccel)')
		cur.execute('CREATE INDEX IF NOT EXISTS ParticleIDX6 ON	particle(yaccel)')

	def Make_DB(self):
		DB_fh = tkFileDialog.asksaveasfilename(parent=root,title="Save the Database as...")
		sim.DB = sqlite3.Connection(DB_fh)
		self.createDB(sim.DB)
		self.loadData(sim.DB)

DB = Data_Base()

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
		
		csvmenu = Menu(menubar, tearoff=0)
		csvmenu.add_command(label="Export to CSV", command=sim.csvExport)
		menubar.add_cascade(label="CSV Management", menu=csvmenu)

		dbmenu = Menu(menubar, tearoff=0)
		dbmenu.add_command(label="Make and Load DB from CSV", command=DB.Make_DB)
		dbmenu.add_command(label="Load DB from .db File", command=DB.Open_DB)
		menubar.add_cascade(label="Database Management", menu=dbmenu)

		viewmenu = Menu(menubar, tearoff=0)
		viewmenu.add_command(label="Simulation Viewer", command=Open_Simulation_Viewer)
		viewmenu.add_command(label="Particle Viewer", command=Open_Particle_Viewer)
		menubar.add_cascade(label="Access Database", menu=viewmenu)
		
		helpmenu = Menu(menubar, tearoff=0)
		helpmenu.add_command(label="How this program works (Does Nothing)", command=self.How_Program_Works_PopUp)
		helpmenu.add_command(label="How to use this program (Does Nothing)", command=self.How_To_Use_Program_PopUp)
		helpmenu.add_command(label="Using Data Viewer (Does Nothing)", command=self.Data_Viewer_PopUp)
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
		
	def Data_Viewer_PopUp(self):
		Type = "Data_Viewer"
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

class Particle_Data_Viewer:
	def __init__(self,p):
		self.p = p
		QUERY = Particle_Queries(self.p)
		
		self.D_Viewer = Toplevel()
		self.D_Viewer.wm_title("Particle Data Viewer")
		Fig_1 = Figure(figsize=(8,4), dpi=75)
		Graph_1 = Fig_1.add_subplot(1.05,1,1)
		Graph_1.plot(QUERY.Vel_Graph)
		Graph_1.set_title('Velocity Per Iteration')
		Graph_1.set_xlabel('Iteration #')
		Graph_1.set_ylabel('Velocity')
		canvas = FigureCanvasTkAgg(Fig_1, master=self.D_Viewer)
		canvas.show()
		canvas.get_tk_widget().grid(row=0,column=0,sticky=W)
		canvas._tkcanvas.grid(row=0,column=0,sticky=W)
		
		Fig_2 = Figure(figsize=(8,4), dpi=75)
		Graph_2 = Fig_2.add_subplot(1.05,1,1)
		Graph_2.plot(QUERY.Accel_Graph)
		Graph_2.set_title('Acceleration Per Iteration')
		Graph_2.set_xlabel('Iteration #')
		Graph_2.set_ylabel('Acceleration')
		canvas = FigureCanvasTkAgg(Fig_2, master=self.D_Viewer)
		canvas.show()
		canvas.get_tk_widget().grid(row=1,column=0,sticky=W)
		canvas._tkcanvas.grid(row=1,column=0,sticky=W)
		text_info = Message(self.D_Viewer, text="""
		Particle # %d
		Created on Iteration # %f
		Removed on Iteration # %f \n
		Active for %f iterations \n
		Average Velocity: %f
		Lowest Velocity: %f
		Highest Velocity: %f
		Starting Velocity: %f
		Final Velocity: %f \n
		Average Acceleration: %f
		Lowest Acceleration: %f
		Highest Acceleration: %f
		Starting Acceleration: %f
		Final Acceleration: %f \n
		Highest X: %f
		Lowest X: %f
		Highest Y: %f
		Lowest Y: %f \n
		Starting Position: (%f,  %f)
		Final Position: (%f,  %f) \n
		"""%(QUERY.Particle_Name,QUERY.birth,QUERY.death,QUERY.lifespan,
		QUERY.avg_vel,QUERY.min_vel,QUERY.max_vel,QUERY.init_vel,QUERY.final_vel,
		QUERY.avg_accel,QUERY.min_accel,QUERY.max_accel,QUERY.init_accel,QUERY.final_accel,
		QUERY.min_x,QUERY.max_x,QUERY.min_y,QUERY.max_y,QUERY.init_x,QUERY.init_y,QUERY.final_x,QUERY.final_y))
		text_info.grid(column=1,row=0,sticky=N,rowspan=2)

class Particle_Queries:
	def __init__(self,p):
		cur = sim.DB.cursor()
		self.Particle_Name = int(p)
		self.Vel_Graph,self.avg_vel,self.min_vel,self.max_vel,self.init_vel,self.final_vel = self.QUERY_Particle_Velocities(sim.DB,p)
		self.Accel_Graph,self.avg_accel,self.min_accel,self.max_accel,self.init_accel,self.final_accel = self.QUERY_Particle_Accels(sim.DB,p)
		self.x,self.y,self.min_x,self.max_x,self.min_y,self.max_y,self.init_x,self.init_y,self.final_x,self.final_y = self.QUERY_Particle_Positions(sim.DB,p)
		self.birth,self.death,self.lifespan = self.QUERY_Particle_Iterations(sim.DB,p)

	def Get_Particle_Data(self,db,Particle_Name,Column_Type):
		Universe.space.update()
		Universe.status_bar.update()
		if Column_Type is "velocity":
			Col_X = "xvel"
			Col_Y = "yvel"
			cur = db.cursor()
			cur.execute("SELECT ALL iteration,%s,%s FROM particle WHERE name = %s" %(Col_X,Col_Y,Particle_Name))
			data = cur.fetchall()
			data.sort()
			w = [(i[1],i[2]) for i in data]
			return w
		elif Column_Type is "accelleration":
			Col_X = "xaccel"
			Col_Y = "yaccel"
			cur = db.cursor()
			cur.execute("SELECT ALL iteration,%s,%s FROM particle WHERE name = %s" %(Col_X,Col_Y,Particle_Name))
			data = cur.fetchall()
			data.sort()
			w = [(i[1],i[2]) for i in data]
			return w
		elif Column_Type is "position":
			Col_X = "xpos"
			Col_Y = "ypos"
			cur = db.cursor()
			cur.execute("SELECT ALL iteration,%s,%s FROM particle WHERE name = %s" %(Col_X,Col_Y,Particle_Name))
			data = cur.fetchall()
			data.sort()
			w = [(i[1],i[2]) for i in data]
			return w
		elif Column_Type is "iteration":
			Col_X = 'iteration'
			cur = db.cursor()
			cur.execute("SELECT ALL iteration FROM particle WHERE name = %s" %(Particle_Name))
			data = cur.fetchall()
			data.sort()
			return data
	
	def Merge_XY(self,In_List): #get magnitude
		z = []
		for i in In_List:
			x = i[0]
			y = i[1]
			merge = math.sqrt((x * x) + (y * y))
			z.append(merge)
		return z
	
	def QUERY_Particle_Velocities(self,db,Particle_Name):
		a = self.Get_Particle_Data(db,Particle_Name,"velocity")
		b = self.Merge_XY(a)		# List Of Velocities for Particle sorted by iteration
		c = numpy.mean(b)	# Average Velocity of Particle
		d = min(b)			# Minimum Velocity of Particle
		e = max(b)			# Maximum Velocity of Particle
		f = b[0]			# Initial Velcoity of Particle
		g = b
		g.reverse()
		h = g[0]			# Final Velocity   of Particle
		return (b,c,d,e,f,h)
	
	def QUERY_Particle_Accels(self,db,Particle_Name):
		a = self.Get_Particle_Data(db,Particle_Name,'accelleration')
		b = self.Merge_XY(a)		# List of accelerations for Particle sorted by iteration
		c = numpy.mean(b)	# Average Acceleration of Particle
		d = min(b)			# Minimum Acceleration of Particle
		e = max(b)			# Maximum Acceleration of Particle
		f = b[0]			# Initial Acceleration of Particle
		g = b
		g.reverse()
		h = g[0]			# Final Acceleration   of Particle
		return (b,c,d,e,f,h)
	
	def QUERY_Particle_Positions(self,db,Particle_Name):
		a = self.Get_Particle_Data(db,Particle_Name,'position')
		x = [i[0] for i in a]
		y = [i[1] for i in a]
		minx = min(x)
		maxx = max(x)
		miny = min(y)
		maxy = max(y)
		initx = x[0]
		inity = y[0]
		x.reverse()
		y.reverse()
		finalx = x[0]
		finaly = x[0]
		x.reverse()
		y.reverse()
		return (x,y,minx,maxx,miny,maxy,initx,inity,finalx,finaly)

	def QUERY_Particle_Iterations(self,db,Particle_Name):
		a = self.Get_Particle_Data(db,Particle_Name,'iteration')
		t = [i[0] for i in a]
		b = t[1]
		c = max(t)
		d = c - b
		return (b,c,d)

class Simulation_Data_Viewer:
	def __init__(self):
		QUERY = Simulation_Queries()
		master = Toplevel()
		master.wm_title("Simulation Data Viewer")
		
		Fig_1 = Figure(figsize=(5,4), dpi=75)
		Graph_1 = Fig_1.add_subplot(1.25,1,1)
		Graph_1.set_title('Average Velocity Per Iteration')
		Graph_1.set_xlabel('Iteration')
		Graph_1.set_ylabel('Average Velocity')

		Fig_2 = Figure(figsize=(5,4), dpi=75)
		Graph_2 = Fig_2.add_subplot(1.25,1,1)
		Graph_2.set_title('Average Acceleration Per Iteration')
		Graph_2.set_xlabel('Iteration')
		Graph_2.set_ylabel('Average Acceleration')

		Fig_3 = Figure(figsize=(5,4), dpi=75)
		Graph_3 = Fig_3.add_subplot(1.25,1,1)
		Graph_3.set_title('Active Particles Per Iteration')
		Graph_3.set_xlabel('Iteration')
		Graph_3.set_ylabel('Active Particles')
		
		Graph_1.plot(QUERY.Velocity_Averages_Per_Iteration)
		canvas1 = FigureCanvasTkAgg(Fig_1, master=master)
		canvas1.show()
		canvas1.get_tk_widget().grid(row=0,column=0)
		canvas1._tkcanvas.grid(row=0,column=0)
		
		Graph_2.plot(QUERY.Acceleration_Averages_Per_Iteration)
		canvas2 = FigureCanvasTkAgg(Fig_2, master=master)
		canvas2.show()
		canvas2.get_tk_widget().grid(row=0,column=1)
		canvas2._tkcanvas.grid(row=0,column=1)
		
		Graph_3.plot(QUERY.Particles_Per_Iteration)
		canvas3 = FigureCanvasTkAgg(Fig_3, master=master)
		canvas3.show()
		canvas3.get_tk_widget().grid(row=0,column=2)
		canvas3._tkcanvas.grid(row=0,column=2)
		text_info = Message(master, text="""Initial Iteration #: %f\n Final Iteration #: %f \n Length of Simulation: %f""" %(QUERY.Init_Iter,QUERY.Final_Iter,QUERY.Sim_Length))
		text_info.grid(row=1,column=0)
		cur = sim.DB.cursor()
		cur.execute("SELECT DISTINCT name FROM particle")
		data = cur.fetchall()
		num = len(data)
		particle_range = Message(master, text="Particle's Name's Range from 1 to %d" %(num))
		particle_range.grid(row=1,column=2)
		self.E1_value = DoubleVar()
		E1 = Tkinter.Entry(master, textvariable=self.E1_value).grid(row=1,column=1)
		Make_Button = Tkinter.Button(master, text='View Particle', command=self.getAttributes).grid(row=2,column=1)
		
	def getAttributes(self):
		next_particle = self.E1_value.get()
		x = int(next_particle)
		Open_Particle_Viewer(x)

class Simulation_Queries:
	def __init__(self):
		self.Iter_Iter,self.Init_Iter,self.Final_Iter,self.Sim_Length = self.Get_Simulation_Length()
		self.Particles_Per_Iteration = self.Get_Particles_Per_Iteration()
		self.Velocity_Averages_Per_Iteration = self.Get_Avg_Vel_Graph()
		self.Acceleration_Averages_Per_Iteration = self.Get_Avg_Accel_Graph()

	def Merge_XY(self,In_List): #get magnitude
		z = []
		for i in In_List:
			x = i[0]
			y = i[1]
			merge = math.sqrt((x * x) + (y * y))
			z.append(merge)
		return z
		
	def Get_Simulation_Length(self):
		Universe.space.update()
		Universe.status_bar.update()
		cur = sim.DB.cursor()
		cur.execute("SELECT DISTINCT iteration FROM particle")
		d = cur.fetchall()
		alpha = min(d)
		omega = max(d)
		Sim_Length = omega[0] - alpha[0]
		return (d,alpha[0],omega[0],Sim_Length)

	def Get_Particles_Per_Iteration(self):
		Universe.space.update()
		Universe.status_bar.update()
		cur = sim.DB.cursor()
		Particles_Per_Iteration = []
		self.Iter_Iter.sort()
		for i in self.Iter_Iter:
			cur.execute("SELECT DISTINCT name FROM particle WHERE iteration = %f" %(i))
			num = len(cur.fetchall())
			Particles_Per_Iteration.append(num)
		return Particles_Per_Iteration

	def Get_Avg_Vel_Graph(self):
		Universe.space.update()
		Universe.status_bar.update()
		cur = sim.DB.cursor()
		Iter_Velocity_Averages = []
		self.Iter_Iter.sort()
		for i in self.Iter_Iter:
			cur.execute("SELECT DISTINCT name FROM particle WHERE iteration = %f" %(i))
			data = cur.fetchall()
			Iter_Velocities = []
			for p in data:
				cur.execute("SELECT ALL xvel,yvel FROM particle WHERE iteration = %f AND name = %d" %(i[0],p[0]))
				d = cur.fetchall()
				Velocity = self.Merge_XY(d)
				Iter_Velocities.append(float(Velocity[0]))
			Average = numpy.mean(Iter_Velocities)
			Iter_Velocity_Averages.append(Average)
		return Iter_Velocity_Averages

	def Get_Avg_Accel_Graph(self):
		Universe.space.update()
		Universe.status_bar.update()
		cur = sim.DB.cursor()
		Iter_Acceleration_Averages = []
		self.Iter_Iter.sort()
		for i in self.Iter_Iter:
			cur.execute("SELECT DISTINCT name FROM particle WHERE iteration = %f" %(i))
			data = cur.fetchall()
			Iter_Accel = []
			for p in data:
				cur.execute("SELECT ALL xaccel,yaccel FROM particle WHERE iteration = %f AND name = %d" %(i[0],p[0]))
				d = cur.fetchall()
				Acceleration = self.Merge_XY(d)
				Iter_Accel.append(float(Acceleration[0]))
			Average = numpy.mean(Iter_Accel)
			Iter_Acceleration_Averages.append(Average)
		return Iter_Acceleration_Averages

def Open_Simulation_Viewer():
	Sim_Viewer = Simulation_Data_Viewer()

def Open_Particle_Viewer(p):
	Particle_Viewer = Particle_Data_Viewer(p)

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

def Open_Viewer(Viewer_Type):
	if Viewer_Type is 'particle':
		x = Particle_Data_Viewer()
	if Viewer_Type is 'simulation':
		x = Simulation_Data_Viewer

Universe = Main_Window(root)
mainloop()
