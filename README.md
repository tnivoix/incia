# User Manual

## Setup

First you need Python, you can download it from the official webpage : https://www.python.org/downloads/
When you install it, check the box that says "Add python.exe to PATH".

Then you need to install all requiered libraries. Start a Command Prompt ("Invite de commande") and run the command ` pip install -r C:\*path_to_application*\requirements.txt ` (Replace *path_to_application* by the current path. You can get it in properties of the requirements.txt file)

Then, to start the application, you need to run the command ` python xenopeAnalyser.py ` from a Command Prompt or double click on the file xenopeAnalyser.py (open with Python)

## Home Page

The home page just redirects to other pages.

## Spike2 Page

On this page, you can load a .smr file to see all signals and you can switch between them with the buttons. You can also export the file to .txt for an import in Spike2. You can also just save events that will be automaticly load in the application. Finaly, you can computes phases 'S-S' comparing the GVS with all others signals.

The program will load all signals and events with "MS-" in it. I use this patern to filter start event channels from other.

On each signals, you can click and drag events to move them, you can right on an event to delete it and you can middle click to add one. If you click upper the 0 on the Y axe, it's for start events and if it's under, it's for end events.

## One Graph Page

On this page, you can open a .txt file from Spike2 "Phase 'S-S'" to display the circular graph and statistics.

## Mean Graph Page

On this page, you add open multiple graphs the same way that the other page. You can right click on a graph to erase it. You can make the mean of all graph on screen and save it in a file. When you compute the mean, you will be redirect to the OneGrahPage to see the result graph.

## Multiple Graph Page

On this page you can display multiple graphs on the same graph.
