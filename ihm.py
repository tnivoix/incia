# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/	

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib

from interfaceModels import Spike2Figure
matplotlib.use('TkAgg', force=True)
import tkinter as tk
from tkinter import ttk
from spike2Fig import Spike2Fig
from static import Side, Root


LARGE_FONT= ("Verdana", 12)


class XenopeAnalyser(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default="pictures/xenope.ico")
        tk.Tk.wm_title(self, "Xenope analyser")
        
        
        container = tk.Frame(self, name="application")
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, Spike2Page, AnalysisPage, PageThree):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

        
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent, name="startPage")
        label = tk.Label(self, text="Start Page", font=LARGE_FONT, name="startPage_label")
        label.pack(pady=10,padx=10)

        button = ttk.Button(self, text="Open a Spike2 file",
                            command=lambda: controller.show_frame(Spike2Page), name="startPage_button_spike2Page")
        button.pack()

        button2 = ttk.Button(self, text="Do some analysis",
                            command=lambda: controller.show_frame(AnalysisPage), name="startPage_button_analysisPage")
        button2.pack()

        button3 = ttk.Button(self, text="Graph Page",
                            command=lambda: controller.show_frame(PageThree), name="startPage_button_graphPage")
        button3.pack()

class Spike2Page(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, name="spike2Page")
        label = tk.Label(self, text="Spike2 Page", font=LARGE_FONT, name="spike2Page_label")
        label.pack(pady=10,padx=10)
        f1 = tk.Frame(self, name="spike2Page_frame1")
        f2 = tk.Frame(self, name="spike2Page_frame2")

        button1 = ttk.Button(f1, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage), name="spike2Page_button_startPage")
        button1.pack(side=tk.LEFT)

        button2 = ttk.Button(f1, text="Open a file",
                            command=lambda: self.openSpike2File(), name="spike2Page_button_openFile")
        button2.pack(side=tk.LEFT)

        for s in [e.name for e in Side]:
            for r in [e.name for e in Root]:
                name = "{}-{}".format(s,r)
                button = ttk.Button(f2, text=name,
                                command=lambda name=name: self.changeAxe(name), name="spike2Page_button_{}".format(name))
                button.pack(side=tk.LEFT)
        f1.pack()


    def changeAxe(self, name):
        self.myFig.plotSignal(self.myFig.ax2, name)
        self.myFig.fig.canvas.draw()

    def onpick(self, event):
        self.myFig.onpick(event)

    def onpress(self, event):
        self.myFig.onpress(event)

    def onrelease(self, event):
        self.myFig.onrelease(event)

    def openSpike2File(self):
        self.myFig = Spike2Fig()
        filePath = "Data_thomas/230407-galv-s54-analyse/230407-galv-s54_000.smr"
        self.myFig.getCleanData(filePath)
        self.myFig.getGVSStartsEnds()
        self.myFig.setupFig()
        
        self.children["spike2Page_frame2"].pack()

        f = self.myFig.fig

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        canvas.mpl_connect('pick_event', self.onpick)
        canvas.mpl_connect('button_press_event', self.onpress)
        canvas.mpl_connect('button_release_event', self.onrelease)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class AnalysisPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, name="analysisPage")
        label = tk.Label(self, text="Analysis Page", font=LARGE_FONT, name="analysisPage_label")
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage), name="analysisPage_button_startPage")
        button1.pack()

        button2 = ttk.Button(self, text="Do analysis",
                            command=lambda: self.doAnalysis(), name="analysisPage_button_doAnalysis")
        button2.pack()

    def doAnalysis(self):
        print("TODO: Do analysis")

class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Graph Page!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        self.fig = Spike2Figure(3, ["Ax1", "Ax2", "Ax3"])
        x1 = np.array([0, 1, 2, 3])
        y1 = np.array([5, 2, 8, 6])
        self.fig.signals["Ax1"].setData(x1, y1)
        self.fig.signals["Ax1"].plot()
        
        x2 = np.array([0, 1, 2, 3])
        y2 = np.array([10, 2, 0, 12])
        self.fig.signals["Ax2"].setData(x2, y2)
        self.fig.signals["Ax2"].plot()
        
        x3 = np.array([0, 1, 2, 3])
        y3 = np.array([0, 3, 2, 19])
        self.fig.signals["Ax3"].setData(x3, y3)
        self.fig.signals["Ax3"].plot()

        self.fig.showButton.p.on_clicked(self.on_clicked)

        f = self.fig.fig

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def on_clicked(self, label):
        self.fig.showButton.onClicked(label)

app = XenopeAnalyser()
app.mainloop()