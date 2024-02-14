import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tkinter import filedialog, messagebox
import tkinter as tk
import math
import json
###
### This does the plotting for Wikus's work
### Compilinf can be esaily doen with pyinstaller, nothing fancy reuerd
### A Jason File is needed for the Settings
### The file that needs to be selected in a csv File
###
###
###
# Open and read the JSON file
with open('Settings.json', 'r') as json_file:
    data = json.load(json_file)

# Access the float value by its key
MinThreshold = data['Min']
MaxThreshold = data['Max']

file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

if (not(file_path)):
    messagebox.showerror("Error", f"Error loading and plotting the CSV file")
# Load your CSV data into a pandas DataFrame
df = pd.read_csv(file_path)
z_values = df['Depth']
diameter_values = df['Diameter']

ZCount = 0
ZValue = 0
for C1 in range(len(z_values)):
    if C1 == 0:
        ZValue = z_values[C1]
    if ZValue == z_values[C1]:
        ZCount = ZCount + 1

AnglesCount = 2*math.pi/ZCount

# Extract x, y, and z values from the DataFrame
x_values = []
y_values = []

for C1 in range(len(diameter_values)):
    x_values.append((diameter_values[C1]/2) * math.cos(C1 * AnglesCount))
    y_values.append((diameter_values[C1]/2) * math.sin(C1 * AnglesCount))

data = {'X': x_values, 'Y': y_values, 'Z': z_values}

# Create a DataFrame from the dictionary
df = pd.DataFrame(data)

x_values = df['X']
y_values = df['Y']
z_values = df['Z']
# Define a threshold for coloring points
threshold = 3480  # Adjust this threshold as needed

# Calculate the distance of each point from the z-axis
distances = np.sqrt(x_values**2 + y_values**2)*2

# Create a list of colors based on the distance and threshold
colors = ['red' if ((d > MaxThreshold) or (d < MinThreshold))else 'gray' for d in distances]

# Create a 3D scatter plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the points with specified colors
ax.scatter(x_values, y_values, z_values, c=colors)

# Customize the plot
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('')
plt.tight_layout()
# Show the plot
plt.show()
