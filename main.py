
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
   - Option to write to a stylesheet:
        Eventually style_sheet editor
   - Finish code writing
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

    SPECIAL_PROPS = ["image", "command"]

    def __init__(self):
        # Setting up the main window
        self.root = tk.Tk()
        self.root.title("UI Maker")
        self.root.geometry("1100x600+0+0")
        self.root.configure(background='#A9A9A9')

        self.root.bind("<Configure>", lambda evt: self.changeWindowProps("width", evt))
        self.root.protocol("WM_DELETE_WINDOW", self.askCloseWindow)
        
        # WINDOW VARIABLES
        self.user_widgets = {} # Widget Name ==> Widget Instance
        self.prop_vars = {} # Property Name ==> Tkinter Variable
        self.input_fields = {} # Property Name ==> Tkinter Entry
        self.problem_count = 0
        self.widget_position = {} # Widget Name ==> Position and Size Tuple
        self.pop_win = False
        self.old_ratio = 0
        self.ui_json_file_path = ""
        self.assets_path = "None"
        self.assets_images = {} # Image Name ==> PhotoImage Object
        self.default_widget_properties = {} # Widget Name ==> Properties dict


        # CODE WRITING VARIABLES
        self.code = {
            "tkVars": {},
            "standalones": [],
            "funcs": {
                "None": []
            },
            "parents": {},
            "optionMenuVals": {},
            "optionMenuStringVars": {},
            "types": {},
            "images": {},
            "commands": {}
        }

        self.style_sheet = {} # Style Class Name ==> Styling Properties

        self.root_options = { # Properties of the window itself like title or geometry
            "title": "Tkinter App",
            "width": "1600",
            "height": "900",
            "xpos": "0",
            "ypos": "0"
        }

        # Setting up the window
        self.setupWidgetsBar()
        self.setupUICanvas()
        self.setupWidgetPropsBar()
        self.setupMenuBar()

        self.selectPrev(0)




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
        stylemenu.add_separator()
        stylemenu.add_command(label="Add Assets Folder", command=self.addAssetsFolder, accelerator="Ctrl+A")

        self.menu.add_cascade(label="Style", menu=stylemenu)

        self.root.config(menu=self.menu)

        # Adding shortcuts
        self.root.bind_all("<Control-s>", self.quickSave)
        self.root.bind_all("<Control-o>", self.openUI)
        self.root.bind_all("<Control-f>", self.askAddFunction)
        self.root.bind_all("<Control-a>", self.addAssetsFolder)
        self.root.bind_all("<Control-Down>", self.selectNext)
        self.root.bind_all("<Control-Up>", self.selectPrev)

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
        
        dir_ = 0 if type(dir_) == tk.Event else dir_

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
                if name in UIMaker.SPECIAL_PROPS:
                    popup_props.append(name)
            
            names = list(filter(lambda x: x not in UIMaker.NON_STYLE_PROPS, names))

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
            
            if name in ["command"]:
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
        self.pop_win.addInput("OptionMenu", "Widget to lift", self.user_widgets.keys())
        self.pop_win.addCloseFunc(self.pop_up_close)
    
    def updateWidgetImage(self, name, variables):
        widg = self.user_widgets[self.selected_widget_name.get()]
        widg[name] = self.assets_images[variables["Widget Image"].get()]

        # Updating the images dict
        if self.selected_widget_name.get() not in self.code["images"].keys():
            self.assets_images.update({self.selected_widget_name.get(): self.assets_images[variables["Widget Image"].get()]})
            self.code["images"].update({self.selected_widget_name.get(): variables["Widget Image"].get()})
        else:
            self.assets_images[self.selected_widget_name.get()] = self.assets_images[variables["Widget Image"].get()]
            self.code["images"][self.selected_widget_name.get()] = variables["Widget Image"].get()

        self.pop_win = 0

    def updateWidgetCommand(self, name, variables):
        widg = self.user_widgets[self.selected_widget_name.get()]
        # Add the command to the widget
        widg[name] = lambda x=self.user_widgets[variables["Widget to lift"].get()]: x.lift()

        # Save the command in a dictionary
        if self.selected_widget_name.get() in self.code["commands"].keys():
            self.code["commands"][self.selected_widget_name.get()] = [variables["Widget to lift"].get(), name]
        else:
            self.code["commands"].update({self.selected_widget_name.get(): [variables["Widget to lift"].get(), name]})

        self.pop_win = 0
        

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

        # Delete the widget from all the dictionaries
        for parent in self.code["parents"]:
            if to_delete in self.code["parents"][parent]:
                index = self.code["parents"][parent].index(to_delete)
                del self.code["parents"][parent][index]

        for func in self.code["funcs"]:
            if to_delete in self.code["funcs"][func]:
                index = self.code["funcs"][func].index(to_delete)
                del self.code["funcs"][func][index]

        # Delete the widget itself
        self.user_widgets[to_delete].destroy()
        del self.user_widgets[to_delete]

        # Reset the widget option menu
        self.selected_widget_name.set("root")
        self.refreshOptionMenu()
    
    def saveUI(self, quick = False):
        if self.problem_count > 0:
            msgbox.showwarning("Warning", "Please fix all the current problems before trying to save the UI !")
            return False

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
            styling = {}
            
            for i, name in enumerate(props_names):
                class_ = self.user_widgets[widg_name].winfo_class()
                if vals[i] != self.default_widget_properties[class_][name]:
                    styling.update({name: vals[i]})

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

        print(self.code)

        UI["sheet"] = self.sheet

        path_ = askfile.asksaveasfile(defaultextension=".json") if not quick else self.ui_json_file_path

        if not path_:
            return False

        self.ui_json_file_path = path_.name if not quick else path_

        # Save the ui in a json file
        with open(self.ui_json_file_path, "w") as ui_file:
            json.dump(UI, ui_file)

        return True

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
                            self.placeWidget(self.code["types"][widget], variables)
                
                # Setting up the new layer
                layer_parents = new_layer_parents
            
            for widget in filter(lambda x: x!="root", self.user_widgets.keys()):
                self.updateWidgetPropertiesFromSheet(widget, ui_dict["sheet"][widget])
                # Add command if there was one
                if widget in self.code["commands"].keys():
                    widg_to_lift = self.user_widgets[self.code["commands"][widget][0]]
                    self.user_widgets[widget][self.code["commands"][widget][1]] = lambda x=widg_to_lift: x.lift()


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
            class_ = self.user_widgets[widg_name].winfo_class()
            if values[i] != self.default_widget_properties[class_][name]:
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

    def resetUI(self):
        self.root.destroy()
        self.__init__()

    # Creates the widget canvas where the widgets are located
    # It is not actually a tkinter Canvas. The widgets are placed dynamically
    def setupUICanvas(self):
        
        # Creating the frame that contains the user UI
        self.ui = tk.Frame(self.root, bg="white")
        self.ui.place(relx=0.25, rely=0, relwidth=0.75, relheight=0.80)

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

        print(variables["sorter_list"])

        style_sheet = {}

        controller = CodeWritingController(self.code, path, variables["Sheet Name"].get() + ".json", "assets")

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

        with open(os.path.join(os.path.dirname(__file__), variables["Sheet Name"].get() + ".json"), "w") as new_sheet:
            json.dump(style_sheet, new_sheet)

        controller.addTemplate("class")

        controller.apendFunction("None")

        for func in list(filter(lambda x: x!="None", self.code["funcs"])):
            controller.addTemplate("func_call", func=func)
        
        controller.addTemplate("sheet_load_func")
        controller.addTemplate("assets")
        
        if len(self.code["funcs"].keys()) > 2:
            for func in variables["sorter_list"]:
                controller.appendFunction(func)
        else:
            controller.appendFunction(self.code["funcs"].keys()[0])
        
        controller.addTemplate("app_call")

        with open(path.name, "w") as codefile:
            codefile.write(controller.getCode())

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
        if len(self.code["funcs"].keys()) > 2:
            sorter_args =  ["Sort the functions by order of creation\n (This can impact the way the app works !)", list(filter(lambda x: x!= "None",self.code["funcs"].keys()))]
            self.pop_win.addInput("sorter", "Function Creation Order", sorter_args)
        self.pop_win.addInput("Entry", "Sheet Name")
    


    def findParentName(self, widg_name):
        for parent in self.code["parents"].keys():
            if widg_name in self.code["parents"][parent]:
                return parent
    
    def getWidgetText(self, args, templates):
        if len(args[1]) == 2:
            pass
        if len(args[1]) == 4:
            pass
        if len(args[1]) == 0:
            pass


    def getWidgetFormatArgs(self, widg_name):
        # Getting the widget class and short name
        class_ = self.user_widgets[widg_name].winfo_class()
        short = UIMaker.WIDGET_SHORTS[UIMaker.WIDGETS.index(class_)]

        # Checking if the widget is a standalone
        if widg_name in self.code["standalones"]:
            short = "self." + self.formatName(widg_name.replace(" ", ""))

        # Getting the widget parent
        parent = self.findParentName(widg_name)
        if parent == "root":
            parent = "self.root"
        
        # Getting the position and size
        pos = self.widget_position[widg_name]

        args_1 = [widg_name, short, class_, parent, widg_name, short, pos[0], pos[1], pos[2], pos[3]]
        
        args_2 = []

        if widg_name in self.code["commands"].keys():
            args_2 += [self.code["commands"][widg_name][1], "self.goTo" + self.formatName(self.code["commands"][widg_name][0])]
        if widg_name in self.code["images"].keys():
            args_2 += ["image", "self.assets_dict[{}]".format(self.formatName(self.code["images"][widg_name]))]
            
        return args_1, args_2

    def formatName(self,name):
        pass

       


    
    # Selects the widget which was clicked on or which was selected in the drop menu.
    def selectWidget(self, *args):
        # Checks if selected widget is the root window
        # Prevent widget selection if there are problems
        if self.problem_count > 0:
            if self.prev:
                msgbox.showwarning("Warning", "Please fix all the problems in the current widget before selection another one.")
                self.selected_widget_name.set(self.prev)
        else:
            if self.selected_widget_name.get() == "root":
                # Removing the chose styling and save styling options
                self.delete_btn.place_forget()
                self.save_style_btn.place_forget()
                self.style_btn.place_forget()
            else:
                self.delete_btn.place(relx=0, rely=0, relwidth=0.33, relheight=1)
                self.save_style_btn.place(relx=0.33, rely=0, relwidth=0.33, relheight=1)
                self.style_btn.place(relx=0.66, rely=0, relwidth=0.33, relheight=1)
            self.getWidgetProperties()
    
    def selectNext(self, evt):
        curr = self.selected_widget_name.get()
        widg_list = list(self.user_widgets.keys())
        # Get the name of the next widget in the list
        next_ = widg_list[(widg_list.index(curr) + 1) % (len(widg_list))]
        # Select that widget
        self.selected_widget_name.set(next_)
        self.selectWidget()

    def selectPrev(self, evt):
        curr = self.selected_widget_name.get()
        widg_list = list(self.user_widgets.keys())
        # Get the name of the previous widget in the list
        next_ = widg_list[(widg_list.index(curr) - 1) % (len(widg_list))]
        # Select that widget
        self.selected_widget_name.set(next_)
        self.selectWidget()
    
    # Places the widget that was selected in the widget selection bar.
    def placeWidget(self, name, variables):
        
        widget_name = variables["Widget Name"].get()
        args = ""

        if name == 'OptionMenu':
            self.code["tkVars"].update({variables["StringVar Name"].get(): tk.StringVar()})
            self.code["optionMenuVals"].update({widget_name: "','".join(variables['Default Values'].get().split(","))})
            self.code["optionMenuStringVars"].update({widget_name: variables["StringVar Name"].get()})
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
        self.code["types"].update({widget_name: name})
        self.widget_position.update({widget_name: (0, 0, 0.2, 0.2)})

        # Add the widget properties to the default widget properties
        if name not in self.default_widget_properties.keys():
            self.default_widget_properties.update({name: {}})
            for prop in widget.keys():
                self.default_widget_properties[name].update({prop: widget[prop]})

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
                if len(args) == 3 or len(args) == 0:
                    w, h, x, y = self.prop_vars["relwidth"].get(), self.prop_vars["relheight"].get(), self.prop_vars["relx"].get(), self.prop_vars["rely"].get()
                else:
                    x, y, w, h = args[1], args[2], args[3], args[4]
                self.user_widgets[widg_name].place(relx=x, rely=y, relwidth=w, relheight=h)
                # Update dictionary
                self.widget_position[widg_name] = (x, y, w, h)
                if len(args) == 3 or len(args) == 0:
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
        if name != "title" and self.selected_widget_name.get() == "root":
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
        elif name == "title":
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
            ui_height = 0.80
            ui_width = ui_height * (new_ratio/win_ratio)
        
        # Replace the UI
        self.ui.place_forget()
        self.ui.place(relx=0.25+(0.75 - ui_width)/2, rely=(0.80 - ui_height)/2, relwidth=ui_width, relheight=ui_height)

    # Asks if the user wishes to save the UI before the window closes
    def askCloseWindow(self):
        if msgbox.askyesno("Quit", "Do you wish to save before quitting ?"):
            res = self.saveUI()
            if res:
                self.root.destroy()
                sys.exit()
        else:
            self.root.destroy()
            sys.exit()

    

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
        
        # Creates the input label and widget
        lbl = tk.Label(self.top, text=name, relief="raised")
        lbl.place(relx=0, rely=0.1*self.n_inputs, relwidth=0.5, relheight=0.1)

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
            self.n_inputs += 6
        
        if _type != "sorter":
            # Placing the input
            input_.place(relx=0.5, rely=0.1*self.n_inputs, relwidth=0.5, relheight=0.1)
            if self.n_inputs == 0:
                input_.focus()
            self.n_inputs += 1
    
    def focusNextWindow(self, event):
        event.widget.tk_focusNext().focus()
        return("break")

    def addCloseFunc(self, func):
        self.top.protocol("WM_DELETE_WINDOW", func)
    
    def updateSorter(self, list_):
        for i, el in enumerate(list_):
            color = "#F9F9F9" if i%2==0 else "#D9D9D9"
            btn = tk.Button(self.top, text="Up", command=lambda x=i: self.moveUpSorter(x), bg=color)
            btn.place(relx=0, rely=(0.5)*(i/len(list_)) + 0.1, relwidth=0.1, relheight=(0.5)/(len(list_)))
            lbl = tk.Label(self.top, text=el, bg=color)
            lbl.place(relx=0.1, rely=(0.5)*(i/len(list_)) + 0.1, relwidth=0.9, relheight=(0.5)/(len(list_)))

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
        


class CodeWritingController:

    TEMPLATE_ARGS = json.load(open(os.path.join(os.path.dirname(__file__), "templates_args.json"), "r"))

    def __init__(self, data, root_options, style_sheet_path, assets_path):
        
        self.code_data = data
        self.root_options = root_options
        self.style_sheet_path = style_sheet_path
        self.assets_path = assets_path
        self.code = ""
        self.templates = self.loadTemplates()
    

    def getCode(self):
        return self.code

    def loadTemplates(self):

        templates = {}

        # Loading all of the templates into a dictionary
        with open(os.path.join(os.path.dirname(__file__), "Templates.txt"), "r") as f:
            data = f.read()
            data = data.split("==>:")
            data = data[1::]
            data = [el.split("<<<") for el in data]
            for i, template in enumerate(data):
                data[i][1] = data[i][1][2::]
                templates.update({template[0]: template[1]})
        
        return templates

    # Sort a list of widget with the top level parents first
    def HierarchySort(self, widget_list):

        widgets_seen = []
        
        widget_queue = widget_list.copy()
        
        while len(widget_queue) > 0:

            top_level = False
            current_level_widget = widget[0]
            found_higher = False

            # Find the top level parent of that widget
            while not top_level:
                for parent in self.code_data["parents"]:
                    if current_level_widget in self.code_data["parents"][parent] and parent not in widgets_seen and parent != "root" and parent in widget_list:
                        current_level_widget = parent
                        found_higher = True
                        break

                if not found_higher:
                    widgets_seen.append(current_level_widget)
                    widget_queue = list(filter(lambda x: x!=current_level_widget, widget_queue))
                    break
            
        return widgets_seen

                

    def appendWidget(self, widget):

        template_name = ""

        kwargs = {"widget": widget}
        
        if widget in self.code_data["optionMenuVals"].keys():
            template_name += "Option_Menu_"
        else:
            template_name += "creation_"
        
        if widget in self.code_data["standalones"].keys():
            template_name += "standalone"
        else:
            template_name += "dict"
        
        if widget in self.code_data["images"].keys() and widget in self.code_data["commands"].keys():
            template_name += "_img_and_cmd"
        elif widget in self.code_data["images"].keys():
            template_name += "_img_or_cmd"
            kwargs.update({"prop": "image"})
        elif widget in self.code_data["commands"].keys():
            template_name += "_img_or_cmd"
            kwargs.update({"prop": "command"})
        
        self.addTemplate(template_name, kwargs)

        

    def appendFunction(self, func):
        sorted_widgets = self.HierarchySort(self.code_data["funcs"][func])

        self.addTemplate("func", func=func)

        for widget in sorted_widgets:
            self.appendWidget(widget)

    

    def addTemplate(self, template, **kwargs):
        if template in CodeWritingController.TEMPLATE_ARGS.keys():
            args = self.getArgsFromTemplate(template, **kwargs)
            self.code += self.templates[template].format(args)
        else:
            self.code += self.templates[template]

    def getArgsFromTemplate(self, template, **kwargs):
        
        args_names = CodeWritingController.TEMPLATE_ARGS[template]

        if "widget" in kwargs.keys():
            return self.getWidgetArgs(kwargs["widget"], args_names, kwargs["prop"] if "props" in kwargs.keys() else False)
        
        else:
            return self.getMiscArgs(args_names, kwargs["func"] if "props" in kwargs.keys() else False)
    
    def getMiscArgs(self, args, func):
        
        format_args = []

        for arg in args:
            
            if arg == "win_title":
                format_args.append(self.root_options["title"])

            if arg == "win_x":
                format_args.append(self.root_options["xpos"])

            if arg == "win_y":
                format_args.append(self.root_options["ypos"])

            if arg == "win_w":
                format_args.append(self.root_options["width"])

            if arg == "win_h":
                format_args.append(self.root_options["height"])

            if arg == "func_name":
                format_args.append(self.formatName(func))

            if arg == "sheet_path":
                format_args.append(self.style_sheet_path)

            if arg == "assets_path":
                format_args.append(self.assets_path)
        
        return format_args

    def getWidgetArgs(self, widget, args, prop):

        format_args = []

        widget_type = self.code_data["types"][widget]
        widget_pos = self.code_data["widget_position"][widget]
        
        for arg in args:
            
            if arg == "name":
                format_args.append(widget if "short" in args else formatName(widget))
            
            elif arg == "short":
                format_args.append(UIMaker.WIDGET_SHORTS[UIMaker.WIDGETS.index(widget_type)])

            elif arg == "widget":
                format_args.append(widget_type)
            
            elif arg == "parent":
                format_args.append(self.findParentOf(widget))
            
            elif arg == "x":
                format_args.append(widget_pos[0])
            
            elif arg == "y":
                format_args.append(widget_pos[1])
            
            elif arg == "w":
                format_args.append(widget_pos[2])
            
            elif arg == "h":
                format_args.append(widget_pos[3])

            elif arg == "var_name":
                format_args.append(self.code_data["optionMenuStringVar"])

            elif arg == "options":
                format_args.append("'" + self.code_data["optionMenuVals"] + "'")
            
            elif arg == "props_name":
                format_args.append(prop)
            
            elif arg == "props_value":
                if prop == "command":
                    format_args.append("lambda: print('Command Coming Soon..')")
                else:
                    format_args.append("self.assets_dict[{}]".format(self.code["images"][widget]))
            
            elif arg == "img_value":
                format_args.append("self.assets_dict[{}]".format(self.code["images"][widget]))

            elif arg == "cmd_value":
                format_args.append("lambda: print('Command Coming Soon..')")

        return format_args

    def findParentOf(self, widget):
        
        for parent in self.code_data["parents"]:
            if widget in self.code_data["parents"][parent]:
                return parent

    def formatName(self, name):
        res = ""
        next_up = False
        for char in name:
            if char == " ":
                next_up = True
            else:
                res += char if not next_up else char.upper()
        return res

if __name__ == "__main__":
    print("Launching the User Interface Builder...")
    uimaker = UIMaker()

    uimaker.root.mainloop()
    


    

    