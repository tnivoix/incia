from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib
import pandas as pd
import numpy as np
from scipy.stats import circmean

matplotlib.use("TkAgg", force=True)
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from spike2Fig import Spike2Fig
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
        
        width= self.winfo_screenwidth()
        height= self.winfo_screenheight()
        #setting tkinter window size
        self.geometry("%dx%d" % (width, height))

        self.frames = {}

        for F in (StartPage, Spike2Page, OneGraphPage, MeanGraphPage, MultipleGraphPage):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont, redirectPath=""):
        """
        Show the selected page.
        """
        frame = self.frames[cont]
        frame.tkraise()
        if redirectPath != "":
            frame.createGraph(redirectPath)


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
            text="One Graph Page",
            command=lambda: controller.show_frame(OneGraphPage),
            name="startPage_button_oneGraphPage",
        )
        button2.pack()

        button3 = ttk.Button(
            self,
            text="Mean Graph Page",
            command=lambda: controller.show_frame(MeanGraphPage),
            name="startPage_button_meanGraphPage",
        )
        button3.pack()

        button4 = ttk.Button(
            self,
            text="Display multiple graphs",
            command=lambda: controller.show_frame(MultipleGraphPage),
            name="startPage_button_multipleGraphPage",
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

        button5 = ttk.Button(
            f1,
            text="Compute Phases",
            command=lambda: self.computePhases(),
            name="spike2Page_button_computePhases",
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

    def computePhases(self):
        fileName = self.filename
        self.myFig.computePhases(fileName)

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
            self.children["spike2Page_frame1"].children[
                "spike2Page_button_computePhases"
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
        
        self.createGraph(filepath)

    def createGraph(self, filepath):
        name = filepath.split("/")[-1][:-4]
        self.circularGraph = CircularGraph(name)
        self.circularGraph.openTxtFile(filepath, name)
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
            text="Compute mean",
            command=lambda: self.computeMean(),
            name="meanGraphPage_button_computeMean",
        )
        button2.pack(side=tk.LEFT)
        """
        button2 = ttk.Button(
            f1,
            text="Open reference excel file",
            command=lambda: self.openReferenceFile(),
            name="meanGraphPage_button_openFile",
        )
        """
        button3 = ttk.Button(
            f1,
            text="Add Graph",
            command=lambda: self.addGraph(),
            name="meanGraphPage_button_addGraph",
        )
        button3.pack(side=tk.LEFT)
        f1.pack()
        f2.pack(side=tk.TOP)
        self.row = 0
        self.column = 0
        self.graphs = {}

        self.controller = controller

    def addGraph(self):
        filetypes = [("Text Document", "*.txt")]

        filepath = filedialog.askopenfilename(
            title="Open file", initialdir=".", filetypes=filetypes
        )
        name = filepath.split("/")[-1][:-4]
        graph = CircularGraph(name)
        graph.openTxtFile(filepath, name)
        graph.plotGraph()

        f = graph.fig

        canvas = FigureCanvasTkAgg(f, self.children["meanGraphPage_frame2"])
        canvas.draw()
        canvas.get_tk_widget().bind("<Button-3>", self.deleteGraph)
        canvas.get_tk_widget().config(width=300, height=300)
        canvas.get_tk_widget().grid(row=self.row, column=self.column)
        self.graphs[canvas.get_tk_widget().winfo_name()] = graph
        stats = tk.Frame(self.children["meanGraphPage_frame2"])
        for k, v in graph.stats.items():
            stat = tk.Label(stats, text="{} : {}".format(k, v))
            stat.pack(side="top")
        stats.grid(row=self.row+1, column=self.column)

        if self.column >=4:
            self.column = 0
            self.row += 2
        else:
            self.column += 1

    def deleteGraph(self, event):
        canvas = str(event.widget).split('.')[-1]
        frame = canvas.replace("canvas","frame")
        self.graphs.pop(canvas)
        self.children["meanGraphPage_frame2"].children[canvas].destroy()
        self.children["meanGraphPage_frame2"].children[frame].destroy()


    def computeMean(self):
        means = []
        for graph in self.graphs.values():
            mean = circmean(graph.data[graph.name])
            mean = np.rad2deg(mean) / 360
            means.append(mean)

        files = [("Text Document", "*.txt")]
        filename = filedialog.asksaveasfilename(filetypes=files, defaultextension=files)
        df = pd.DataFrame({"Time":[0]*len(means), "'S-S'_Phase": means})
        df.to_csv(filename, index=None, sep=" ", mode="a")

        self.controller.show_frame(OneGraphPage, filename)
       
class MultipleGraphPage(tk.Frame):
    """
    Page to do analysis.
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, name="multipleGraphPage")
        label = tk.Label(
            self, text="MultipleGraph Page", font=LARGE_FONT, name="multipleGraphPage_label"
        )
        label.pack(pady=10, padx=10)
        f1 = tk.Frame(self, name="multipleGraphPage_frame1")
        f2 = tk.Frame(self, name="multipleGraphPage_frame2")

        button1 = ttk.Button(
            f1,
            text="Back to Home",
            command=lambda: controller.show_frame(StartPage),
            name="multipleGraphPage_button_startPage",
        )
        button1.pack()

        button2 = ttk.Button(
            f1,
            text="Add graph",
            command=lambda: self.addGraph(),
            name="multipleGraphPage_button_addGraph",
        )
        button2.pack()
        f1.pack()
        f2.pack(side=tk.TOP)

    def addGraph(self):
        filetypes = [("Text Document", "*.txt")]

        filepath = filedialog.askopenfilename(
            title="Open file", initialdir=".", filetypes=filetypes
        )
        name = filepath.split("/")[-1][:-4]
        if "!canvas" not in self.children["multipleGraphPage_frame2"].children.keys():
            self.graph = CircularGraph(name)
        
        self.graph.openTxtFile(filepath, name)
        self.graph.plotGraph()

        if "!canvas" not in self.children["multipleGraphPage_frame2"].children.keys():
            f = self.graph.fig

            self.canvas = FigureCanvasTkAgg(f, self.children["multipleGraphPage_frame2"])
            
            self.canvas.get_tk_widget().config(width=500, height=500)
            self.canvas.get_tk_widget().pack(side=tk.TOP)

        self.canvas.draw()

if __name__ == "__main__":
    app = XenopeAnalyser()
    app.mainloop()
