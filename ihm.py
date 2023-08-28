import os
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib
import pandas as pd

from interfaceModels import Spike2Figure

matplotlib.use("TkAgg", force=True)
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from spike2FigOld import Spike2Fig
from static import Side, Root
from graph import CircularGraph


LARGE_FONT = ("Verdana", 12)


class XenopeAnalyser(tk.Tk):
    """
    Main class of the application. It will create the interface with all pages.
    """

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default="./pictures/xenope.ico")
        tk.Tk.wm_title(self, "Xenope analyser")

        container = tk.Frame(self, name="application")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, Spike2Page, AnalysisPage, OneGraphPage, MeanGraphPage):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        """
        Show the selected page.
        """
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):
    """
    Start page of the application the redirect to all other pages.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, name="startPage")
        label = tk.Label(
            self, text="Start Page", font=LARGE_FONT, name="startPage_label"
        )
        label.pack(pady=10, padx=10)

        button = ttk.Button(
            self,
            text="Open a Spike2 file",
            command=lambda: controller.show_frame(Spike2Page),
            name="startPage_button_spike2Page",
        )
        button.pack()

        button2 = ttk.Button(
            self,
            text="Do some analysis",
            command=lambda: controller.show_frame(AnalysisPage),
            name="startPage_button_analysisPage",
        )
        button2.pack()

        button3 = ttk.Button(
            self,
            text="One Graph Page",
            command=lambda: controller.show_frame(OneGraphPage),
            name="startPage_button_oneGraphPage",
        )
        button3.pack()

        button4 = ttk.Button(
            self,
            text="Mean Graph Page",
            command=lambda: controller.show_frame(MeanGraphPage),
            name="startPage_button_meanGraphPage",
        )
        button4.pack()


class Spike2Page(tk.Frame):
    """
    Page used to open, modify and save a spike2 file .smr.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, name="spike2Page")
        label = tk.Label(
            self, text="Spike2 Page", font=LARGE_FONT, name="spike2Page_label"
        )
        label.pack(pady=10, padx=10)
        f1 = tk.Frame(self, name="spike2Page_frame1")
        f2 = tk.Frame(self, name="spike2Page_frame2")

        button1 = ttk.Button(
            f1,
            text="Back to Home",
            command=lambda: controller.show_frame(StartPage),
            name="spike2Page_button_startPage",
        )
        button1.pack(side=tk.LEFT)

        button2 = ttk.Button(
            f1,
            text="Open a file",
            command=lambda: self.openSpike2File(),
            name="spike2Page_button_openFile",
        )
        button2.pack(side=tk.LEFT)

        button3 = ttk.Button(
            f1,
            text="Export file",
            command=lambda: self.exportFile(),
            name="spike2Page_button_exportFile",
        )

        button4 = ttk.Button(
            f1,
            text="Save events",
            command=lambda: self.saveEvents(),
            name="spike2Page_button_saveEvents",
        )

        for s in [e.name for e in Side]:
            for r in [e.name for e in Root]:
                name = "{}-{}".format(s, r)
                button = ttk.Button(
                    f2,
                    text=name,
                    command=lambda name=name: self.changeAxe(name),
                    name="spike2Page_button_{}".format(name),
                )
                button.pack(side=tk.LEFT)
        f1.pack()

    def exportFile(self):
        """
        Ask where to save the file and redirect to the Spike2Fig function.
        """
        files = [("Text Document", "*.txt")]
        filename = filedialog.asksaveasfilename(filetypes=files, defaultextension=files)
        self.myFig.exportDataInTxt(filename)

    def saveEvents(self):
        savefile = self.filename[:-4] + ".csv"
        self.myFig.saveEventsInCsv(savefile)

    def changeAxe(self, name):
        """
        Change the signal ploted on the second axe.
        """
        self.myFig.plotSignal(self.myFig.ax2, name)
        self.myFig.fig.canvas.draw()

    def onpick(self, event):
        """
        Redirect to the Spike2Fig function
        """
        self.myFig.onpick(event)

    def onpress(self, event):
        """
        Redirect to the Spike2Fig function
        """
        self.myFig.onpress(event)

    def onrelease(self, event):
        """
        Redirect to the Spike2Fig function
        """
        self.myFig.onrelease(event)

    def openSpike2File(self):
        """
        Ask the file .smr to open and create the Spike2Fig object.
        """
        filetypes = (("Data Files", "*.smr"), ("All Files", "*.*"))

        self.filename = filedialog.askopenfilename(
            title="Open file", initialdir=".", filetypes=filetypes
        )

        self.myFig = Spike2Fig()
        self.myFig.getCleanData(self.filename)
        self.myFig.setupFig()

        f = self.myFig.fig
        self.createCanvas(f)

    def createCanvas(self, f):
        """
        Create the canvas to display on the page.
        """
        if "spike2Page_canvas" in list(self.children.keys()):
            self.nametowidget("spike2Page_canvas").destroy()
            self.nametowidget("spike2Page_toolbar").destroy()
        else:
            self.children["spike2Page_frame1"].children[
                "spike2Page_button_exportFile"
            ].pack(side=tk.LEFT)
            self.children["spike2Page_frame1"].children[
                "spike2Page_button_saveEvents"
            ].pack(side=tk.LEFT)
            self.children["spike2Page_frame2"].pack()

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        canvas.mpl_connect("pick_event", self.onpick)
        canvas.mpl_connect("button_press_event", self.onpress)
        canvas.mpl_connect("button_release_event", self.onrelease)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        canvasName = canvas.get_tk_widget().winfo_name()
        toolbarName = toolbar.winfo_name()
        self.children["spike2Page_canvas"] = self.children.pop(canvasName)
        self.children["spike2Page_toolbar"] = self.children.pop(toolbarName)


class AnalysisPage(tk.Frame):
    """
    Page to do analysis.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, name="analysisPage")
        label = tk.Label(
            self, text="Analysis Page", font=LARGE_FONT, name="analysisPage_label"
        )
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(
            self,
            text="Back to Home",
            command=lambda: controller.show_frame(StartPage),
            name="analysisPage_button_startPage",
        )
        button1.pack()

        button2 = ttk.Button(
            self,
            text="Do analysis",
            command=lambda: self.doAnalysis(),
            name="analysisPage_button_doAnalysis",
        )
        button2.pack()

    def doAnalysis(self):
        """
        TODO: Do analysis.
        """
        print("TODO: Do analysis")


class OneGraphPage(tk.Frame):
    """
    TMP page to display hideable axes.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(
            self, text="One Graph Page!", font=LARGE_FONT, name="oneGraphPage_label"
        )
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(
            self,
            text="Back to Home",
            command=lambda: controller.show_frame(StartPage),
            name="oneGraphPage_button_startPage",
        )
        button1.pack()
        button2 = ttk.Button(
            self,
            text="Open txt file",
            command=lambda: self.openTxtFile(),
            name="oneGraphPage_button_openFile",
        )
        button2.pack()

    def openTxtFile(self):
        """
        Ask the .txt file to open.
        """
        filetypes = [("Text Document", "*.txt")]

        filepath = filedialog.askopenfilename(
            title="Open file", initialdir=".", filetypes=filetypes
        )

        self.circularGraph = CircularGraph(filepath.split("/")[-1][:-4])
        self.circularGraph.openTxtFile(filepath)
        self.circularGraph.plotGraph()

        if "oneGraphPage_canvas" in list(self.children.keys()):
            self.nametowidget("oneGraphPage_canvas").destroy()
            self.nametowidget("oneGraphPage_stats").destroy()

        f = self.circularGraph.fig

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side="left", fill=tk.BOTH, expand=True)

        canvasName = canvas.get_tk_widget().winfo_name()
        self.children["oneGraphPage_canvas"] = self.children.pop(canvasName)
        stats = tk.Frame(self, name="oneGraphPage_stats")
        for k, v in self.circularGraph.stats.items():
            stat = tk.Label(stats, text="{} : {}".format(k, v))
            stat.pack(side="top")
        stats.pack(side="right", fill=tk.BOTH, expand=True)


class MeanGraphPage(tk.Frame):
    """
    TMP page to display hideable axes.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(
            self, text="Mean Graph Page!", font=LARGE_FONT, name="meanGraphPage_label"
        )
        label.pack(pady=10, padx=10)
        f1 = tk.Frame(self, name="meanGraphPage_frame1")
        f2 = tk.Frame(self, name="meanGraphPage_frame2")
        button1 = ttk.Button(
            f1,
            text="Back to Home",
            command=lambda: controller.show_frame(StartPage),
            name="meanGraphPage_button_startPage",
        )
        button1.pack(side=tk.LEFT)
        button2 = ttk.Button(
            f1,
            text="Open reference excel file",
            command=lambda: self.openReferenceFile(),
            name="meanGraphPage_button_openFile",
        )
        button2.pack(side=tk.LEFT)
        f1.pack()

    def openReferenceFile(self):
        """
        Ask the .txt file to open.
        """
        filetypes = [("Excel files", ".xlsx .xls")]

        filepath = filedialog.askopenfilename(
            title="Open file", initialdir=".", filetypes=filetypes
        )

        self.getAllCases(filepath)

    def getAllCases(self, filepath):
        try:
            # ERROR HERE folder
            self.df = pd.read_excel(filepath, sheet_name="Data", usecols="A:F")
            column_headers = self.df.columns.values.tolist()
            new_headers = []
            for column_header in column_headers:
                self.df[column_header] = self.df[column_header].str.lower()
                new_headers.append(column_header.rstrip())
            self.df.columns = new_headers
            f2 = self.children["meanGraphPage_frame2"]
            self.drogues = self.df["Drogue"].unique().tolist()
            droguesList = ttk.Combobox(
                f2, values=self.drogues, name="meanGraphPage_droguesList"
            )
            droguesList.current(0)
            droguesList.pack(side=tk.LEFT)

            self.lesions = self.df["lésion"].unique().tolist()
            lesionsList = ttk.Combobox(
                f2, values=self.lesions, name="meanGraphPage_lesionsList"
            )
            lesionsList.current(0)
            lesionsList.pack(side=tk.LEFT)

            self.locs = self.df["Localisation dépo drogue"].unique().tolist()
            locsList = ttk.Combobox(f2, values=self.locs, name="meanGraphPage_locsList")
            locsList.current(0)
            locsList.pack(side=tk.LEFT)

            self.racines = self.df["Racine"].unique().tolist()
            racinesList = ttk.Combobox(
                f2, values=self.racines, name="meanGraphPage_racinesList"
            )
            racinesList.current(0)
            racinesList.pack(side=tk.LEFT)

            self.sides = ["L", "R"]
            sidesList = ttk.Combobox(
                f2, values=self.sides, name="meanGraphPage_sidesList"
            )
            sidesList.current(0)
            sidesList.pack(side=tk.LEFT)

            f2.pack()
            button = ttk.Button(
                self,
                text="Display those graph",
                command=lambda: self.displayAllGraphs(),
                name="meanGraphPage_button_displayAllGraphs",
            )
            button.pack()
        except FileNotFoundError:
            print("File not found.")
        except pd.errors.EmptyDataError:
            print("No data")

    def getSpecies(self, directory):
        drogue = (
            self.children["meanGraphPage_frame2"]
            .children["meanGraphPage_droguesList"]
            .get()
        )
        lesion = (
            self.children["meanGraphPage_frame2"]
            .children["meanGraphPage_lesionsList"]
            .get()
        )
        loc = (
            self.children["meanGraphPage_frame2"]
            .children["meanGraphPage_locsList"]
            .get()
        )
        racine = (
            self.children["meanGraphPage_frame2"]
            .children["meanGraphPage_racinesList"]
            .get()
        )
        side = (
            self.children["meanGraphPage_frame2"]
            .children["meanGraphPage_sidesList"]
            .get()
        )
        df = self.df
        df = df.loc[
            (df["Drogue"] == drogue)
            & (df["lésion"] == lesion)
            & (df["Localisation dépo drogue"] == loc)
            & (df["Racine"] == racine)
        ]

        species = list(df["Individu"])
        print(species)
        fileNames = []
        for s in species:
            df = df.loc[(df["Individu"] == s) & (df["Racine"] == racine)]
            i = 0
            for index, row in df.iterrows():
                if row["Drogue"] == drogue and row["lésion"] == lesion and row["Localisation dépo drogue"] == loc:
                    break
                i += 2
            folder = ""
            with os.scandir(directory) as entries:
                for entry in entries:
                    if entry.is_dir:
                        entry = entry.path
                        print(entry)
                        date, subject = s.split("-")
                        print(date, subject)
                        if date in entry and subject in entry:
                            folder = entry
                            break
            file = ""
            with os.scandir(folder) as entries:
                for entry in entries:
                    entry = entry.path
                    r = ""
                    if side == "c":
                        r = "Caud"
                    elif side == "r":
                        r = "Rost"
                    elif side == "m":
                        r = "Mid"
                    if side in entry and r in entry and "00{}".format(i) in entry:
                        file = entry
                        break
            fileNames.append(file)

        return fileNames
        

    def displayAllGraphs(self):
        directory = filedialog.askdirectory(title="Select the folder with all analyse folders")
        fileNames = self.getSpecies(directory)
        print(fileNames)
        
                    


if __name__ == "__main__":
    app = XenopeAnalyser()
    app.mainloop()
