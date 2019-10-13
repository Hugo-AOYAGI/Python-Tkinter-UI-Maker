
import tkinter as tk
import sys 
import os
import tkinter.messagebox as msgbox
import tkinter.filedialog as askfile
import time
import json
import inspect
import re

"""
 TODO :
   - Option to save widget styling (All options or styling only)
   - Option to write to a stylesheet:
        Eventually style_sheet editor
   - Option to save a UI
   - UI loading feature
   - Fix code writing bugs:
        Gotta find the bugs first ..
   - Add option for short style sheet:
        Style Sheet where only changed parameters are written
   - Assets folder feature:
        Add a folder where you can put assets images to re-use in UI
"""

# Creates the window for the UI Builder
class UIMaker:

    #CONSTANTS
    WIDGETS = ["Frame", "LabelFrame", "Canvas", "Label", "Message", "Text", "Button", "Entry", "Listbox", "Menubutton", "OptionMenu", "Checkbutton", "Radiobutton", "Spinbox", "Menu", "PanedWindow"]

    PARENTS = ["Frame", "LabelFrame", "Canvas", "Tk", "PanedWindow"]

    WINDOW_PROPS = ["title", "width", "height", "xpos", "ypos"]

    WIDGET_CUSTOM_PROPS = ["relx", "rely", "relwidth", "relheight"]

    WIDGET_SHORTS = ["frame", "lblframe", "canv", "lbl", "msg", "text", "btn", "entry", "listbox", "menubtn", "optionmenu", "checkbtn", "radiobtn", "spinbox", "menu", "pannedwin"]

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


        # FOR TEST PURPOSES
        var1 = tk.StringVar()
        var1.set("Test Button")
        var2 = tk.StringVar()
        var2.set("root")
        var3 = tk.StringVar()
        var3.set("0")
        var4 = tk.StringVar()
        var4.set("None")
        self.placeWidget("Button", {"Widget Name": var1, "Widget Parent": var2, "Is Standalone": var3, "Created in Function": var4})
        
        """
        The Window contains 3 main parts : 
            - the Canvas where the UI is drawn
            - the Properties panel to change the widget styling
            - the Widget selection bar to choose widgets to place

        ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        ░░╔══════╦═════════════════════╗░░
        ░░║░░░░░░║░░░░░░░░░░░░░░░░░░░░░║░░
        ░░║░░P░░░║░░░░░░░░░░░░░░░░░░░░░║░░
        ░░║░░R░░░║░░░░░░░░░░░░░░░░░░░░░║░░
        ░░║░░O░░░║░░░  UI Canvas  ░░░░░║░░
        ░░║░░P░░░║░░░░░░░░░░░░░░░░░░░░░║░░
        ░░║░░E░░░║░░░░░░░░░░░░░░░░░░░░░║░░
        ░░║░░R░░░║░░░░░░░░░░░░░░░░░░░░░║░░
        ░░║░░T░░░║░░░░░░░░░░░░░░░░░░░░░║░░
        ░░║░░I░░░╠═════════════════════╣░░
        ░░║░░E░░░║░░░░░░░░░░░░░░░░░░░░░║░░
        ░░║░░S░░░║░░░░ Widget Bar ░░░░░║░░
        ░░║░░░░░░║░░░░░░░░░░░░░░░░░░░░░║░░
        ░░╚══════╩═════════════════════╝░░
        ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
        """

    # Creates the upper menu of the window
    def setupMenuBar(self):
        frame = tk.Frame(self.root, bg="#DFDFDF")
        frame.place(relx=0.25, rely=0, relwidth=0.75, relheight=0.05)

        # Adding button to add new functions to the code
        func_btn = tk.Button(frame, text="New Function", command=self.askAddFunction)
        func_btn.place(relx=0, rely=0, relwidth=0.10, relheight=1)

        # Adding button to write the code
        write_btn = tk.Button(frame, text="Write Code", command=self.askWriteCode)
        write_btn.place(relx=0.10, rely=0, relwidth=0.10, relheight=1)

        # Adding button to save the UI
        save_btn = tk.Button(frame, text="Save UI", command=self.saveUI)
        save_btn.place(relx=0.20, rely=0, relwidth=0.10, relheight=1)

        # Adding button to open a UI
        open_btn = tk.Button(frame, text="Open UI", command=self.openUI)
        open_btn.place(relx=0.30, rely=0, relwidth=0.10, relheight=1)

        # Adding button to reset the UI
        reset_btn = tk.Button(frame, text="Reset", command=self.resetUI)
        reset_btn.place(relx=0.40, rely=0, relwidth=0.10, relheight=1)

        # Adding button to add a stylesheet to the UI
        add_btn = tk.Button(frame, text="Add StyleSheet", command=self.importStyleSheet)
        add_btn.place(relx=0.50, rely=0, relwidth=0.15, relheight=1)

        # Adding button to export a stylesheet from the UI
        exp_btn = tk.Button(frame, text="Export StyleSheet", command=self.exportStyleSheet)
        exp_btn.place(relx=0.65, rely=0, relwidth=0.15, relheight=1)

        # Placeholder
        open_btn = tk.Button(frame)
        open_btn.place(relx=0.80, rely=0, relwidth=0.20, relheight=1)

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
    
    # Asks for the widget parameters such as parent or name
    def askAddFunction(self):
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
            
            self.createWidgetPropertiesInputs(names, values)
        else:
        # Checks if the widget is any other widget
            # Adding the custom properties
            names = UIMaker.WIDGET_CUSTOM_PROPS.copy()
            # Getting the current size and position properties
            pos = self.widget_position[self.selected_widget_name.get()]
            values = [pos[0], pos[1], pos[2], pos[3]]

            names += list(selected.keys())
            values += [selected[key] for key in list(selected.keys())]
            
            self.createWidgetPropertiesInputs(names, values)
            
    # Creates all the inputs for the widget properties
    def createWidgetPropertiesInputs(self, names, values, types = 0):

        self.prop_vars = {}
        
        for child in self.props_frame.winfo_children():
            child.destroy()
        
        for i, name in enumerate(names):
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

    def deleteWidget(self):
        if self.selected_widget_name.get() == "root":
            msgbox.showwarning('Warning', "Can't delete the root window or else you won't have an app")
            return 0
        # Delete the widget's children if there are
        children = self.user_widgets[self.selected_widget_name.get()].winfo_children()

        keys_to_kill = []

        for name in self.user_widgets.keys():
            if self.user_widgets[name] in children:
                keys_to_kill.append(name)
        
        for key in keys_to_kill:
            self.user_widgets[key].destroy()
            del self.user_widgets[key]

        # Delete the widget itself
        self.user_widgets[self.selected_widget_name.get()].destroy()
        del self.user_widgets[self.selected_widget_name.get()]

        # Reset the widget option menu
        self.selected_widget_name.set("root")
        self.refreshOptionMenu()
    
    def saveUI(self):
        pass

    def openUI(self):
        pass

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

        with open(path, "w") as new_sheet:
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
        self.ui.place(relx=0.25, rely=0.05, relwidth=0.75, relheight=0.75)

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
        print(variables)
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
        print(variables["Is Standalone"].get())
        if variables["Is Standalone"].get() == "1":
            self.code["standalones"].append(widget_name)

        func_name = variables["Created in Function"].get()
        self.code["funcs"][func_name].append(widget_name)

        self.refreshOptionMenu()

        print(self.code)

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
                self.user_widgets[self.selected_widget_name.get()].place_forget()
                # Get the position and size
                w, h, x, y = self.prop_vars["relwidth"].get(), self.prop_vars["relheight"].get(), self.prop_vars["relx"].get(), self.prop_vars["rely"].get()
                self.user_widgets[self.selected_widget_name.get()].place(relx=x, rely=y, relwidth=w, relheight=h)
                # Update dictionary
                self.widget_position[self.selected_widget_name.get()] = (x, y, w, h)
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
        self.ui.place(relx=0.25+(0.75 - ui_width)/2, rely=0.05+(0.75 - ui_height)/2, relwidth=ui_width, relheight=ui_height)
    
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
        self.top.geometry("600x400")

        self.parent = root

        # VARIABLES
        self.variables = {}
        self.prohibited_vals = {} # For entry inputs
        self.confirm_function = confirm_function
        self.func_args = func_args

        # Add confirm button
        confirm = tk.Button(self.top, text="Confirm", command=self.confirm)
        confirm.place(relx=0.3, rely=0.9, relwidth=0.4, relheight=0.1)

        root.bind("<Return>", self.confirm)

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
        lbl = tk.Label(self.top, text=name)
        lbl.place(relx=0, rely=0.1*n_inputs, relwidth=0.3, relheight=0.1)

        if _type == "Entry":
            input_ = tk.Entry(self.top, textvariable = self.variables[name])
            # Adds the prohibited values if there are 
            self.prohibited_vals.update({name: arg})
        elif _type == "OptionMenu":
            input_ = tk.OptionMenu(self.top, self.variables[name], "")
            input_['menu'].delete(0, 'end')
            # Adding the options given in the arguments
            for option in arg:
                input_['menu'].add_command(label=option, command=tk._setit(self.variables[name], option))
            self.variables[name].set(option)
        elif _type == "Checkbutton":
            # Create the check button
            input_ = tk.Checkbutton(self.top, variable=self.variables[name])
            self.variables[name].set("0")
        
        if _type == "sorter":
            # Creating the "move up" buttons
            self.variables.update({"sorter_list": arg[1]})
            self.variables[name].set("0")
            print(arg)
            self.updateSorter(arg[1])
            lbl = tk.Label(self.top, text=arg[0])
            lbl.place(relx=0, rely=0, relwidth=1, relheight=0.1)
        else:
            # Placing the input
            input_.place(relx=0.4, rely=0.1*n_inputs, relwidth=0.5, relheight=0.1)
    
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
        print(i)
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
                return 0

            # Checks if the value is prohibited
            if name in self.prohibited_vals:
                if self.variables[name].get() in self.prohibited_vals[name]:
                    msgbox.showwarning("ERROR", "This value for '{}' is prohibited.".format(name))
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
    


    

    