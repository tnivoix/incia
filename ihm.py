import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib

from interfaceModels import Spike2Figure
matplotlib.use('TkAgg', force=True)
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from spike2FigOld import Spike2Fig
from static import Side, Root


LARGE_FONT= ("Verdana", 12)


class XenopeAnalyser(tk.Tk):
    """
    Main class of the application. It will create the interface with all pages.
    """

    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default="./pictures/xenope.ico")
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
    """
    Page used to open, modify and save a spike2 file .smr.
    """

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

        button3 = ttk.Button(f1, text="Save file",
                            command=lambda: self.saveFile(), name="spike2Page_button_saveFile")
        
        for s in [e.name for e in Side]:
            for r in [e.name for e in Root]:
                name = "{}-{}".format(s,r)
                button = ttk.Button(f2, text=name,
                                command=lambda name=name: self.changeAxe(name), name="spike2Page_button_{}".format(name))
                button.pack(side=tk.LEFT)
        f1.pack()

    def saveFile(self):
        """
        Ask where to save the file and redirect to the Spike2Fig function.
        """
        files = [('Text Document', '*.txt')]
        filename = filedialog.asksaveasfilename(filetypes = files, defaultextension = files)
        self.myFig.saveDataInTxt(filename)

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
        filetypes = (('Data Files', '*.smr'),('All Files', '*.*'))

        filename = filedialog.askopenfilename(
            title='Open file',
            initialdir='.',
            filetypes=filetypes)

        self.myFig = Spike2Fig()
        self.myFig.getCleanData(filename)
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
            self.children["spike2Page_frame1"].children["spike2Page_button_saveFile"].pack(side=tk.LEFT)
            self.children["spike2Page_frame2"].pack()
        
        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        canvas.mpl_connect('pick_event', self.onpick)
        canvas.mpl_connect('button_press_event', self.onpress)
        canvas.mpl_connect('button_release_event', self.onrelease)

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
        label = tk.Label(self, text="Analysis Page", font=LARGE_FONT, name="analysisPage_label")
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage), name="analysisPage_button_startPage")
        button1.pack()

        button2 = ttk.Button(self, text="Do analysis",
                            command=lambda: self.doAnalysis(), name="analysisPage_button_doAnalysis")
        button2.pack()

    def doAnalysis(self):
        """
        TODO: Do analysis.
        """
        print("TODO: Do analysis")

class PageThree(tk.Frame):
    """
    TMP page to display hideable axes.
    """

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
        """
        Redirect to the Spike2Figure function
        """
        self.fig.showButton.onClicked(label)

if __name__ == "__main__":
    app = XenopeAnalyser()
    app.mainloop()