
# IMPORTS
import tkinter as tk
import json
import os
from ctypes import windll
from PIL import Image, ImageTk

# Application Class
class TkinterApp:
    
    # Constructor
    def __init__(self):
        
        # Creating the root window
        self.root = tk.Tk()
        
        # Setting the root window parameters
        self.root.title("Tkinter App")
        self.root.geometry("1600x900+0+0")

        # Making the window less blurry
        windll.shcore.SetProcessDpiAwareness(1)
        self.root.tk.call('tk', 'scaling', 2)
        
        # Window variables
        self.window_widgets = {} # Widget Name --> Widget 
        self.tkinter_variables = {} # Variable Name --> Tkinter Variable
        self.style_sheet = {} # Widget Name --> Styling
        self.assets_dict = {} # Image Name --> PhotoImage Object

        # Calling the window setup functions
        self.loadStyleSheet()

        self.mainMenuSetup()
        self.menu1Setup()
        self.confirmMenuSetup()
        self.menu2Setup()

    # Loading the style sheet for the widgets
    def loadStyleSheet(self):
        path = os.path.join(os.path.dirname(__file__), "test_sheet.json")
        
        # Opening the json file and loading it into the style_sheet variable
        with open(path, "r") as sheet:
            data = json.load(sheet)
            self.style_sheet =  data

    def mainMenuSetup(self):	

        # Creating 'mainMenu' Widget
        frame = tk.Frame(self.root, self.style_sheet["mainMenu"])
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.window_widgets.update({"mainMenu": frame})


        # Creating 'main_menu_title' Widget
        lbl = tk.Label(self.window_widgets['mainMenu'], self.style_sheet["main_menu_title"])
        lbl.place(relx=0.2, rely=0, relwidth=0.6, relheight=0.2)
        self.window_widgets.update({"main_menu_title": lbl})

        # Creating 'menu1btn' Widget
        self.menu1btn = tk.Button(self.window_widgets['mainMenu'], self.style_sheet["menu1btn"], command=lambda: self.menu1Frame.lift())
        self.menu1btn.place(relx=0.4, rely=0.3, relwidth=0.2, relheight=0.15)

        # Creating 'menu2btn' Widget
        self.menu2btn = tk.Button(self.window_widgets['mainMenu'], self.style_sheet["menu2btn"], command=lambda: self.frameMenu2.lift())
        self.menu2btn.place(relx=0.4, rely=0.5, relwidth=0.2, relheight=0.15)

        # Creating 'quitBtn' Widget
        self.quitBtn = tk.Button(self.window_widgets['mainMenu'], self.style_sheet["quitBtn"], command=self.root.destroy)
        self.quitBtn.place(relx=0.42, rely=0.9, relwidth=0.16, relheight=0.1)
            
    def menu1Setup(self):	
        # Creating 'menu1Frame' Widget
        self.menu1Frame = tk.Frame(self.root, self.style_sheet["menu1Frame"])
        self.menu1Frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            
        # Creating 'backbtn' Widget
        self.backbtn = tk.Button(self.menu1Frame, self.style_sheet["backbtn"], command=lambda: self.window_widgets['mainMenu'].lift())
        self.backbtn.place(relx=0, rely=0.9, relwidth=0.2, relheight=0.1)


        # Creating 'menu1title' Widget
        lbl = tk.Label(self.menu1Frame, self.style_sheet["menu1title"])
        lbl.place(relx=0.3, rely=0, relwidth=0.4, relheight=0.2)
        self.window_widgets.update({"menu1title": lbl})


        # Creating 'name_lbl' Widget
        lbl = tk.Label(self.menu1Frame, self.style_sheet["name_lbl"])
        lbl.place(relx=0.2, rely=0.25, relwidth=0.2, relheight=0.2)
        self.window_widgets.update({"name_lbl": lbl})


        # Creating 'age_lbl' Widget
        lbl = tk.Label(self.menu1Frame, self.style_sheet["age_lbl"])
        lbl.place(relx=0.2, rely=0.45, relwidth=0.2, relheight=0.05)
        self.window_widgets.update({"age_lbl": lbl})

        # Creating 'name_entry' Widget
        self.name_entry = tk.Entry(self.menu1Frame, self.style_sheet["name_entry"])
        self.name_entry.place(relx=0.35, rely=0.325, relwidth=0.3, relheight=0.05)
            
        # Creating 'age_input' Widget
        self.age_input = tk.Spinbox(self.menu1Frame, self.style_sheet["age_input"])
        self.age_input.place(relx=0.35, rely=0.45, relwidth=0.3, relheight=0.05)
            

        # Creating 'confirm_btn' Widget
        btn = tk.Button(self.menu1Frame, self.style_sheet["confirm_btn"], command=lambda: self.confirmFrame.lift())
        btn.place(relx=0.4, rely=0.75, relwidth=0.2, relheight=0.1)
        self.window_widgets.update({"confirm_btn": btn})

        # Creating 'pwEntry' Widget
        self.pwEntry = tk.Entry(self.menu1Frame, self.style_sheet["pwEntry"])
        self.pwEntry.place(relx=0.35, rely=0.575, relwidth=0.3, relheight=0.05)
            

        # Creating 'pwLbl' Widget
        lbl = tk.Label(self.menu1Frame, self.style_sheet["pwLbl"])
        lbl.place(relx=0.25, rely=0.575, relwidth=0.1, relheight=0.05)
        self.window_widgets.update({"pwLbl": lbl})

    def confirmMenuSetup(self):	
        # Creating 'confirmFrame' Widget
        self.confirmFrame = tk.Frame(self.root, self.style_sheet["confirmFrame"])
        self.confirmFrame.place(relx=0, rely=0, relwidth=1, relheight=1)
            

        # Creating 'confirmMsg' Widget
        msg = tk.Message(self.confirmFrame, self.style_sheet["confirmMsg"])
        msg.place(relx=0.25, rely=0.2, relwidth=0.5, relheight=0.4)
        self.window_widgets.update({"confirmMsg": msg})


        # Creating 'goBackToMenuBtn' Widget
        btn = tk.Button(self.confirmFrame, self.style_sheet["goBackToMenuBtn"], command=lambda: self.window_widgets['mainMenu'].lift())
        btn.place(relx=0.4, rely=0.6, relwidth=0.2, relheight=0.1)
        self.window_widgets.update({"goBackToMenuBtn": btn})

    def menu2Setup(self):	
        # Creating 'frameMenu2' Widget
        self.frameMenu2 = tk.Frame(self.root, self.style_sheet["frameMenu2"])
        self.frameMenu2.place(relx=0, rely=0, relwidth=1, relheight=1)
            

        # Creating 'menu2title' Widget
        lbl = tk.Label(self.frameMenu2, self.style_sheet["menu2title"])
        lbl.place(relx=0.2, rely=0, relwidth=0.6, relheight=0.2)
        self.window_widgets.update({"menu2title": lbl})


        # Creating 'backBtn2' Widget
        btn = tk.Button(self.frameMenu2, self.style_sheet["backBtn2"], command=lambda: self.window_widgets['mainMenu'].lift())
        btn.place(relx=0, rely=0.9, relwidth=0.2, relheight=0.1)
        self.window_widgets.update({"backBtn2": btn})


# Running the Application
if __name__ == "__main__":
    app = TkinterApp()
    app.root.mainloop()

