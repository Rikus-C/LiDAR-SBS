import matplotlib.pyplot as plt
import numpy as np

class Debugger:

    def __init__(self):
        pass


            

    def plot(self, y_values_array, labels, pi_Index):
        plt.style.use('fivethirtyeight')
        x_values = np.arange(max(map(len, y_values_array)))  # Generating x values as a range of numbers
       
        # Plotting each set of y values
        for y_values, label in zip(y_values_array, labels):
            plt.plot(x_values[:len(y_values)], y_values, marker="o", linestyle="-", label=label)

        plt.scatter(pi_Index, y_values_array[0][pi_Index], label='Data Points', color='black', zorder=2)
        
        

        # Adding labels and title
        plt.xlabel("X values")
        plt.ylabel("Y values")
        plt.title("Value Plots")

        # Display the legend
        plt.legend()
        plt.tight_layout()

        # Show the plot
        plt.show()

    def plotLive(self, y_values_array, labels, pi_Index):
        x_values = np.arange(max(map(len, y_values_array)))  # Generating x values as a range of numbers
       
        # Plotting each set of y values
        for y_values, label in zip(y_values_array, labels):
            self.ax.plot(x_values[:len(y_values)], y_values, marker="o", linestyle="-", label=label)

        self.ax.scatter(pi_Index, y_values_array[0][pi_Index], label='Data Points', color='black', zorder=2)
        self.Fig.canvas.draw()

    def save_array_to_txt(self, array, file_path):
        with open(file_path, "w") as file:
            for item in array:
                file.write(str(item) + "\n")

    def read_array_from_txt(self, file_path):
        array = []
        with open(file_path, "r") as file:
            for line in file:
                # Remove leading and trailing whitespaces, then convert to the appropriate data type
                element = line.strip()
                try:
                    element = eval(element)  # Try to evaluate the string as a literal (e.g., int, float)
                except (NameError, SyntaxError):
                    pass  # If not a literal, keep it as a string
                array.append(element)
        return array

    def create_sliding_window_plot(self, width, height, offset):
        slide = []
        a = height/(width/2)**2
        for x in range(-width/2, width/2 + 1):
            slide.append(x*a + offset)
        return slide

    def SaveArrayToCSV(data, FileName):
        with open(FileName, mode='a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(data)

    def LoadArrayFromCSV(FileName):
        global garr_LoadedData

        with open(FileName, mode='r', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                garr_LoadedData.append(row)
