import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tkinter import filedialog, messagebox
import tkinter as tk
import math
from tkinter import simpledialog
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Circle, PathPatch
import mpl_toolkits.mplot3d.art3d as art3d

###
### This does the plotting for the Micon and NOV excle files.
### Compilinf can be esaily doen with pyinstaller, nothing fancy reuerd
### Excel File Must Look Identical to the Micon_NOV file here (Only the Data sheets are needed, the naming and position is extreamly important, even sheet names) 
### DepthofDistanceOut is the variable which determines what dpeth to check the error at, this is not doen yet but is active
###
###
###
DepthofDistanceOut = 100
root = tk.Tk()
root.withdraw()  # Hide the root window
file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])

if (not(file_path)):
    messagebox.showerror("Error", f"Error loading and plotting the CSV file")
# Load your CSV data into a pandas DataFrame
xls = pd.ExcelFile(file_path)
sheet_names = xls.sheet_names

# Print the list of sheet names
hasMicon = False
hasNOV = False
for sheet_name in sheet_names:
    if ("NOV" in sheet_name):
        hasNOV = True
    if ("Micon" in sheet_name):
        hasMicon = True

if hasMicon and hasNOV:
    choice = simpledialog.askstring("Sheet Selection", "Both 'Micon' and 'NOV' sheets found. Choose one (Micon/NOV):", parent=root)

    hasNOV = False
    hasMicon = False
    if choice == "Micon":
        hasMicon = True
    elif choice == "NOV":
        hasNOV = True

    root.destroy()  # Close the dialog window
df = pd
if (hasMicon):
    df = pd.read_excel(file_path, sheet_name="Display Data (Micon)", header=1)
    numeric_columns = ['Depth', 'Northing Inclination', 'Easting Inclination']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
    df = df.dropna(subset=numeric_columns)
elif hasNOV:
    df = pd.read_excel(file_path, sheet_name="Display Data (NOV)", header=1)
    numeric_columns = ['Depth', 'Inclination', 'Azimuth']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
    df = df.dropna(subset=numeric_columns)
else:
    exit()
if (hasMicon):

    

    ##Calculations Start
    df['yInc'] = df['Northing Inclination'].abs().apply(math.sin) # I
    df['xInc'] = df['Easting Inclination'].abs().apply(math.sin) # J
    df['yDepth'] = df['Northing Inclination'].abs().apply(math.cos)# K
    df['xDepth'] = df['Easting Inclination'].abs().apply(math.cos)# L
    df['rInc'] = df.apply(lambda row: math.sqrt(row['yInc']**2 + row['xInc']**2), axis=1)# M
    df['xInc2'] = df.apply(lambda row: row['yInc'] / row['rInc'] if row['rInc'] != 0 else 0, axis=1)# N
    df['yInc2'] = df.apply(lambda row: row['xInc'] / row['rInc'] if row['rInc'] != 0 else 0, axis=1)# O
    df['yDepth2'] = df.apply(lambda row: row['yDepth'] / row['rInc'] if row['rInc'] != 0 else 0, axis=1)# P
    df['xDepth2'] = df.apply(lambda row: row['xDepth'] / row['rInc'] if row['rInc'] != 0 else 0, axis=1)# Q
    df['rInc2'] = df.apply(lambda row: math.sqrt(row['yInc2']**2 + row['xInc2']**2), axis=1)# R
    df['rIncDepth'] = df.apply(lambda row: math.sqrt(row['yDepth2']**2 + row['xDepth2']**2), axis=1)# S
    df['Azmuth First Quadrant'] = np.arctan2(df['yInc2'], df['xInc2'])# T
    df['Azmuth First Quadrant'].fillna(0, inplace=True)
    df['Inclination'] = np.where(df['rIncDepth'] == 0, 0, np.arctan(df['rInc2'] / df['rIncDepth']) * 180 / np.pi)# U

    def custom_function(row):
        if (row['Northing Inclination'] != 0) or (row['Easting Inclination'] != 0):
            if (np.sign(row['Easting Inclination']) >= 0) and (np.sign(row['Northing Inclination']) <= 0):
                return (np.pi - row['Azmuth First Quadrant']) * 180 / np.pi
            elif (np.sign(row['Easting Inclination']) <= 0) and (np.sign(row['Northing Inclination']) <= 0):
                return (np.pi + row['Azmuth First Quadrant']) * 180 / np.pi
            elif (np.sign(row['Easting Inclination']) <= 0) and (np.sign(row['Northing Inclination']) >= 0):
                return (np.pi * 2 - row['Azmuth First Quadrant']) * 180 / np.pi
            else:
                return row['Azmuth First Quadrant'] * 180 / np.pi
        else:
            return 0

    df['Azimuth'] = df.apply(custom_function, axis=1)# V
if (hasNOV or hasMicon):
    df['Rod Distance'] = df['Depth'].diff()# W
    df['Rod Distance'].iloc[0] = df['Rod Distance'].iloc[1]
    df['Northing First Quadrant'] = df['Rod Distance'] * np.sin(df['Inclination'] * np.pi / 180) * np.cos((-1 * (df['Azimuth'] + 90)) * np.pi / 180)# X
    df['Easting First Quadrant'] = df['Rod Distance'] * np.sin(df['Inclination'] * np.pi / 180) * np.sin((-1 * (df['Azimuth'] + 90)) * np.pi / 180)# Y
    df['True Depth'] = np.sqrt(np.power(df['Rod Distance'], 2) - np.power(df['Northing First Quadrant'], 2) - np.power(df['Easting First Quadrant'], 2))# Z

    df['True Depth Final'] = 0
    df['True Depth Final'].iloc[1] = df['Depth'].iloc[0]

    for i in range(2, len(df)):
        df['True Depth Final'].iloc[i] = df['True Depth Final'].iloc[i - 1] + df['True Depth'].iloc[i - 1]


    df['Northing Final'] = 0
    for i in range(2, len(df)):
        df['Northing Final'].iloc[i] = df['Northing Final'].iloc[i - 1] + df['Northing First Quadrant'].iloc[i - 1]

    df['Easting Final'] = 0
    for i in range(2, len(df)):
        df['Easting Final'].iloc[i] = df['Easting Final'].iloc[i - 1] + df['Easting First Quadrant'].iloc[i - 1]

    ##

z_values = df["True Depth Final"]
x_values = df["Easting Final"]
y_values = df["Northing Final"]
#print(len(z_values))

decimation_factor = 10  # Adjust this factor as needed
z_values = z_values[::decimation_factor]
x_values = x_values[::decimation_factor]
y_values = y_values[::decimation_factor]

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the points with specified colors
ax.plot(x_values, y_values, z_values)
radius = 0.5  # Radius of the cylinder
start_pos = np.array([df['Easting Final'].iloc[0], df['Northing Final'].iloc[0], df['True Depth Final'].iloc[0]])  # Starting position (x, y, z)
end_pos = np.array([df['End'].iloc[0], df['Unnamed: 3'].iloc[0], df['Unnamed: 4'].iloc[0]])    # Ending position (x, y, z)

axis = end_pos - start_pos

# Create points for the cylinder's surface
u = np.linspace(0, 2 * np.pi, 100)  # Create points along the circumference
z = np.linspace(0, 1, 100)  # Create points along the height (normalized)
U, Z = np.meshgrid(u, z)
X = start_pos[0] + radius * np.cos(U)
Y = start_pos[1] + radius * np.sin(U)
Z = start_pos[2] + Z * np.linalg.norm(axis)  # Scale the height by the length of the axis

#ax.plot_surface(X, Y, Z, alpha=0.5)

u = np.linspace(0, 2 * np.pi, 100)  # Create points along the circumference
z = np.linspace(0, 1, 100)  # Create points along the height (normalized)
U, Z = np.meshgrid(u, z)
X = start_pos[0] + radius * np.cos(U)
Y = start_pos[1] + radius * np.sin(U)
Z = start_pos[2] + Z * np.linalg.norm(axis)  # Scale the height by the length of the axis

for C1 in range(len(X)):
    X[C1] = X[C1] + end_pos[0]* C1/len(X)
    Y[C1] = Y[C1] + end_pos[1]* C1/len(X)


# Plot the cylinder's surface
ax.plot_surface(X, Y, Z, alpha=0.5)
df['MaxErrors'] = df.apply(lambda row: math.sqrt((row['Easting Final'] - end_pos[0])**2 + (row['Northing Final'] - end_pos[1])**2), axis=1)
MaxOut = df['MaxErrors'].max()
fig.text(0.00, 0.98, 'End Away: ' + str(math.sqrt((df['Easting Final'].iloc[-1] * df['Easting Final'].iloc[-1] - end_pos[0]*end_pos[0]) + (df['Northing Final'].iloc[-1] * df['Northing Final'].iloc[-1] - end_pos[1]*end_pos[1] ))),
        fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
fig.text(0.00, 0.90, 'Max Away: ' + str(MaxOut),
        fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
OutDistaceAtXDepth = -1
for C1 in range(len(df['MaxErrors'])):
    if (round(df['True Depth Final'].iloc[C1]) == round(DepthofDistanceOut)):
        OutDistaceAtXDepth = df['MaxErrors'].iloc[C1]
        break

fig.text(0.00, 0.82, 'Distance Away At ' + str(DepthofDistanceOut)  +  ' Depth: ' + str(OutDistaceAtXDepth),
        fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
# Customize the plot
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('')
ax.set_xlim(-25, 25)  # Replace x_min and x_max with your desired limits
ax.set_ylim(-25, 25) 
ax.invert_zaxis()
plt.tight_layout()
# Show the plot
plt.show()