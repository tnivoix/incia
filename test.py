# Libs for data manipulation
import numpy as np
import pandas as pd

# Lib for graphs visualisation
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Libs for stats
from scipy.stats import circmean, circvar
from astropy.stats import rayleightest

# Lib for file explorer
import tkinter
from tkinter import filedialog

ROOTS = ["Rost", "Mid", "Caud"]
SIDE = ["L","R"]

def formatPhaseData(data):
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


def importPhaseFromSpike(fileName):
    data = []
    try:
        df = pd.read_csv(fileName, sep=" ")
        data = formatPhaseData(df)
    except FileNotFoundError:
        print("File not found.")
    except pd.errors.EmptyDataError:
        print("No data")
    return data
    
    


def printStats(name, angles):
    # Nb phases
    n = angles.shape[0]
    # Mean vector
    mean = circmean(angles)
    # Mean vector length
    r = 1 - circvar(angles)
    # Rayleigh test Z
    Z = n * r * r
    # Rayleigh test p
    p = rayleightest(angles)
    # Rao's spacing test U
    u = 0
    for i in range(n):
        t = 0
        if i == n - 1:
            t = 2 * np.pi - angles[i] + angles[0]
        else:
            t = angles[i + 1] - angles[i]
        u += abs(t - 2 * np.pi / n)
    u = 0.5 * u

    print("Name : {}".format(name))
    print("Number of observations : {}".format(n))
    print("Mean vector : {}".format(np.rad2deg(mean)))
    print("Length of mean vector : {}".format(r))
    print("Rayleigh test (Z) : {}".format(Z))
    print("Rayleigh test (p) : {}".format(p))
    print("Rao's spacing test (U) : {}".format(np.rad2deg(u)))


# Create the figure to display all graphs
def setupFigure(date, subject):
    nbRows = 2
    nbCols = 3

    fig = plt.figure(1, figsize=(nbCols*4,nbRows*3))
    i=1
    for row in range(nbRows):
        for col in range(nbCols):
            ax = fig.add_subplot(nbRows,nbCols,i, projection = 'polar')
            ax.set_theta_zero_location("N")  # theta=0 at the top
            ax.set_theta_direction(-1)  # theta increasing clockwise
            ax.set_yticklabels([])
            ax.set_rgrids([])
            ax.set_thetagrids([0,90,180,270],["0°","90°","180°","270°"])
            ax.set_ylim(0,1)
            if row == 0:
                ax.set_title(ROOTS[col])
            if col == 0:
                ax.set_ylabel("Side : {}".format(SIDE[row]), fontsize=20, rotation=0, labelpad=100)

            i += 1
    fig.suptitle("Date : {} / Subject : {}".format(date, subject))
    return fig


def displayOneGraph(ax, data, step):
    mean = circmean(data)

    r = 1 - circvar(data)

    ax.plot(data, [1] * data.shape[0], "o", label=step, color="blue")
    ax.quiver(mean, 0, 0, r, label=step, color="blue", angles="xy", scale=2)


def displayFigure(fig):
    # Create the legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(),loc='lower center', title='Steps', frameon=False)
    plt.tight_layout()
    plt.show()


"""
Folder template :
{date}-galv-{subject}-analyse

File template :
{date}-galv-{subject}_{step}-Phase Ev-GVS & MS-{side}-{root}- mode 'S-S'.txt
{date}-galv-{subject}_{step}_{stimu}-Phase Ev-GVS & MS-{side}-{root}- mode 'S-S'.txt
{date}-galv-{subject}_{step}-Phase Ev-GVS & MS-{side}-{root}- mode 'S-S'.txt
"""

def formatFileName(date, subject, step, side, root):
    file_name = "{date}-galv-{subject}_{step}-Phase Ev-GVS & MS-{side}-{root}- mode 'S-S'.txt".format(date=date,subject=subject,step=step,side=side,root=root)
    return file_name

def getOneExperiment(folder, date, subject, step):
    data = {}

    for side in SIDE:
        for root in ROOTS:
            tmp_file_name = formatFileName(date,subject,step,side,root)
            tmp_data = importPhaseFromSpike(folder+tmp_file_name)
            data[tmp_file_name] = tmp_data
    return data

def printOneExperimentStats(data):
    for name, item in data.items():
        printStats(name, item)
        print("")

def displayOneExperimentGraph(data, step):
    fig = setupFigure(date, subject)
    i=0
    j=0
    for value, subplot in zip(data.values(), fig.get_axes()):
        displayOneGraph(subplot, value, step)
        
        if j == 2:
            i += 1
            j = 0
        else:
            j += 1

    displayFigure(fig)

if __name__ == "__main__":
    date = "230407"
    subject = "s54"
    step = "000"
    folder = "Data_thomas/230407-galv-s54-analyse/"
    labels = [step]

    data = getOneExperiment(folder, date, subject, step)
    displayOneExperimentGraph(data, step)

"""
if __name__ == "__main__":
    date = "230407"
    subject = "s54"
    step = "000"
    folder = "Data_thomas/230407-galv-s54-analyse/"
    L_Caud_name = "230407-galv-s54_000-Phase Ev-GVS & MS-L-Caud- mode 'S-S'.txt"
    L_Mid_name = "230407-galv-s54_000-Phase Ev-GVS & MS-L-Mid- mode 'S-S'.txt"
    L_Rost_name = "230407-galv-s54_000-Phase Ev-GVS & MS-L-Rost- mode 'S-S'.txt"
    R_Caud_name = "230407-galv-s54_000-Phase Ev-GVS & MS-R-Caud- mode 'S-S'.txt"
    R_Mid_name = "230407-galv-s54_000-Phase Ev-GVS & MS-R-Mid- mode 'S-S'.txt"
    R_Rost_name = "230407-galv-s54_000-Phase Ev-GVS & MS-R-Rost- mode 'S-S'.txt"

    L_Caud = importPhaseFromSpike(folder + L_Caud_name)
    L_Mid = importPhaseFromSpike(folder + L_Mid_name)
    L_Rost = importPhaseFromSpike(folder + L_Rost_name)
    R_Caud = importPhaseFromSpike(folder + R_Caud_name)
    R_Mid = importPhaseFromSpike(folder + R_Mid_name)
    R_Rost = importPhaseFromSpike(folder + R_Rost_name)

    fig, axes = setupFigure(2, 3)

    printStats(L_Rost_name, L_Rost)
    print("")
    printStats(L_Mid_name, L_Mid)
    print("")
    printStats(L_Caud_name, L_Caud)
    print("")
    printStats(R_Rost_name, R_Rost)
    print("")
    printStats(R_Mid_name, R_Mid)
    print("")
    printStats(R_Caud_name, R_Caud)

    print(L_Mid)

    displayOneGraph(L_Rost_name, axes, 0, 0, L_Rost)
    displayOneGraph(L_Mid_name, axes, 0, 1, L_Mid)
    displayOneGraph(L_Caud_name, axes, 0, 2, L_Caud)
    displayOneGraph(R_Rost_name, axes, 1, 0, R_Rost)
    displayOneGraph(R_Mid_name, axes, 1, 1, R_Mid)
    displayOneGraph(R_Caud_name, axes, 1, 2, R_Caud)

    displayFigure()
"""