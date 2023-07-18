# The code for changing pages was derived from: http://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
# License: http://creativecommons.org/licenses/by-sa/3.0/	

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
#from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk
from interfaceModels import *
from spike2Fig import *

from neo.io import Spike2IO


LARGE_FONT= ("Verdana", 12)


class XenopeAnalyser(tk.Tk):

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default="pictures/xenope.ico")
        tk.Tk.wm_title(self, "Xenope analyser")
        
        
        container = tk.Frame(self)
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
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button = ttk.Button(self, text="Open a Spike2 file",
                            command=lambda: controller.show_frame(Spike2Page))
        button.pack()

        button2 = ttk.Button(self, text="Do some analysis",
                            command=lambda: controller.show_frame(AnalysisPage))
        button2.pack()

        button3 = ttk.Button(self, text="Graph Page",
                            command=lambda: controller.show_frame(PageThree))
        button3.pack()

class Spike2Page(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Spike2 Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Open a file",
                            command=lambda: self.openSpike2File())
        button2.pack()

   

    def openSpike2File(self):
        filePath = "Data_thomas/230407-galv-s54-analyse/230407-galv-s54_000.smr"
        data = getDataFromSpike2(filePath)
        names = []
        for signals in data.analogsignals:
            names += signals.array_annotations["channel_names"].tolist()
        fig = Spike2Figure(len(names), names)

        i = 0
        for signals in data.analogsignals:
            for j in range(len(signals.array_annotations["channel_ids"])):
                fig.signals[names[i]].setData(signals.times.magnitude, signals[:,j].magnitude)
                fig.signals[names[i]].plot()
                i += 1

        f = fig.fig

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)



class AnalysisPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Analysis Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Do analysis",
                            command=lambda: self.doAnalysis())
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

        fig = Spike2Figure(3, ["Ax1", "Ax2", "Ax3"])
        x1 = np.array([0, 1, 2, 3])
        y1 = np.array([5, 2, 8, 6])
        fig.signals["Ax1"].setData(x1, y1)
        fig.signals["Ax1"].plot()
        
        x2 = np.array([0, 1, 2, 3])
        y2 = np.array([10, 2, 0, 12])
        fig.signals["Ax2"].setData(x2, y2)
        fig.signals["Ax2"].plot()
        
        x3 = np.array([0, 1, 2, 3])
        y3 = np.array([0, 3, 2, 19])
        fig.signals["Ax3"].setData(x3, y3)
        fig.signals["Ax3"].plot()

        f = fig.fig

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        

app = XenopeAnalyser()
app.mainloop()