import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tkinter import filedialog, messagebox
import tkinter as tk
import math
import json

file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

if (not(file_path)):
    messagebox.showerror("Error", f"Error loading and plotting the CSV file")
# Load your CSV data into a pandas DataFrame
df = pd.read_csv(file_path)

numeric_columns = ['True Depth Final', 'Northing Final', 'Easting Final']
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

# Remove rows with NaN (missing) values in any of the numeric columns
df = df.dropna(subset=numeric_columns)


print(df.head())

z_values = df["True Depth Final"]
x_values = df["Easting Final"]
y_values = df["Northing Final"]
print(len(z_values))

decimation_factor = 1  # Adjust this factor as needed
z_values = z_values[::decimation_factor]
x_values = x_values[::decimation_factor]
y_values = y_values[::decimation_factor]

print(len(z_values))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the points with specified colors
ax.plot(x_values, y_values, z_values)

# Customize the plot
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('')
ax.set_xlim(-25, 25)  # Replace x_min and x_max with your desired limits
ax.set_ylim(-25, 25) 
plt.tight_layout()
# Show the plot
plt.show()