# Lib for file explorer

from tkinter import Tk, filedialog

import models

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
    while answer not in [1, 2]:
        print("Hello my friend, what do you want to do?")
        print("[1] Analyse one specimen (choose subfolder)")
        print("[2] Analyse all specimens (choose folder)")
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