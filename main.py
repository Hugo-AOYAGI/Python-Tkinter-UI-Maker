
import tkinter as tk
from tkinter import ttk
import sys 
import os
import tkinter.messagebox as msgbox
import tkinter.filedialog as askfile
import time
import json
import inspect
import re
import webbrowser
from PIL import Image, ImageTk
from ctypes import windll

"""
 TODO :
   - Undo and Redo option
   - Change widget name in parent dict on edit
"""


# Creates the window for the UI Builder
class UIMaker:

    #CONSTANTS
    WIDGETS = ["Frame", "Labelframe", "Canvas", "Label", "Message", "Text", "Button", "Entry", "Listbox", "Menubutton", "OptionMenu", "Checkbutton", "Radiobutton", "Spinbox"]

    PARENTS = ["Frame", "Labelframe", "Canvas", "Tk"]

    WINDOW_PROPS = ["title", "width", "height", "xpos", "ypos"]

    WIDGET_CUSTOM_PROPS = ["relx", "rely", "relwidth", "relheight"]

    WIDGET_SHORTS = ["frame", "lblframe", "canv", "lbl", "msg", "text", "btn", "entry", "listbox", "menubtn", "optionmenu", "checkbtn", "radiobtn", "spinbox", "menu", "pannedwin"]

    NON_STYLE_PROPS = ["scrollregion", "xscrollcommand", "xscrollincrement", "yscrollcommand", "yscrollincrement", "image", "textvariable", "command", "invalidcommand", "invcmd", "validatecommand", "vcmd", "listvariable", "variable", "menu", "selectimage", "tristateimage"]

    SPECIAL_PROPS = ["image", "command"]

    def __init__(self):
        # Setting up the main window
        self.root = tk.Tk()
        self.root.title("UI Maker")
        self.root.geometry("1600x900+0+0")
        self.root.configure(background='#FFFFFF')

        windll.shcore.SetProcessDpiAwareness(1)
        self.root.tk.call('tk', 'scaling', 2)

        # ICONS
        self.appicon = ImageTk.PhotoImage(Image.open(os.path.join("assets", "icons", "icon.png")))
        self.deleteicon = ImageTk.PhotoImage(Image.open(os.path.join("assets", "icons", "delete.png")).resize((25, 25)))
        self.grabicon = ImageTk.PhotoImage(Image.open(os.path.join("assets", "icons", "grab.png")).resize((30, 30)))
        self.editicon = ImageTk.PhotoImage(Image.open(os.path.join("assets", "icons", "edit.png")).resize((30, 30)))
        self.arrowicon = ImageTk.PhotoImage(Image.open(os.path.join("assets", "icons", "down_arrow.png")).resize((15, 12)))


        self.root.tk.call('wm', 'iconphoto', self.root._w, self.appicon)  

        self.root.tk_setPalette(background="#F9F9FF", foreground="#000000")

        self.root.bind("<Configure>", lambda evt: self.changeWindowProps("width", evt))
        self.root.protocol("WM_DELETE_WINDOW", self.askCloseWindow)
        
        # WINDOW VARIABLES
        self.user_widgets = {} # Widget Name ==> Widget Instance
        self.prop_vars = {} # Property Name ==> Tkinter Variable
        self.input_fields = {} # Property Name ==> Tkinter Entry
        self.problem_count = 0
        self.pop_win = False
        self.old_ratio = 0
        self.ui_json_file_path = ""
        self.assets_path = "None"
        self.assets_images = {} # Image Name ==> PhotoImage Object
        self.default_widget_properties = {} # Widget Name ==> Properties dict
        self.stringVars = {}
        self.removed_props = ["Menubutton", "textvariable"]

        self.previous_search_value = "Search for widgets"

        self.selecting = False
        self.editing_widget = False

        self.undo_history = []
        self.redo_history = []

        # CODE WRITING VARIABLES
        self.code = {
            "standalones": [],
            "funcs": {
                "None": []
            },
            "parents": {},
            "optionMenuVals": {},
            "optionMenuStringVars": {},
            "types": {},
            "images": {},
            "commands": {},
            "widget_position": {}
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

        # Misc Menu: Tree View, Settings
        miscmenu = tk.Menu(self.menu, tearoff=False)
        miscmenu.add_command(label="Widget Tree View", command=self.showTreeView)
        miscmenu.add_separator()
        miscmenu.add_command(label="Info", command=self.showInfo)

        self.menu.add_cascade(label="Misc", menu=miscmenu)

        self.root.config(menu=self.menu)

        # Adding shortcuts
        self.root.bind_all("<Control-s>", self.quickSave)
        self.root.bind_all("<Control-o>", self.openUI)
        self.root.bind_all("<Control-f>", self.askAddFunction)
        self.root.bind_all("<Control-a>", self.addAssetsFolder)
        self.root.bind_all("<Control-Down>", self.selectNext)
        self.root.bind_all("<Control-Up>", self.selectPrev)
        self.root.bind_all("<Up>", self.up_arrow_scroll)
        self.root.bind_all("<Down>", self.down_arrow_scroll)

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
                btn = tk.Button(frame, text=widget_name, command=lambda x=widget_name: self.getWidgetParameters(x), relief="groove", font=("Arial", 10), fg="#101050")
                btn.place(relx=i/(n_widgets/2), rely=j*0.5, relwidth=1/(n_widgets/2), relheight=0.5)

    def showInfo(self):
        self.info_win = tk.Toplevel(self.root)
        self.info_win.geometry("800x600")

        title = tk.Label(self.info_win, text="INFORMATION", font=("Arial", 20))
        title.place(relwidth=1, relheight=0.1)

        git_title = tk.Label(self.info_win, text="Github : ", font=("Arial", 13, "bold"))
        git_title.place(relx=0, rely=0.15, relwidth=0.3, relheight=0.05)

        path = "https://github.com/Hugo-AOYAGI/Python-Tkinter-UI-Maker"

        git_link = tk.Label(self.info_win, text="github.com/Hugo-AOYAGI/Python-Tkinter-UI-Maker", fg="blue")
        git_link.place(relx=0.3, rely=0.15, relwidth=0.7, relheight=0.05)
        git_link.bind("<Button-1>", lambda evt: webbrowser.open(path, new=2))

        credits_title = tk.Label(self.info_win, text="Credits : ", font=("Arial", 13, "bold"))
        credits_title.place(relx=0, rely=0.20, relwidth=0.3, relheight=0.05)

        credits_icons = tk.Label(self.info_win, text="Icons by Hawcons (http://www.hawcons.com) ")
        credits_icons.place(relx=0.3, rely=0.20, relwidth=0.7, relheight=0.05)

    def showTreeView(self):
        self.tree_view_win = tk.Toplevel(self.root)
        self.tree_view_win.geometry("800x600")

        style = ttk.Style(self.tree_view_win)
        style.configure('Treeview', rowheight=25) 

        self.treeview = ttk.Treeview(self.tree_view_win, selectmode="browse") 
        self.treeview["columns"]=("one")

        self.vsb = tk.Scrollbar(self.tree_view_win, orient="vertical", command=self.treeview.yview)
        self.vsb.place(x=780, rely=0, relheight=1, width=20)

        self.treeview.column("#0", width=650, minwidth=150, stretch=tk.NO)
        self.treeview.column("one", width=150, minwidth=100, stretch=tk.NO)

        self.treeview.heading("#0", text="Name", anchor=tk.W)
        self.treeview.heading("one", text="Type", anchor=tk.W)
        
        index = 0

        root = self.treeview.insert("", "end", "root", text="root", values=("MainWindow"))

        next_level_parents = []
        current_level_parents = [(root, 'root')]
        lowest = False

        while not lowest:
            if len(list(self.code["parents"].keys())) == 0:
                break
            for folder, parent in current_level_parents:
                for widget in self.code["parents"][parent]:
                    if widget in list(self.code["parents"].keys()):
                        new_folder = self.treeview.insert(folder, "end", index, text=widget, values=self.code["types"][widget])
                        next_level_parents.append((new_folder, widget))
                        index += 1
                    else:
                        self.treeview.insert(folder, "end", index, text=widget, values=self.code["types"][widget])
                        self.treeview.see(index)
                        index += 1
            if next_level_parents == []:
                lowest = True
            current_level_parents = next_level_parents
            next_level_parents = []
                    
        self.treeview.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.tree_view_win.bind("<Configure>", self.updateTreeViewSize)

    def updateTreeViewSize(self, *args):
        self.treeview.column("#0", width=int(0.8*args[0].width))
        self.treeview.column("one", width=int(0.2*args[0].width))

        if args[0].width > 100:
            self.vsb.place_forget()
            self.vsb.place(x=args[0].width-20, y=0, height=args[0].height, width=20)
        

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
        
        self.pop_win = PopUp(self.root, "Create Function",self, self.createNewFunc)
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
        title_lbl = tk.Label(frame, text="WIDGET PROPERTIES", font=("Arial", 12, "bold"), fg="#101060")
        title_lbl.place(relx=0, rely=0, relwidth=1, relheight=0.1)

        # Creating the option menu
        self.option_menu = tk.OptionMenu(frame, self.selected_widget_name, "root")
        self.option_menu.configure(relief="groove", indicatoron=0, image=self.arrowicon, compound="right")
        self.option_menu.place(relx=0, rely=0.1, relwidth=0.55, relheight=0.05)
        self.selected_widget_name.trace_add("write", self.selectWidget)

        # Creating the search bar
        self.search = tk.StringVar()
        self.search.set("Search for widgets")
        self.search.trace_add("write", self.searchUpdate)

        self.search_bar = tk.Entry(frame, textvariable=self.search, font=("Arial", 8), fg="#909090")
        self.search_bar.place(relx=0.55, rely=0.1, relwidth=0.35, relheight=0.05)

        self.search_results = tk.Frame(frame, bg="red")
        self.search_results.place(relx=0.5, rely=0.15, relwidth=0.5, relheight=0.2)

        self.searchUpdate()

        # Touch to select button
        
        self.touch_select_btn = tk.Button(frame, command=self.touchToSelect,image=self.grabicon, relief="groove")
        self.touch_select_btn.place(relx=0.9, rely=0.1, relheight=0.05, relwidth=0.1)

        self.touchToSelectSetup()

        # Creating the widget action bar: delete, copy
        action_bar = tk.Frame(frame)
        action_bar.place(relx=0, rely=0.15, relwidth=1, relheight=0.05)

        action_bar_font = ("Arial", 7)

        self.save_style_btn = tk.Button(action_bar, text="Save Styling", command=self.askSaveStyling, font=action_bar_font,relief="groove")

        self.style_btn = tk.Button(action_bar, text="Choose Styling", command=self.askStyling, font=action_bar_font, relief="groove")

        self.edit_btn = tk.Button(action_bar, command=self.askEditWidget, relief="groove", image=self.editicon)

        self.delete_btn = tk.Button(action_bar, command=self.deleteWidget, relief="groove", image=self.deleteicon)

        # Creating a canvas in order to add a scrollbar
        self.props_canv = tk.Canvas(frame, scrollregion = (0, 0, 100, 2000), yscrollincrement="2")
        self.props_canv.place(relx=0, rely=0.2, relwidth=1, relheight=0.8)

        self.sb = tk.Scrollbar(self.props_canv, command = self.props_canv.yview)
        self.sb.place(relx=0, rely=0, relwidth=0.05, relheight=1)

        self.props_canv.config(yscrollcommand=self.sb.set)

        # Creating the frame where the properties are displayed
        self.props_frame = tk.Frame(self.props_canv, width=370, height=1800)
        
        self.props_canv.create_window(205, 900, window=self.props_frame)

        # Adding the mousewheel handler
        self.props_canv.bind_all("<MouseWheel>", self._on_mousewheel)

        # Selects the default widget to print its properties
        self.selectWidget()
    
    def searchUpdate(self, *args):

        search_value = self.search.get().lstrip(" ")

        # Placeholder

        self.search.set(search_value)

        test_a = len(search_value) < 18 and self.previous_search_value == "Search for widgets"
        test_b = len(search_value) > 18 and search_value.replace(" ", "") == "Searchforwidgets"

        if search_value == "" or search_value == "Search for widgets" or test_a or test_b:
            self.previous_search_value = "Search for widgets"
            self.setPlaceholder()
        elif self.previous_search_value == "Search for widgets":
            self.previous_search_value = search_value
            self.search_bar.configure(fg="#050560")
            temp = [char for char in search_value]
            for char in [char for char in "Search for widgets"]:
                temp.remove(char)
            self.search.set("".join(temp))
            search_value = temp[0]
        else:
            self.previous_search_value = search_value
            self.search_bar.configure(fg="#050560")

        # Check for widgets

        possible_widgets = []

        for widget in self.user_widgets.keys():
            if widget.startswith(search_value) and search_value != "":
                possible_widgets.append(widget)
        if len(possible_widgets) > 0:
            self.showSearchResults(possible_widgets)
        else: 
            self.removeSearchResults()

    def removeSearchResults(self):
        self.search_results.place_forget()

    def showSearchResults(self, results):
        for child in self.search_results.winfo_children():
            child.destroy()
        
        self.search_results.place(relx=0.5, rely=0.15, relwidth=0.5, relheight=0.04*len(results))
        self.search_results.lift()

        for i, widget in enumerate(results):
            btn = tk.Button(self.search_results, text=widget, command=lambda x=widget: self.searchResultPress(x), relief="groove")
            btn.place(relx=0, rely=(1/len(results))*i, relwidth=1, relheight=(1/len(results)))
        self.root.bind("<Return>", lambda evt, x=results[0]: self.searchResultPress(x, evt))
        
    def searchResultPress(self, widget_name, *args):
        self.selected_widget_name.set(widget_name)
        self.selectWidget()
        self.search.set("")
        self.searchUpdate()

    def setPlaceholder(self):
        self.search_bar.configure(fg="#909090")
        self.search.set("Search for widgets")

    def touchToSelectSetup(self):

        # Creating screen blocker
        self.sb_left = tk.Frame(self.root, bg="#FAFAFA", relief="groove")
        self.sb_bottom = tk.Frame(self.root, bg="#FAFAFA", relief="groove")

        # Creation stop select button
        self.stop_touch_select_btn = tk.Button(self.sb_left, command=self.touchToSelectStop,image=self.grabicon, relief="groove")
        self.stop_touch_select_btn.place(relx=0.9, rely=0.1, relheight=0.05, relwidth=0.1)

        # Adding label
        title = tk.Label(self.sb_left, text="Click on a widget\nto select it.", bg="#FAFAFA", font=('Arial', 16))
        title.place(relx=0.1, rely=0.05, relheight=0.1, relwidth=0.8)
        
    def touchToSelect(self):

        self.root.configure(cursor="crosshair")
        
        self.sb_left.place(relx=0, rely=0, relwidth=0.25, relheight=1)
        self.sb_bottom.place(relx=0.25, rely=0.8, relwidth=0.75, relheight=0.2)

        self.selecting = True
        
        for widget in list(self.user_widgets.keys()):
            if widget == "root":
                self.ui.bind("<Button-1>", lambda evt, x=widget:self.touchToSelectPress(x, evt))
            else:
                self.user_widgets[widget].bind("<Button-1>", lambda evt, x=widget:self.touchToSelectPress(x, evt))


    def touchToSelectStop(self):
        self.sb_left.place_forget()
        self.sb_bottom.place_forget()
        self.root.configure(cursor="arrow")

        # Unbinding all mouse clicks
        for widget in list(self.user_widgets.keys()):
            if widget == "root":
                self.ui.unbind("<Button-1>")
            else:
                self.user_widgets[widget].unbind("<Button-1>")

        self.selecting = False

    def touchToSelectPress(self, widget, *args):
        self.selecting = False

        self.selected_widget_name.set(widget)
        self.selectWidget()

        self.touchToSelectStop()
        

    def _on_mousewheel(self, event):
        self.props_canv.yview_scroll(int(-5*(event.delta/120)), "units")
 
    def down_arrow_scroll(self, event):
        self.props_canv.yview_scroll(18, "units")

    def up_arrow_scroll(self, event):
        self.props_canv.yview_scroll(-18, "units")

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
            pos = self.code["widget_position"][self.selected_widget_name.get()]
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
                btn = tk.Button(self.props_frame, text=name, command=lambda x=name: self.widgetImageAsk(x), relief="groove")
                btn.place(relx=0, rely=0.02*(i+last_i), relwidth=1, relheight=0.02)
            
            if name in ["command"]:
                btn = tk.Button(self.props_frame, text=name, command=lambda x=name: self.widgetCommandAsk(x), relief="groove")
                btn.place(relx=0, rely=0.02*(i+last_i), relwidth=1, relheight=0.02)
            
    # Create pop up to get new widget properties (name, parent ..etc)
    def askEditWidget(self, widget = False):
        widget_name = self.selected_widget_name.get() if not widget else widget

        type_ = self.code["types"][widget_name]

        option_menu_args = []
        if type_ == "OptionMenu":
            option_menu_args = [self.code["optionMenuStringVars"][widget_name], self.code["optionMenuVals"][widget_name]]

        # Create parameters pop_up
        self.getWidgetParameters(type_)

        # Fill in the current values for thoses parameters
        self.pop_win.setInputsValues([widget_name, 
                                    self.findParent(widget_name), 
                                    int(widget_name in self.code["standalones"]),
                                    self.findCreationFunc(widget_name)
                                    ] + option_menu_args)
        
        # Allowing the same name for the widget
        self.pop_win.prohibited_vals["Widget Name"].remove(widget_name)

        # Blocking the parent option menu
        sb = tk.Label(self.pop_win.top, text="Parent: "+self.findParent(widget_name)+" (Cannot be edited)", relief="groove")
        sb.place(relx=0, rely=0.1, relwidth=1, relheight=0.1)

        self.pop_win.confirm_function = self.editWidget
        self.pop_win.func_args = [widget_name, self.findCreationFunc(widget_name)]
        
    # Edit the code variables of a widget from pop_up inputs
    def editWidget(self, arguments, variables, *args):
        
        self.pop_win = 0

        widget_name, previous_func = arguments[0], arguments[1]

        # Getting the new_name of the widget
        new_name = variables["Widget Name"].get()

        # If the name was changed, change the name in all the self.code dictionaries if lists
        if new_name != widget_name:
            for category in self.code.keys():
                if isinstance(self.code[category], (list)):
                    self.code[category] = [new_name if el == widget_name else el for el in self.code[category]]
                else:
                    for key in list(self.code[category].keys()):
                        if key == widget_name:
                            # Copy the previous value into a new key-value pair and delete the previous one
                            self.code[category][new_name] = self.code[category][key]  
                            del self.code[category][key]
        
            self.user_widgets[new_name] = self.user_widgets[widget_name]
            del self.user_widgets[widget_name]

        # Changing the function
        self.code["funcs"][previous_func].remove(widget_name)
        self.code["funcs"][variables["Created in Function"].get()].append(new_name)
        
        # Changing the parent
        parent = self.findParent(widget_name)
        self.code["parents"][parent].remove(widget_name)
        self.code["parents"][parent].append(new_name)

        # Changing the standalone value
        if new_name in self.code["standalones"] and not variables["Is Standalone"].get():
            self.code["standalones"].remove(new_name)
        elif new_name not in self.code["standalones"] and variables["Is Standalone"].get():
            self.code["standalones"].append(new_name)

        self.refreshOptionMenu()
        
    
    def widgetImageAsk(self, name):
        # Checks if a pop up window is already opened
        if self.pop_win:
            msgbox.showwarning("Warning","Please close or confirm the previous Pop Up before opening another one.")
            return 0
        
        if len(self.assets_images.keys()) == 0:
            msgbox.showwarning("Warning","No images have been added to the assets folder !")
            return 0
        

        self.pop_win = PopUp(self.root, "Choose an Image for the widget", self, self.updateWidgetImage, name)
        self.pop_win.addInput("OptionMenu", "Widget Image", self.assets_images.keys())
        self.pop_win.addCloseFunc(self.pop_up_close)

    def widgetCommandAsk(self, name):
        # Checks if a pop up window is already opened
        if self.pop_win:
            msgbox.showwarning("Warning","Please close or confirm the previous Pop Up before opening another one.")
            return 0
        
        self.pop_win = PopUp(self.root, "Choose a command for the widget", self, self.updateWidgetCommand, name)
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
        

    def deleteWidget(self, widg = False, *args):
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
        
        keys_to_kill.append(to_delete)

        for key in keys_to_kill:
            self.user_widgets[key].destroy()
            del self.user_widgets[key]

            # Delete the widget from all the dictionaries
            for parent in self.code["parents"]:
                if key in self.code["parents"][parent]:
                    index = self.code["parents"][parent].index(key)
                    del self.code["parents"][parent][index]

            for func in self.code["funcs"]:
                if key in self.code["funcs"][func]:
                    index = self.code["funcs"][func].index(key)
                    del self.code["funcs"][func][index]
            
            del self.code["types"][key]
            if key in self.code["optionMenuVals"].keys():
                del self.code["optionMenuVals"][key]
                del self.code["optionMenuStringVars"][key]
                del self.stringVars[key]

            if key in self.code["images"].keys():
                del self.code["images"][key]
            if key in self.code["commands"].keys():
                del self.code["commands"][key]

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
            pos = self.code["widget_position"][widg_name]

            styling = self.getChangedPropertiesSheet(widg_name)

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
            while len(seen_widgets) < len(ui_dict["widget_names"]) and layer_parents != []:
                # Loop through the parents of the current layer   
                new_layer_parents = [] 
                for parent in layer_parents:
                    if parent in list(self.code["parents"].keys()):
                        
                        # Loop through the children of that parent
                        for widget in self.code["parents"][parent]:
                            if widget in seen_widgets:
                                continue
                            # Setting up their properties
                            variables = {"Widget Name": tk.StringVar(), 
                                        "Is Standalone": tk.BooleanVar(), 
                                        "Widget Parent": tk.StringVar(), 
                                        "Created in Function": tk.StringVar(),
                                        "StringVar Name": tk.StringVar(),
                                        "Default Values": tk.StringVar()
                                        }
                        
                            # Getting the values of their parameters
                            variables["Widget Parent"].set(parent)
                            variables["Widget Name"].set(widget)
                            variables["Is Standalone"].set(True if widget in self.code["standalones"] else False)

                            if widget in self.code["optionMenuVals"].keys():
                                variables["StringVar Name"].set(self.code["optionMenuStringVars"][widget])
                                variables["Default Values"].set(self.code["optionMenuVals"][widget].replace("'", ""))
                                

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

    def findParent(self, widget):
        for parent in self.code["parents"].keys():
            if widget in self.code["parents"][parent]:
                return parent
    
    def findCreationFunc(self, widget):
        for func in self.code["funcs"].keys():
            if widget in self.code["funcs"][func]:
                return func

    def askSaveStyling(self):
        # Checks if a pop up window is already opened
        if self.pop_win:
            msgbox.showwarning("Warning","Please close or confirm the previous Pop Up before opening another one.")
            return 0
        
        widget_name = self.selected_widget_name.get()

        # Asking for the class name
        self.pop_win = PopUp(self.root, "Widget Styling", self, self.saveStyling, widget_name)
        self.pop_win.addCloseFunc(self.pop_up_close)
        self.pop_win.addInput("Entry", "Class Name", self.style_sheet.keys())

    def saveStyling(self, widg_name, variables):
        self.pop_win = 0
    
        # Updating the style sheet
        self.style_sheet.update({variables["Class Name"].get(): self.getChangedPropertiesSheet(widg_name)})

    def getChangedPropertiesSheet(self, widg_name):
        # Getting the widget properties
        names = list(self.user_widgets[widg_name].keys())
        filtered_props = list(filter(lambda x: x not in self.removed_props,names))
        values = [self.user_widgets[widg_name][key] for key in filtered_props]


        # Appending the properties to a dictionary
        new_class = {}
        for i, name in enumerate(filtered_props):
            class_ = self.user_widgets[widg_name].winfo_class() if widg_name not in self.code["optionMenuVals"].keys() else "OptionMenu"
            if values[i] != self.default_widget_properties[class_][name]:
                new_class.update({name: values[i]})
        
        return new_class

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

        self.pop_win = PopUp(self.root, "Widget Styling", self, self.applyStyling, widget_name)
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

    def writeCode(self, path = 0, variables = 0):
        
        self.pop_win = 0

        style_sheet = {}

        controller = CodeWritingController(self.code, self.root_options, variables["Sheet Name"].get() + ".json", "assets")

        # Saving style to a style_sheet
        for widg_name in self.user_widgets.keys():

            if widg_name == "root":
                continue

            changed_props = self.getChangedPropertiesSheet(widg_name)
            props = {}
            
            for name in list(changed_props.keys()):
                if isinstance(changed_props[name], tk.Menu):
                    break
                value = changed_props[name] if isinstance(changed_props[name], (str, int, float)) else changed_props[name].string
                props.update({name: value})
                
            style_sheet.update({widg_name: props})

        with open(os.path.join(os.path.dirname(path.name), variables["Sheet Name"].get() + ".json"), "w") as new_sheet:
            json.dump(style_sheet, new_sheet)

        controller.addTemplate("class")

        if self.assets_path != "None":
            controller.addTemplate("assets_call")

        controller.appendFunction("None")

        for func in list(filter(lambda x: x!="None", variables["sorter_list"])):
            controller.addTemplate("func_call", func=func)
        
        controller.addTemplate("sheet_load_func")
        if self.assets_path != "None":
            controller.addTemplate("assets")

        if len(list(self.code["funcs"].keys())) > 2:
            for func in variables["sorter_list"]:
                controller.appendFunction(func)
        elif len(list(self.code["funcs"].keys())) == 2:
            controller.appendFunction(list(self.code["funcs"].keys())[1])
        
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

        self.pop_win = PopUp(self.root, "Test", self, self.writeCode, path)
        self.pop_win.addCloseFunc(self.pop_up_close)
        if len(self.code["funcs"].keys()) > 2:
            sorter_args =  ["Sort the functions by order of creation\n (This can impact the way the app works !)", list(filter(lambda x: x!= "None",self.code["funcs"].keys()))]
            self.pop_win.addInput("sorter", "Function Creation Order", sorter_args)
        self.pop_win.addInput("Entry", "Sheet Name")

    
    # Selects the widget which was clicked on or which was selected in the drop menu.
    def selectWidget(self, *args):

        if self.selecting:
            if self.prev:
                self.selected_widget_name.set(self.prev)
            return 0

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
                self.edit_btn.place_forget()
            else:
                self.delete_btn.place(relx=0.9, rely=0, relwidth=0.1, relheight=1)
                self.save_style_btn.place(relx=0, rely=0, relwidth=0.4, relheight=1)
                self.style_btn.place(relx=0.4, rely=0, relwidth=0.4, relheight=1)
                self.edit_btn.place(relx=0.8, rely=0, relwidth=0.1, relheight=1)
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

        # Handling option menu case
        if name == 'OptionMenu':
            # Updating dictionaries
            self.stringVars.update({variables["StringVar Name"].get(): tk.StringVar()})

            # Checking if the widget is already registered in the dictionary
            if widget_name in list(self.code["optionMenuVals"].keys()):
                self.code["optionMenuVals"][widget_name] = "','".join(variables['Default Values'].get().split(","))
                self.code["optionMenuStringVars"][widget_name] = variables["StringVar Name"].get()
            else:
                self.code["optionMenuVals"].update({widget_name: "','".join(variables['Default Values'].get().split(","))})
                self.code["optionMenuStringVars"].update({widget_name: variables["StringVar Name"].get()})
            args = ", self.stringVars[variables['StringVar Name'].get()], '{}'".format("','".join(variables['Default Values'].get().split(",")))
            
        parent = "self.ui" if variables["Widget Parent"].get() == "root" else "self.user_widgets[variables['Widget Parent'].get()]"

        # Adding the parent to the code variable
        if variables["Widget Parent"].get() not in self.code["parents"].keys():
            self.code["parents"].update({variables["Widget Parent"].get(): []})

        if widget_name not in self.code["parents"][variables["Widget Parent"].get()]:
            self.code["parents"][variables["Widget Parent"].get()].append(widget_name) 

        # Creating the widget
        widget = eval("tk.{}({}{})".format(name, parent, args))
        widget.place(relx=0, rely=0, relwidth=0.2, relheight=0.2)

        # Adding the widget in the dictionary
        self.user_widgets.update({widget_name: widget})
        if widget_name not in list(self.code["types"].keys()):
            self.code["types"].update({widget_name: name})
        if widget_name not in list(self.code["widget_position"].keys()):
            self.code["widget_position"].update({widget_name: (0, 0, 0.2, 0.2)})

        # Add the widget properties to the default widget properties
        if name not in self.default_widget_properties.keys():
            self.default_widget_properties.update({name: {}})
            for prop in widget.keys():
                self.default_widget_properties[name].update({prop: widget[prop]})

        # Add the widget to the code writing variables
        if variables["Is Standalone"].get() == "1":
            self.code["standalones"].append(widget_name)

        func_name = variables["Created in Function"].get()
        if widget_name not in list(self.code["funcs"][func_name]):
            self.code["funcs"][func_name].append(widget_name)

        self.refreshOptionMenu()

        del self.pop_win
        self.pop_win = False
    
    def pop_up_close(self):
        self.pop_win.top.destroy()
        self.pop_win = False
        self.editing_widget = False

    # Spawns PopUp Window to ask for widget parameters
    def getWidgetParameters(self, name):
        if self.pop_win:
            msgbox.showwarning("warning","Please close or confirm the previous Pop Up before opening another one.")
            return 0
        # Create the pop up window
        self.pop_win = PopUp(self.root, "Widget Creation : {}".format(name), self, self.placeWidget, name)
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
            self.pop_win.addInput("Entry", "StringVar Name", self.stringVars.keys())
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
                self.code["widget_position"][widg_name] = (x, y, w, h)
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

    def __init__(self, root, name, app, confirm_function, func_args = []):

        # Creating the PopUp window
        self.top = tk.Toplevel(root)
        self.top.title(name)
        self.top.geometry("750x450")

        self.app = app

        self.parent = root

        self.top.tk.call('wm', 'iconphoto', self.top._w, self.app.appicon)  

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
        lbl = tk.Label(self.top, text=name, relief="groove")
        lbl.place(relx=0, rely=0.1*self.n_inputs, relwidth=0.5, relheight=0.1)

        # Entry input for text
        if _type == "Entry":
            input_ = tk.Entry(self.top, textvariable = self.variables[name])
            # Adds the prohibited values if there are 
            self.prohibited_vals.update({name: arg})
        
        # Option menu to chose from multiple options
        elif _type == "OptionMenu":
            input_ = tk.OptionMenu(self.top, self.variables[name], "")
            input_.configure(relief="groove", indicatoron=0, image=self.app.arrowicon, compound="right")
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
    
    def setInputsValues(self, values):
        variable_names = list(self.variables.keys())

        for i, value in enumerate(values):
            self.variables[variable_names[i]].set(value)

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
        self.parent.unbind_all("<Return>")
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
            current_level_widget = widget_queue[0]
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
        
        if widget in self.code_data["standalones"]:
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
        
        self.addTemplate(template_name, **kwargs)

        

    def appendFunction(self, func):
        sorted_widgets = self.HierarchySort(self.code_data["funcs"][func])

        if func != "None":
            self.addTemplate("func", func=func)

        for widget in sorted_widgets:
            self.appendWidget(widget)

    

    def addTemplate(self, template, **kwargs):
        if template in CodeWritingController.TEMPLATE_ARGS.keys():
            args = self.getArgsFromTemplate(template, **kwargs)

            self.code += self.templates[template].format(*args)
        else:
            self.code += self.templates[template]

    def getArgsFromTemplate(self, template, **kwargs):
        
        args_names = CodeWritingController.TEMPLATE_ARGS[template]

        if "widget" in kwargs.keys():
            return self.getWidgetArgs(kwargs["widget"], args_names, kwargs["prop"] if "prop" in kwargs.keys() else False)
        
        else:
            return self.getMiscArgs(args_names, kwargs["func"] if "func" in kwargs.keys() else False)
    
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
                format_args.append(widget if "short" in args else self.formatName(widget))
            
            elif arg == "short":
                format_args.append(UIMaker.WIDGET_SHORTS[UIMaker.WIDGETS.index(widget_type)])

            elif arg == "widget":
                format_args.append(widget_type)
            
            elif arg == "parent":
                parent_name = self.findParentOf(widget)
                if parent_name == 'root' or parent_name in self.code_data["standalones"]:
                    parent_name = "self." + parent_name
                else:
                    parent_name = "self.window_widgets['{}']".format(parent_name)
                format_args.append(parent_name)
            
            elif arg == "x":
                format_args.append(widget_pos[2])
            
            elif arg == "y":
                format_args.append(widget_pos[3])
            
            elif arg == "w":
                format_args.append(widget_pos[0])
            
            elif arg == "h":
                format_args.append(widget_pos[1])

            elif arg == "var_name":
                format_args.append(self.code_data["optionMenuStringVars"][widget])

            elif arg == "options":
                format_args.append("'" + self.code_data["optionMenuVals"][widget] + "'")
            
            elif arg == "props_name":
                format_args.append(prop)
            
            elif arg == "props_value":
                if prop == "command":
                    format_args.append(self.getCommandArgs(widget))
                else:
                    format_args.append("self.assets_dict['{}']".format(self.code_data["images"][widget]))
            
            elif arg == "img_value":
                format_args.append("self.assets_dict['{}']".format(self.code_data["images"][widget]))

            elif arg == "cmd_value":
                format_args.append(self.getCommandArgs(widget))

        return format_args

    def findParentOf(self, widget):
        
        for parent in self.code_data["parents"]:
            if widget in self.code_data["parents"][parent]:
                return parent

    def getCommandArgs(self, widget):

        widget_to_lift = self.code_data["commands"][widget][0]
        
        if widget_to_lift in self.code_data["standalones"]:
            return "lambda: self.{}.lift()".format(widget_to_lift)
        else:
            return "lambda: self.window_widgets['{}'].lift()".format(widget_to_lift)

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
    


    

    
