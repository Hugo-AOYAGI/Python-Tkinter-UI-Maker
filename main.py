
import tkinter as tk
import sys 
import os
import tkinter.messagebox as msgbox
import tkinter.filedialog as askfile
import time
import json
import inspect
import re
from PIL import Image, ImageTk

"""
 TODO :
   - Option to save widget styling (All options or styling only)
   - Option to write to a stylesheet:
        Eventually style_sheet editor
   - Finish code writing
   - Add option for short style sheet:
        Style Sheet where only changed parameters are written
"""

# Creates the window for the UI Builder
class UIMaker:

    #CONSTANTS
    WIDGETS = ["Frame", "LabelFrame", "Canvas", "Label", "Message", "Text", "Button", "Entry", "Listbox", "Menubutton", "OptionMenu", "Checkbutton", "Radiobutton", "Spinbox", "Menu", "PanedWindow"]

    PARENTS = ["Frame", "LabelFrame", "Canvas", "Tk", "PanedWindow"]

    WINDOW_PROPS = ["title", "width", "height", "xpos", "ypos"]

    WIDGET_CUSTOM_PROPS = ["relx", "rely", "relwidth", "relheight"]

    WIDGET_SHORTS = ["frame", "lblframe", "canv", "lbl", "msg", "text", "btn", "entry", "listbox", "menubtn", "optionmenu", "checkbtn", "radiobtn", "spinbox", "menu", "pannedwin"]

    NON_STYLE_PROPS = ["scrollregion", "xscrollcommand", "xscrollincrement", "yscrollcommand", "yscrollincrement", "image", "textvariable", "command", "invalidcommand", "invcmd", "validatecommand", "vcmd", "listvariable", "variable", "menu", "selectimage", "tristateimage"]

    SPECIAL_PROPS = ["image", "command", "validatecommand", "vcmd", "selectimage", "tristateimage"]

    def __init__(self):
        # Setting up the main window
        self.root = tk.Tk()
        self.root.title("UI Maker")
        self.root.geometry("1100x600+0+0")
        self.root.configure(background='#A9A9A9')

        self.root.bind("<Configure>", lambda evt: self.changeWindowProps("width", evt))
        
        # WINDOW VARIABLES
        self.user_widgets = {} # Widget Name ==> Widget Instance
        self.widget_vars = {} # Widget Name ==> Control Variable
        self.prop_vars = {} # Property Name ==> Tkinter Variable
        self.input_fields = {} # Property Name ==> Tkinter Entry
        self.problem_count = 0
        self.widget_position = {} # Widget Name ==> Position and Size Tuple
        self.pop_win = False
        self.old_ratio = 0
        self.ui_json_file_path = ""
        self.assets_path = "None"
        self.assets_images = {} # Image Name ==> PhotoImage Object
        self.widget_images = {} # Widget Name ==> Image Name

        

        # CODE WRITING VARIABLES
        self.code = {
            "tkVars": {},
            "standalones": [],
            "funcs": {
                "None": []
            },
            "parents": {}
        }

        self.style_sheet = {} # Style Class Name ==> Styling Properties

        self.root_options = { # Properties of the window itself like title or geometry
            "title": "Tkinter App",
            "width": "1100",
            "height": "600",
            "xpos": "0",
            "ypos": "0"
        }

        # Setting up the window
        self.setupWidgetsBar()
        self.setupUICanvas()
        self.setupWidgetPropsBar()
        self.setupMenuBar()

    # Creates the upper menu of the window
    def setupMenuBar(self):

        # Create the menu of the root
        self.menu = tk.Menu(self.root)
        
        # File Cascade Menu: Save As, Save, Open, Reset
        filemenu = tk.Menu(self.menu, tearoff=False)
        filemenu.add_command(label="Save as", command=self.saveUI)
        filemenu.add_command(label="Save", command=self.quickSave, accelerator="Ctrl+S")
        filemenu.add_separator()
        filemenu.add_command(label="Open file", command=self.openUI, accelerator="Ctrl+O")
        filemenu.add_separator()
        filemenu.add_command(label="Reset UI", command=self.resetUI)

        self.menu.add_cascade(label="File", menu=filemenu)

        # Edit Cascade Menu: New Function, Write Code
        editmenu = tk.Menu(self.menu, tearoff=False)
        editmenu.add_command(label="New Function", command=self.askAddFunction, accelerator="Ctrl+F")
        editmenu.add_separator()
        editmenu.add_command(label="Write Code", command=self.askWriteCode)

        self.menu.add_cascade(label="Edit", menu=editmenu)

        # Style Cascade Menu: Import Style Sheet, Export StyleSheet
        stylemenu = tk.Menu(self.menu, tearoff=False)
        stylemenu.add_command(label="Import StyleSheet", command=self.importStyleSheet)
        stylemenu.add_command(label="Export StyleSheet", command=self.exportStyleSheet)
        stylemenu.add_command(label="Add Assets Folder", command=self.addAssetsFolder)

        self.menu.add_cascade(label="Style", menu=stylemenu)

        self.root.config(menu=self.menu)

        # Adding shortcuts
        self.root.bind_all("<Control-s>", self.quickSave)
        self.root.bind_all("<Control-o>", self.openUI)
        self.root.bind_all("<Control-f>", self.askAddFunction)

    # Creates the widget bar where you can select all the widgets to place
    def setupWidgetsBar(self):
        
        # Creating the container
        frame = tk.Frame(self.root)
        frame.place(relx=0.25, rely=0.8, relwidth=0.75, relheight=0.2)
        
        # Getting the number of widgets
        n_widgets = len(UIMaker.WIDGETS)

        # Creating buttons for each of the available widgets in two rows 
        for i in range(int(n_widgets / 2)):
            for j in range(2):
                widget_name = UIMaker.WIDGETS[int(i+j*(n_widgets/2))]
                btn = tk.Button(frame, text=widget_name, command=lambda x=widget_name: self.getWidgetParameters(x))
                btn.place(relx=i/(n_widgets/2), rely=j*0.5, relwidth=1/(n_widgets/2), relheight=0.5)
    
    # Ask the user to add a new assets folder
    def addAssetsFolder(self, dir_ = 0):
        self.assets_images = {}
        if dir_ == "None":
            return
        # Create the dialog window
        dir_ = askfile.askdirectory() if not dir_ else dir_

        if not dir_:
            return 

        self.assets_path = dir_

        for filename in os.listdir(dir_):
            if filename[-4::] in [".png", ".PNG", ".jpg", ".JPG", ".jpeg", ".JPEG", ".gif", ".GIF"]:
                img = Image.open(os.path.join(dir_, filename))
                self.assets_images.update({filename: ImageTk.PhotoImage(img)})

                    
    # Returns a list of all the files from a directory
    def loopThroughDir(self, dir_):
        files = []
        for filename in os.listdir(dir_):
            if os.path.isdir(filename):
                files += self.loopThroughDir(filename)
            else:
                files.append(filename)
        return files
        

    # Asks for the widget parameters such as parent or name
    def askAddFunction(self, *args):
        if self.pop_win:
            msgbox.showwarning("warning","Please close or confirm the previous Pop Up before opening another one.")
            return 0
        
        self.pop_win = PopUp(self.root, "Create Function", self.createNewFunc)
        self.pop_win.addCloseFunc(self.pop_up_close)

        self.pop_win.addInput("Entry", "Function Name", self.code["funcs"].keys())
        
    def createNewFunc(self, evt, variables):
        self.code["funcs"].update({variables["Function Name"].get(): []})
        self.pop_win.top.destroy()
        self.pop_win = False

    # Creates the widgets properties bar where you can set all the widget styling
    def setupWidgetPropsBar(self):

        # Creating the container
        frame = tk.Frame(self.root, bg="blue")
        frame.place(relx=0, rely=0, relheight=1, relwidth=0.25)

        # Option Menu with all the widgets 

        # Creating the tkinter var and setting the default value
        self.selected_widget_name = tk.StringVar()
        self.selected_widget_name.set("root")

        # Adding a title label
        title_lbl = tk.Label(frame, text="Widget Properties")
        title_lbl.place(relx=0, rely=0, relwidth=1, relheight=0.1)

        # Creating the option menu
        self.option_menu = tk.OptionMenu(frame, self.selected_widget_name, "root")
        self.option_menu.place(relx=0, rely=0.1, relwidth=1, relheight=0.05)
        self.selected_widget_name.trace_add("write", self.selectWidget)

        # Creating the widget action bar: delete, copy
        action_bar = tk.Frame(frame)
        action_bar.place(relx=0, rely=0.15, relwidth=1, relheight=0.05)

        self.delete_btn = tk.Button(action_bar, text="Delete", command=self.deleteWidget)
        self.delete_btn.place(relx=0, rely=0, relwidth=0.33, relheight=1)

        self.save_style_btn = tk.Button(action_bar, text="Save Styling", command=self.askSaveStyling)
        self.save_style_btn.place(relx=0.33, rely=0, relwidth=0.33, relheight=1)

        self.style_btn = tk.Button(action_bar, text="Chose Styling", command=self.askStyling)
        self.style_btn.place(relx=0.66, rely=0, relwidth=0.33, relheight=1)

        # Creating a canvas in order to add a scrollbar
        self.props_canv = tk.Canvas(frame, scrollregion = (0, 0, 100, 2000))
        self.props_canv.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)

        self.sb = tk.Scrollbar(self.props_canv, command = self.props_canv.yview)
        self.sb.place(relx=0, rely=0, relwidth=0.05, relheight=1)

        self.props_canv.config(yscrollcommand=self.sb.set)

        # Creating the frame where the properties are displayed
        self.props_frame = tk.Frame(self.props_canv, width=260, height=1800)
        
        self.props_canv.create_window(140, 900, window=self.props_frame)

        # Adding the mousewheel handler
        self.props_canv.bind_all("<MouseWheel>", self._on_mousewheel)

        # Selects the default widget to print its properties
        self.selectWidget()
    
    def _on_mousewheel(self, event):
        self.props_canv.yview_scroll(int(-1*(event.delta/120)), "units")
 
    # Refreshes the option menu when new widgets are added 
    def refreshOptionMenu(self):
        # Deleting old values
        self.selected_widget_name.set("root")
        self.option_menu['menu'].delete(0, 'end')

        # Adding the new values
        for widget in self.user_widgets.keys():
            self.option_menu['menu'].add_command(label=widget, command=tk._setit(self.selected_widget_name, widget))
    
    # Refreshes the widget properties for the newly selected widget.
    def getWidgetProperties(self):

        self.props_canv.yview_moveto(0)

        self.prev = self.selected_widget_name.get()
        # Getting the selected widget

        selected = self.user_widgets[self.selected_widget_name.get()]

        # Checks if the widget is the actual window, if so display its properties.
        if selected == "root_window":
            names = self.root_options.keys()
            values = self.root_options.values()
            
            self.createWidgetPropertiesInputs(names, values, [])
        else:
        # Checks if the widget is any other widget
            # Adding the custom properties
            names = UIMaker.WIDGET_CUSTOM_PROPS.copy()
            # Getting the current size and position properties
            pos = self.widget_position[self.selected_widget_name.get()]
            values = [pos[0], pos[1], pos[2], pos[3]]

            names += list(selected.keys())

            # List for properties with special pop up inputs (ex: image, command)
            popup_props = []

            # Remove the non style properties to then add them in a separate list for pop up input properties
            for name in names:
                if name in UIMaker.NON_STYLE_PROPS:
                    names.remove(name)
                    if name in UIMaker.SPECIAL_PROPS:
                        popup_props.append(name)
                    

            values += [selected[key] for key in filter(lambda x: x not in UIMaker.NON_STYLE_PROPS, list(selected.keys()))]
            
            self.createWidgetPropertiesInputs(names, values, popup_props)
            
    # Creates all the inputs for the widget properties
    def createWidgetPropertiesInputs(self, names, values, popup_props, types = 0):

        self.prop_vars = {}
        
        for child in self.props_frame.winfo_children():
            child.destroy()
        
        last_i = 0
        
        for i, name in enumerate(names):
            last_i = i
            w = 0.33 if types != 0 else 0.5

            # Creating the name label
            name_lbl = tk.Label(self.props_frame, text=name)
            name_lbl.place(relx=0, rely=0.02*i, relwidth=w, relheight=0.02)

            # Creating the type label if there is one
            if types != 0:
                type_lbl = tk.Label(self.props_frame, text=types[0])
                type_lbl.place(relx=w, rely=0.02*i, relwidth=w, relheight=0.02)

            # Creating the input and the variable

            self.prop_vars.update({name: tk.StringVar()})

            # Adding event listener to the string variable
            self.prop_vars[name].set(list(values)[i])
            if name not in UIMaker.WINDOW_PROPS:
                self.prop_vars[name].trace_add("write", lambda e1, e2, e3, x=name: self.reloadProperties(x, e1, e2, e3))
            else:
                self.prop_vars[name].trace_add("write", lambda e1, e2, e3, x=name: self.changeWindowProps(x, e1, e2, e3))

            entry = tk.Entry(self.props_frame, textvariable=self.prop_vars[name])
            self.input_fields.update({name: entry})
            n = 1 if types == 0 else 2
            entry.place(relx=w*n, rely=0.02*i, relwidth=w, relheight=0.02)
        
        # Adding inputs for commands and images properties
        for i, name in enumerate(popup_props):
            
            if name in ["image", "tristateimage", "selectimage"]:
                btn = tk.Button(self.props_frame, text=name, command=lambda x=name: self.widgetImageAsk(x))
                btn.place(relx=0, rely=0.02*(i+last_i), relwidth=1, relheight=0.02)
            
            if name in ["command", "validatecommand", "vcmd"]:
                btn = tk.Button(self.props_frame, text=name, command=lambda x=name: self.widgetCommandAsk(x))
                btn.place(relx=0, rely=0.02*(i+last_i), relwidth=1, relheight=0.02)
            
    
    def widgetImageAsk(self, name):
        # Checks if a pop up window is already opened
        if self.pop_win:
            msgbox.showwarning("Warning","Please close or confirm the previous Pop Up before opening another one.")
            return 0
        
        if len(self.assets_images.keys()) == 0:
            msgbox.showwarning("Warning","No images have been added to the assets folder !")
            return 0
        

        self.pop_win = PopUp(self.root, "Choose an Image for the widget", self.updateWidgetImage, name)
        self.pop_win.addInput("OptionMenu", "Widget Image", self.assets_images.keys())
        self.pop_win.addCloseFunc(self.pop_up_close)

    def widgetCommandAsk(self, name):
        # Checks if a pop up window is already opened
        if self.pop_win:
            msgbox.showwarning("Warning","Please close or confirm the previous Pop Up before opening another one.")
            return 0
        
        self.pop_win = PopUp(self.root, "Choose a command for the widget", self.updateWidgetCommand, name)
    
    def updateWidgetImage(self, name, variables):
        widg = self.user_widgets[self.selected_widget_name.get()]
        widg[name] = self.assets_images[variables["Widget Image"].get()]

        # Updating the images dict
        if self.selected_widget_name.get() not in self.widget_images.keys():
            self.widget_images.update({self.selected_widget_name.get(): self.assets_images[variables["Widget Image"].get()]})
        else:
            self.widget_images[self.selected_widget_name.get()] = self.assets_images[variables["Widget Image"].get()]

        self.pop_win = 0

    def updateWidgetCommand(self, event, variables):
        pass
        

    def deleteWidget(self, widg = False):
        to_delete = self.selected_widget_name.get() if not widg else widg
        if to_delete == "root":
            msgbox.showwarning('Warning', "Can't delete the root window or else you won't have an app")
            return 0
        # Delete the widget's children if there are
        children = self.user_widgets[to_delete].winfo_children()

        keys_to_kill = []

        for name in self.user_widgets.keys():
            if self.user_widgets[name] in children:
                keys_to_kill.append(name)
        
        for key in keys_to_kill:
            self.user_widgets[key].destroy()
            del self.user_widgets[key]

        # Delete the widget itself
        self.user_widgets[to_delete].destroy()
        del self.user_widgets[to_delete]

        # Reset the widget option menu
        self.selected_widget_name.set("root")
        self.refreshOptionMenu()
    
    def saveUI(self, quick = False):
        if self.problem_count > 0:
            msgbox.showwarning("Warning", "Please fix all the current problems before trying to save the UI !")


        # Create the json file to save the UI
        UI = {}

        # Save the assets folder location
        UI["assets_path"] = self.assets_path

        self.sheet = {}

        # Creating the stylesheet
        for widg_name in filter(lambda x: x!="root", self.user_widgets.keys()):
            # Retrieve widget position
            pos = self.widget_position[widg_name]

            # Retrieve widget properties
            props_names = self.user_widgets[widg_name].keys()
            vals = [self.user_widgets[widg_name][prop] for prop in props_names]
            styling = {props_names[i]: vals[i] for i in range(len(vals))}

            # Handle special case
            for key, val in styling.items():
                if type(val) != str and type(val) != int and type(val) != float:
                    styling[key] = styling[key].string

            # Update sheet
            self.sheet.update({widg_name: {"styling": styling, "position": pos}})
        
        # Save the widget names and properties in json

        UI["widget_names"] = list(self.user_widgets.keys())

        UI["root_options"] = self.root_options

        # Save the code dict
        UI["code"] = self.code

        UI["sheet"] = self.sheet

        UI["types"] = {}

        # Saving the class of each widget
        for widget in UI["widget_names"]:
            if widget != "root":
                UI["types"].update({widget: self.user_widgets[widget].winfo_class()})

        path_ = askfile.asksaveasfile(defaultextension=".json") if not quick else self.ui_json_file_path

        if not path_:
            return

        self.ui_json_file_path = path_.name if not quick else path_

        # Save the ui in a json file
        with open(self.ui_json_file_path, "w") as ui_file:
            json.dump(UI, ui_file)

    def quickSave(self, *args):
        if self.ui_json_file_path != "":
            self.saveUI(True)
        else:
            self.saveUI()

    def openUI(self, *args):
        path_ = askfile.askopenfile(defaultextension=".json")

        if not path_:
            return

        with open(path_.name, "r") as ui_file:
            # Load the json file
            ui_dict = json.load(ui_file)
            
            # Update the window variables
            self.code = ui_dict["code"]
            self.types = ui_dict["types"]
            self.root_options = ui_dict["root_options"]
            self.changeWindowSize()

            # Add the assets folder
            self.addAssetsFolder(ui_dict["assets_path"])

            layer_parents = ["root"]
            new_layer_parents = []
            seen_widgets = ["root"]

            # Delete all the current widgets
            to_delete = list(filter(lambda x: x != "root", self.user_widgets.keys()))
            for widg in to_delete:
                self.deleteWidget(widg)


            # Go through all the layers and hierarchy of the widget tree
            while len(seen_widgets) < len(ui_dict["widget_names"]):

                # Loop through the parents of the current layer                
                for parent in layer_parents:
                    new_layer_parents = []
                    if parent in self.code["parents"]:
                        
                        # Loop through the children of that parent
                        for widget in self.code["parents"][parent]:
                            if widget in seen_widgets:
                                continue
                            # Setting up their properties
                            variables = {"Widget Name": tk.StringVar(), "Is Standalone": tk.BooleanVar(), "Widget Parent": tk.StringVar(), "Created in Function": tk.StringVar()}
                        
                            # Getting the values of their parameters
                            variables["Widget Parent"].set(parent)
                            variables["Widget Name"].set(widget)
                            variables["Is Standalone"].set(True if widget in self.code["standalones"] else False)

                            # Finding their creation function
                            variables["Created in Function"].set(self.findCreationFunc(widget))

                            new_layer_parents.append(widget)
                            seen_widgets.append(widget)
                            
                            # Place the widget
                            self.placeWidget(self.types[widget], variables)
                
                # Setting up the new layer
                layer_parents = new_layer_parents
            
            for widget in filter(lambda x: x!="root", self.user_widgets.keys()):
                self.updateWidgetPropertiesFromSheet(widget, ui_dict["sheet"][widget])

            print(self.user_widgets)

    def updateWidgetPropertiesFromSheet(self, widg_name, sheet):
        for prop in sheet["styling"].keys():
            self.user_widgets[widg_name][prop] = sheet["styling"][prop]
        self.reloadProperties("relwidth", widg_name, sheet["position"][0], sheet["position"][1], sheet["position"][2], sheet["position"][3])

    def findCreationFunc(self, widget):
        for func in self.code["funcs"].keys():
            if widget in self.code["funcs"][func]:
                return func
            
    def findParent(self, widget):
        for parent in self.code["parents"].keys():
            if widget in self.code["parents"][parent]:
                return parent
    

    def askSaveStyling(self):
        # Checks if a pop up window is already opened
        if self.pop_win:
            msgbox.showwarning("Warning","Please close or confirm the previous Pop Up before opening another one.")
            return 0
        
        widget_name = self.selected_widget_name.get()

        # Asking for the class name
        self.pop_win = PopUp(self.root, "Widget Styling", self.saveStyling, widget_name)
        self.pop_win.addCloseFunc(self.pop_up_close)
        self.pop_win.addInput("Entry", "Class Name", self.style_sheet.keys())

    def saveStyling(self, widg_name, variables):
        self.pop_win = 0
        # Getting the widget properties
        names = list(self.user_widgets[widg_name].keys())
        values = [self.user_widgets[widg_name][key] for key in names]

        # Appending the properties to a dictionary
        new_class = {}
        for i, name in enumerate(names):
            new_class.update({name: values[i]})
        
        # Updating the style sheet
        self.style_sheet.update({variables["Class Name"].get(): new_class})

    # Spawns a new window to ask which styling to apply to the widget
    def askStyling(self):
        # Checks if a pop up window is already opened
        if self.pop_win:
            msgbox.showwarning("Warning","Please close or confirm the previous Pop Up before opening another one.")
            return 0

        if len(self.style_sheet.keys()) == 0:
            msgbox.showwarning("Error", "There is no style sheet yet !")
            return 0
        
        widget_name = self.selected_widget_name.get()

        self.pop_win = PopUp(self.root, "Widget Styling", self.applyStyling, widget_name)
        self.pop_win.addCloseFunc(self.pop_up_close)
        self.pop_win.addInput("OptionMenu", "Styling Class", self.style_sheet.keys())
    
    def applyStyling(self, name, variables):
        self.pop_win = 0
        try:
            _class = variables["Styling Class"].get()
            for attr in self.style_sheet[_class]:
                self.user_widgets[name][attr] = self.style_sheet[_class][attr]
            self.getWidgetProperties()
        except:
            msgbox.showwarning("Error", "There was an error somewhere !")
            return 0

    def importStyleSheet(self):
        # Ask for file
        try:
            path = askfile.askopenfile()

            sheet = {}

            with open(path.name, "r") as json_file:
                data = json.load(json_file)

                # Looping through the class names
                for key in data.keys():
                    temp = {}
                    
                    # Looping through the attributes
                    for attr in data[key].keys():
                        temp.update({attr: data[key][attr]})
                    
                    # Adding the styles to the class variable
                    sheet.update({key: temp})
        except:
            msgbox.showerror("Error !", "There was an error trying to open the style sheet.")
            return 0
        
        self.style_sheet.update(sheet)

    def exportStyleSheet(self):
        path = askfile.asksaveasfile()

        with open(path.name, "w") as new_sheet:
            json.dump(self.style_sheet, new_sheet)

    def getChangedProperties(self, widg_name):
        pass

    def resetUI(self):
        self.root.destroy()
        self.__init__()

    # Creates the widget canvas where the widgets are located
    # It is not actually a tkinter Canvas. The widgets are placed dynamically
    def setupUICanvas(self):
        
        # Creating the frame that contains the user UI
        self.ui = tk.Frame(self.root, bg="white")
        self.ui.place(relx=0.25, rely=0.025, relwidth=0.75, relheight=0.75)

        self.user_widgets.update({"root": "root_window"})

        # Creating the error sticker displayed if there is a problem
        self.pb_sticker = tk.Label(self.root, text="Problem(s)", bg="yellow", fg="red")

    # Writes the code for the UI in Python 3

    """
        [Imports]
        
        class [App Name]:
            def __init__(self):
                --> Constructor
                - 'root' Creation and Setup
                - Variable definitions
                - Widget creation from the 'None' Function
                - Calling the widget creation functions
            
            def widgFunc1(self):
                -Widget Creation
            
            def widgFunc2(self):
                -Widget Creation
            
        - Calling the App if name is "__main__"
        - Root MainLoop

    """

    def writeCode(self, path = 0, variables = 0):
        
        self.pop_win = 0

        templates = {}

        code = ""

        style_sheet = {}

        # Saving style to a style_sheet
        for widg_name in self.user_widgets.keys():

            if widg_name == "root":
                continue

            props = {}

            names = list(self.user_widgets[widg_name].keys())
            values = [self.user_widgets[widg_name][key] for key in names]

            for i, name in enumerate(names):
                val = values[i] if isinstance(values[i], (str, int, float)) else values[i].string
                props.update({name: val})
                
            style_sheet.update({widg_name: props})

        with open(os.path.join(os.path.dirname(__file__), "sheet_test.json"), "w") as new_sheet:
            json.dump(style_sheet, new_sheet)

        # Loading all of the templates into a dictionary
        with open(os.path.join(os.path.dirname(__file__), "Templates.txt"), "r") as f:
            data = f.read()
            data = data.split("==>:")
            data = data[1::]
            data = [el.split("<<<") for el in data]
            for i, template in enumerate(data):
                data[i][1] = data[i][1][2::]
                templates.update({template[0]: template[1]})

        # Adding the class creation template

        # Getting the format arguments : title, (w, h, x, y), style_sheet_path
        format_args = [ self.root_options["title"],
                        self.root_options["width"],
                        self.root_options["height"],
                        self.root_options["xpos"],
                        self.root_options["ypos"]]
        code += templates["Class"].format(*format_args)

        # Creating parents in the init function first
        for parent in self.code["parents"].keys():
            if parent in self.code["funcs"]["None"]:
                args = self.getWidgetFormatArgs(parent)
                code += templates["Widget Creation"].format(*args)
                if parent not in self.code["standalones"]:
                    code += templates["Widget Append"].format(parent, args[1])

        # Loops through the widgets in the init function
        for widg_name in self.code["funcs"]["None"]:
            args = self.getWidgetFormatArgs(widg_name)
            code += templates["Widget Creation"].format(*args)
            if widg_name not in self.code["standalones"]:
                code += templates["Widget Append"].format(widg_name, args[1])
    
        # Calling the functions
        for func in variables["sorter_list"]:
            if func == "None":
                continue
            code += templates["Setup Funcs Call"].format(func)
        
        code += templates["Sheet Load Func"].format("sheet_test.json")

        # Looping through the functions

        for func in variables["sorter_list"]:
            if func == "None":
                continue
            code += templates["Function"].format(func)
            for widg_name in self.code["funcs"][func]:
                # Creating parents first
                for parent in self.code["parents"].keys():
                    if parent in self.code["funcs"][func]:
                        args = self.getWidgetFormatArgs(parent)
                        code += templates["Widget Creation"].format(*args)
                        if parent not in self.code["standalones"]:
                            code += templates["Widget Append"].format(parent, args[1])

                # Loops through the widgets
                for widg_name in self.code["funcs"][func]:
                    args = self.getWidgetFormatArgs(widg_name)
                    code += templates["Widget Creation"].format(*args)
                    if widg_name not in self.code["standalones"]:
                        code += templates["Widget Append"].format(widg_name, args[1])

        code += templates["App Call"]


        with open(path.name, "w") as codefile:
            codefile.write(code)

    # Asks the user the options for the code writing. 
    # OPTION:
    # path, stylesheetpathname

    def askWriteCode(self):
        if self.pop_win:
            msgbox.showwarning("warning","Please close or confirm the previous Pop Up before opening another one.")
            return 0

        path = askfile.asksaveasfile()

        self.pop_win = PopUp(self.root, "Test", self.writeCode, path)
        self.pop_win.addCloseFunc(self.pop_up_close)
        self.pop_win.addInput("sorter", "Function Creation Order", ["Sort the functions by order of creation\n (This can impact the way the app works !)", self.code["funcs"].keys()])
    
    def findParentName(self, widg_name):
        for parent in self.code["parents"].keys():
            if widg_name in self.code["parents"][parent]:
                return parent
    
    def getWidgetFormatArgs(self, widg_name):
        # Getting the widget class and short name
        class_ = self.user_widgets[widg_name].winfo_class()
        short = UIMaker.WIDGET_SHORTS[UIMaker.WIDGETS.index(class_)]

        # Checking if the widget is a standalone
        if widg_name in self.code["standalones"]:
            short = "self." + widg_name.replace(" ", "")
            # Checking if the name is allowed (No number as first character)
            if widg_name[0] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                short = "self._" + widg_name[1::]

        # Getting the widget parent
        parent = self.findParentName(widg_name)
        if parent == "root":
            parent = "self.root"
        
        # Getting the position and size
        pos = self.widget_position[widg_name]

        return [widg_name, short, class_, parent, widg_name, short, pos[0], pos[1], pos[2], pos[3]]

    # Returns the writen code to the user, either by asking him to save it or in a label.
    def returnCode(self):
        pass
    
    # Saves the current selected widget properties as a styling class in the main stylesheet.
    def saveToStyleSheet(self):
        pass
    
    # Selects the widget which was clicked on or which was selected in the drop menu.
    def selectWidget(self, *args):
        # Checks if selected widget is the root window
        if self.selected_widget_name.get() == "root":
            # Removing the chose styling and save styling options
            self.delete_btn.place_forget()
            self.save_style_btn.place_forget()
            self.style_btn.place_forget()
        else:
            self.delete_btn.place(relx=0, rely=0, relwidth=0.33, relheight=1)
            self.save_style_btn.place(relx=0.33, rely=0, relwidth=0.33, relheight=1)
            self.style_btn.place(relx=0.66, rely=0, relwidth=0.33, relheight=1)
        # Prevent widget selection if there are problems
        if self.problem_count > 0:
            if self.prev:
                msgbox.showwarning("Warning", "Please fix all the problems in the current widget before selection another one.")
                self.selected_widget_name.set(self.prev)
        else:
            self.getWidgetProperties()
    
    # Places the widget that was selected in the widget selection bar.
    def placeWidget(self, name, variables):
        
        widget_name = variables["Widget Name"].get()
        args = ""

        if name == 'OptionMenu':
            self.code["tkVars"].update({variables["StringVar Name"].get(): tk.StringVar()})
            args = ", self.code['tkVars'][variables['StringVar Name'].get()], '{}'".format("','".join(variables['Default Values'].get().split(",")))
            
        parent = "self.ui" if variables["Widget Parent"].get() == "root" else "self.user_widgets[variables['Widget Parent'].get()]"

        # Adding the parent to the code variable
        if variables["Widget Parent"].get() not in self.code["parents"].keys():
            self.code["parents"].update({variables["Widget Parent"].get(): []})

        self.code["parents"][variables["Widget Parent"].get()].append(widget_name) 

        # Creating the widget
        widget = eval("tk.{}({}{})".format(name, parent, args))
        widget.place(relx=0, rely=0, relwidth=0.2, relheight=0.2)

        # Adding the widget in the dictionary
        self.user_widgets.update({widget_name: widget})
        self.widget_position.update({widget_name: (0, 0, 0.2, 0.2)})

        # Add the widget to the code writing variables
        if variables["Is Standalone"].get() == "1":
            self.code["standalones"].append(widget_name)

        func_name = variables["Created in Function"].get()
        self.code["funcs"][func_name].append(widget_name)

        self.refreshOptionMenu()


        del self.pop_win
        self.pop_win = False
    
    def pop_up_close(self):
        self.pop_win.top.destroy()
        self.pop_win = False

    # Spawns PopUp Window to ask for widget parameters
    def getWidgetParameters(self, name):
        if self.pop_win:
            msgbox.showwarning("warning","Please close or confirm the previous Pop Up before opening another one.")
            return 0
        # Create the pop up window
        self.pop_win = PopUp(self.root, "Widget Creation : {}".format(name), self.placeWidget, name)
        self.pop_win.addCloseFunc(self.pop_up_close)
        
        # Adds the name input field
        self.pop_win.addInput("Entry", "Widget Name", list(self.user_widgets.keys()))

        # Get all the widget that can be parents
        possible_parents = []
        for widget_name in self.user_widgets.keys():
            if widget_name == "root":
                possible_parents.append(widget_name)
                continue
            if self.user_widgets[widget_name].winfo_class() in UIMaker.PARENTS:
                possible_parents.append(widget_name)

        # Adds the parent input field
        self.pop_win.addInput("OptionMenu", "Widget Parent", possible_parents)

        # Adds the standalone checkbox
        self.pop_win.addInput("Checkbutton", "Is Standalone")

        # Adds the created in function:
        self.pop_win.addInput("OptionMenu", "Created in Function", self.code["funcs"].keys())

        # Add special case of OptionMenu
        if name == "OptionMenu":
            self.pop_win.addInput("Entry", "StringVar Name", self.code["tkVars"])
            self.pop_win.addInput("Entry", "Default Values")

    # Reload the selected widget on the canvas after one of its properties was changed.
    def reloadProperties(self, name, *args):
        try:
            # If the Property is a size or pos property, replace widget
            if name in UIMaker.WIDGET_CUSTOM_PROPS:
                widg_name = self.selected_widget_name.get() if len(args) == 3 else args[0]
                self.user_widgets[widg_name].place_forget()
                # Get the position and size
                if len(args) == 3:
                    w, h, x, y = self.prop_vars["relwidth"].get(), self.prop_vars["relheight"].get(), self.prop_vars["relx"].get(), self.prop_vars["rely"].get()
                else:
                    x, y, w, h = args[1], args[2], args[3], args[4]
                self.user_widgets[widg_name].place(relx=x, rely=y, relwidth=w, relheight=h)
                # Update dictionary
                self.widget_position[widg_name] = (x, y, w, h)
                if not args:
                    if self.input_fields[name]["bg"] == "red":
                        self.input_fields[name]["bg"] = "white"
                        self.problem_count -= 1
            else:
            # Else change the actual property
                self.user_widgets[self.selected_widget_name.get()][name] = self.prop_vars[name].get()
                if self.input_fields[name]["bg"] == "red":
                    self.input_fields[name]["bg"] = "white"
                    self.problem_count -= 1
        except:
            # Display problem sticker if there is an issue
            self.pb_sticker.place(relx=0.9, rely=0.05, relwidth=0.1, relheight=0.035)
            if self.input_fields[name]["bg"] != "red":
                self.input_fields[name]["bg"] = "red"
                self.problem_count += 1
        
        self.pb_sticker['text'] = "{} Problem(s)".format(self.problem_count)
        if self.problem_count == 0:
            self.pb_sticker.place_forget()
        
    # Changes the root_option dictionary when the string var are changed
    def changeWindowProps(self, name, *args):
        # Checks if the property is the title, if not make sure the value is allowed
        if name != "title":
            try:
                int(self.prop_vars[name].get())
                self.root_options[name] = self.prop_vars[name].get()
                # Remove error sticker if there was one
                if self.input_fields[name]["bg"] == "red":
                    self.input_fields[name]["bg"] = "white"
                    self.problem_count -= 1
                self.changeWindowSize()
            except:
                # Display error if the value is not allowed (str or float)
                self.pb_sticker.place(relx=0.9, rely=0.05, relwidth=0.1, relheight=0.035)
                if self.input_fields[name]["bg"] != "red":
                    self.input_fields[name]["bg"] = "red"
                    self.problem_count += 1
        else:
            self.root_options[name] = self.prop_vars[name].get()
        self.pb_sticker['text'] = "{} Problem(s)".format(self.problem_count)
        if self.problem_count == 0:
            self.pb_sticker.place_forget()

    # Changes the window size
    def changeWindowSize(self, *args):      

        # Getting the aspect ratio of the window and the new ratio
        new_ratio = int(self.root_options['width'])/int(self.root_options['height'])

        win_ratio = self.root.winfo_width()/self.root.winfo_height()

        if win_ratio == self.old_ratio:
            return 0

        self.old_ratio = win_ratio

        self.old_ratio = new_ratio

        #Check if the new ratio is bigger 
        if new_ratio > win_ratio:
            ui_width = 0.75
            ui_height = ui_width / (new_ratio/win_ratio)
        else:
            ui_height = 0.75
            ui_width = ui_height * (new_ratio/win_ratio)
        
        # Replace the UI
        self.ui.place_forget()
        self.ui.place(relx=0.25+(0.75 - ui_width)/2, rely=0.025+(0.75 - ui_height)/2, relwidth=ui_width, relheight=ui_height)
    
    def reloadPosition(self, *args):
        pass

    # Asks if the user wishes to save the UI before the window closes
    def askCloseWindow(self):
        pass
    

# Creates a pop up to retrieve parameters
class PopUp:

    INPUTS_PRESETS = ["Entry", "OptionMenu", "Checkbutton", "sorter"]

    def __init__(self, root, name, confirm_function, func_args = []):

        # Creating the PopUp window
        self.top = tk.Toplevel(root)
        self.top.title(name)
        self.top.geometry("450x300")

        self.parent = root

        # VARIABLES
        self.variables = {}
        self.prohibited_vals = {} # For entry inputs
        self.confirm_function = confirm_function
        self.func_args = func_args
        self.n_inputs = 0

        # Add confirm button
        confirm = tk.Button(self.top, text="Confirm", command=self.confirm)
        confirm.place(relx=0.3, rely=0.9, relwidth=0.4, relheight=0.1)

        self.top.bind("<Tab>", self.focusNextWindow)

        self.top.bind_all("<Return>", self.confirm)

    # Adds an input amongst multiple presets : Entry, OptionMenu, Checkbutton
    def addInput(self, _type, name, arg = []):
        # Creating the string variable
        self.variables.update({name: tk.StringVar()})

        # Checks if the type is an actual preset
        if _type not in PopUp.INPUTS_PRESETS:
            self.top.destroy()
            return 0
        
        n_inputs = len(self.variables.keys()) - 1
        
        # Creates the input label and widget
        lbl = tk.Label(self.top, text=name, relief="raised")
        lbl.place(relx=0, rely=0.1*n_inputs, relwidth=0.5, relheight=0.1)

        # Entry input for text
        if _type == "Entry":
            input_ = tk.Entry(self.top, textvariable = self.variables[name])
            # Adds the prohibited values if there are 
            self.prohibited_vals.update({name: arg})
        
        # Option menu to chose from multiple options
        elif _type == "OptionMenu":
            input_ = tk.OptionMenu(self.top, self.variables[name], "")
            input_['menu'].delete(0, 'end')
            # Adding the options given in the arguments
            for option in arg:
                input_['menu'].add_command(label=option, command=tk._setit(self.variables[name], option))
            self.variables[name].set(option)

        # Checkbutton input
        elif _type == "Checkbutton":
            # Create the check button
            input_ = tk.Checkbutton(self.top, variable=self.variables[name])
            self.variables[name].set("0")

        # Sorter, sort multiple values in order
        elif _type == "sorter":
            # Creating the "move up" buttons
            self.variables.update({"sorter_list": arg[1]})
            self.variables[name].set("0")
            self.updateSorter(arg[1])
            lbl = tk.Label(self.top, text=arg[0])
            lbl.place(relx=0, rely=0, relwidth=1, relheight=0.1)
        
        if _type != "sorter":
            # Placing the input
            input_.place(relx=0.5, rely=0.1*n_inputs, relwidth=0.5, relheight=0.1)
            if self.n_inputs == 0:
                input_.focus()
    
    def focusNextWindow(self, event):
        event.widget.tk_focusNext().focus()
        return("break")

    def addCloseFunc(self, func):
        self.top.protocol("WM_DELETE_WINDOW", func)
    
    def updateSorter(self, list_):
        for i, el in enumerate(list_):
            color = "#F9F9F9" if i%2==0 else "#D9D9D9"
            btn = tk.Button(self.top, text="Up", command=lambda x=i: self.moveUpSorter(x), bg=color)
            btn.place(relx=0, rely=(0.8)*(i/len(list_)), relwidth=0.1, relheight=(0.8)/(len(list_)))
            lbl = tk.Label(self.top, text=el, bg=color)
            lbl.place(relx=0.1, rely=(0.8)*(i/len(list_)), relwidth=0.9, relheight=(0.8)/(len(list_)))

    def moveUpSorter(self, i):
        if i == 0:
            return 0
        temp = self.variables["sorter_list"][i-1]
        self.variables["sorter_list"][i-1] = self.variables["sorter_list"][i]
        self.variables["sorter_list"][i] = temp

        self.updateSorter(self.variables["sorter_list"])

    def confirm(self, *args):
        for name in self.variables.keys():
            if name == "sorter_list":
                continue
            # Checks if the input is empty
            if self.variables[name].get() == "":
                msgbox.showwarning("ERROR", "Not all parameters were filled in !")
                self.top.lift()
                return 0

            # Checks if the value is prohibited
            if name in self.prohibited_vals:
                if self.variables[name].get() in self.prohibited_vals[name]:
                    msgbox.showwarning("ERROR", "This value for '{}' is prohibited.".format(name))
                    self.top.lift()
                    return 0    

        # Return the inpits and call the confirm function that was set up
        self.confirm_function(self.func_args, self.variables)
        self.parent.unbind("<Return>")
        self.top.destroy()
        

if __name__ == "__main__":
    print("Launching the User Interface Builder...")
    uimaker = UIMaker()

    uimaker.root.mainloop()
    print("Closing the User Interface Builder...")
    


    

    