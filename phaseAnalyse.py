# Lib for file explorer
import numpy as np
from tkinter import Tk, filedialog

import models
import graph
from static import Color

import os


def getDateAndSubjectFromFolder(name):
    date = name.split("/").pop()[:6]
    subject = name.split("/").pop().split("-")[2]
    return date, subject


def getAllFolders(path):
    folders = []
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                path = entry.path.replace("\\", "/")
                date, subject = getDateAndSubjectFromFolder(path)
                folder = models.Folder(path, date, subject)
                folders.append(folder)
    return folders


def menu():
    answer = 0
    while answer not in [1, 2, 3]:
        print("Hello my friend, what do you want to do?")
        print("[1] Analyse one specimen (choose subfolder)")
        print("[2] Analyse all specimens (choose folder)")
        print("[3] Analyse all specimens by type of experiment (choose folder)")
        answer = int(input())
    return answer


def askDirectory():
    root = Tk()
    root.withdraw()
    root.lift()
    root.focus_force()
    root.attributes("-topmost", True)
    directory = filedialog.askdirectory(parent=root)
    return directory

def displayMeansGraph(data, name, experiments):
    fig = graph.setupFigure(
        name
    )

    for i in range(3):
        graph.addAllGraphs(fig, data[i], experiments.split(" / ")[i], Color(i).name, True)
    graph.displayFigure(fig)

if __name__ == "__main__":
    choice = menu()
    directory = askDirectory()
    if choice == 1:
        path = directory.replace("\\", "/")
        date, subject = getDateAndSubjectFromFolder(path)
        folder = models.Folder(path, date, subject)
        folder.displayFolderGraph()
    elif choice == 2:
        folders = getAllFolders(directory)
        for folder in folders:
            folder.displayFolderGraph()
            print(folder.getMeans())
    elif choice == 3:
        folders = getAllFolders(directory)
        foldersByType = {}
        for folder in folders:
            type = folder.getType()
            if type not in foldersByType.keys():
                foldersByType[type] = []
            foldersByType[type].append(folder)
        for type in foldersByType.keys():
            nbFolders = len(foldersByType[type])
            newData = np.zeros((3,6,nbFolders))
            for folderNb in range(nbFolders):
                means = foldersByType[type][folderNb].getMeans()
                for experimentNb in range(3):
                    for graphNb in range(6):
                        newData[experimentNb,graphNb,folderNb] = means[experimentNb][graphNb]
            name = " / ".join(["{}-{}".format(f.date,f.subject) for f in foldersByType[type]])
            displayMeansGraph(newData, name, type)