# Libs for data manipulation
import numpy as np
import pandas as pd

# Lib for graphs visualisation
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Libs for stats
from scipy.stats import circmean, circvar
from astropy.stats import rayleightest

import os

import graph
from static import ROOT_FOLDER, Side, Root, Color


class Folder:
    def __init__(self, path, date, subject):
        self.path = path
        self.date = date
        self.subject = subject
        self.experiments = []
        self.setExperiments()

    def getExperienceNumber(self, fileName):
        before = "{date}-galv-{subject}_".format(date=self.date,subject=self.subject)
        number = fileName[len(before):len(before)+3]
        return number

    def getExperimentInfos(self):
        try:
            df = pd.read_excel(ROOT_FOLDER + "Angle-variation-toutes-racines.xlsx", sheet_name="Data", usecols="A:F")
            df = df.loc[df["Individu"]=="{date}-{subject}".format(date=self.date,subject=self.subject)]
            df = df.loc[df["Racine "]=="C"]
            df = df.reset_index(drop=True)
            return df
        except FileNotFoundError:
              print("File not found.")
        except pd.errors.EmptyDataError:
            print("No data")

    def setExperiments(self):
        numbers = []
        # List all files in a directory using scandir()
        with os.scandir(self.path) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith(".txt") and "Phase" in entry.name:
                    number = self.getExperienceNumber(entry.name)
                    if number not in numbers:
                        numbers.append(number)
        i = 0
        infos = self.getExperimentInfos()
        for number in numbers:
            experiment = Experiment(
                self, number, infos.iloc[i]["Localisation dépo drogue "], infos.iloc[i]["Drogue"], infos.iloc[i]["lésion "], Color(i).name
            )
            i += 1
            self.experiments.append(experiment)

    def displayFolderGraph(self):
        fig = graph.setupFigure(
            "Date : {} / Subject : {}".format(self.date, self.subject)
        )
        for e in self.experiments:
          graph.addAllGraphs(fig, e.getExperimentData(), "{} {}".format(e.drugName, e.drugLoc), e.color, True)
        graph.displayFigure(fig)

    def printFolderStats(self):
        for e in self.experiments:
            e.printExperimentStats()
            print("")


class Experiment:
    def __init__(self, folder, number, drugLoc, drugName, lesion, color):
        self.folder = folder
        self.number = number
        self.drugLoc = drugLoc
        self.drugName = drugName
        self.lesion = lesion
        self.color = color
        self.files = []
        self.setFiles()

    def setFiles(self):
        for side in Side:
            for root in Root:
                file = File(self, side.name, root.name)
                self.files.append(file)

    def setExperimentData(self):
        for file in self.files:
            file.setData()

    def getExperimentData(self):
        data = {}
        for file in self.files:
            data[file.getFileName()] = file.getData()
        return data

    def printExperimentStats(self):
        for file in self.files:
            file.printStats()
            print("")

    def displayExperimentGraph(self):
        fig = graph.setupFigure(
            "Date : {} / Subject : {}".format(self.folder.date, self.folder.subject)
        )
        graph.addAllGraphs(fig, self.getExperimentData(), "{} {}".format(self.drugName, self.drugLoc), self.color, False)
        graph.displayFigure(fig)


class File:
    def __init__(self, experiment, side, root):
        self.experiment = experiment
        self.side = side
        self.root = root
        self.data = []
        self.setData(False)

    def getFileName(self):
        file_name = "{date}-galv-{subject}_{step}-Phase Ev-GVS & MS-{side}-{root}- mode 'S-S'.txt".format(
            date=self.experiment.folder.date,
            subject=self.experiment.folder.subject,
            step=self.experiment.number,
            side=self.side,
            root=self.root,
        )
        return file_name
    
    def getFileNameBis(self, stim):
        file_name = "{date}-galv-{subject}_{step}_{stim}-Phase Ev-GVS & MS-{side}-{root}- mode 'S-S'.txt".format(
            date=self.experiment.folder.date,
            subject=self.experiment.folder.subject,
            step=self.experiment.number,
            stim=stim,
            side=self.side,
            root=self.root,
        )
        return file_name

    def formatPhaseData(self, data):
        phase_numbers = []
        phase_tmp = 1
        row_to_delete = []

        # Look at all phases
        for i in range(data.shape[0]):
            # Check if it's not the first value
            if i != 0:
                # Test if the actual phase time is far away for the previous one
                if data.iloc[i, 0] - data.iloc[i - 1, 0] > 10:
                    # Select the phase to deletion
                    row_to_delete.append(i)
                    # Change cycle
                    phase_tmp += 1
            # Write the cycle number in a tmp array
            phase_numbers.append(phase_tmp)

        # Add cycle number to all phases
        data["Phase_Number"] = phase_numbers

        # Remove useful data between phases
        data = data.drop(row_to_delete)

        # Change angles to degree
        data["'S-S'_Phase"] = data["'S-S'_Phase"] * 360

        # Keep only angles
        angles = np.deg2rad(data["'S-S'_Phase"]).sort_values().array

        return angles

    def setData(self, bis):
        try:
            if not bis:
              df = pd.read_csv(self.experiment.folder.path + "/" + self.getFileName(), sep=" ")
            else:
                df = pd.read_csv(self.experiment.folder.path + "/" + self.getFileNameBis("c"), sep=" ")
            self.data = self.formatPhaseData(df)
        except FileNotFoundError:
            if not bis:
                self.setData(True)
            else:
              print("File not found.")
        except pd.errors.EmptyDataError:
            print("No data")

    def getData(self):
        return self.data

    def printStats(self):
        # Nb phases
        n = len(self.data)
        # Mean vector
        mean = circmean(self.data)
        # Mean vector length
        r = 1 - circvar(self.data)
        # Rayleigh test Z
        Z = n * r * r
        # Rayleigh test p
        p = rayleightest(self.data)
        # Rao's spacing test U
        u = 0
        for i in range(n):
            t = 0
            if i == n - 1:
                t = 2 * np.pi - self.data[i] + self.data[0]
            else:
                t = self.data[i + 1] - self.data[i]
            u += abs(t - 2 * np.pi / n)
        u = 0.5 * u

        print("Name : {}".format(self.getFileName()))
        print("Number of observations : {}".format(n))
        print("Mean vector : {}".format(np.rad2deg(mean)))
        print("Length of mean vector : {}".format(r))
        print("Rayleigh test (Z) : {}".format(Z))
        print("Rayleigh test (p) : {}".format(p))
        print("Rao's spacing test (U) : {}".format(np.rad2deg(u)))
