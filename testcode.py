
# IMPORTS
import tkinter as tk
import json
import os

# Application Class
class TkinterApp:
	
	# Constructor
	def __init__(self):
		
		# Creating the root window
		self.root = tk.Tk()
		
		# Setting the root window parameters
		self.root.title("Tkinter App")
		self.root.geometry("1100x600+0+0")
		
		# Window variables
		self.window_widgets = {} # Widget Name ==> Widget 
		self.tkinter_variables = {} # Variable Name ==> Tkinter Variable
		self.style_sheet = {} # Widget Name ==> Styling

		# Calling the window setup functions
		self.loadStyleSheet()

		# Creating 'Test Button' Widget
		btn = tk.Button(self.root, self.style_sheet["Test Button"])
		btn.place(relx=0, rely=0, relwidth=0.2, relheight=0.2)
		self.window_widgets.update({"Test Button": btn})

	# Loading the style sheet for the widgets
	def loadStyleSheet(self):
		path = os.path.join(os.path.dirname(__file__), "sheet_test.json")
		
		# Opening the json file and loading it into the style_sheet variable
		with open(path, "r") as sheet:
			data = json.load(sheet)
			self.style_sheet =  data


# Running the Application
if __name__ == "__main__":
	app = TkinterApp()
	app.root.mainloop()

