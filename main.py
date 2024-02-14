import sys
from dsp import *
from lidar import *
from tcp_ip import *
from file_reader import *

import numpy as np
import math
from collections import deque
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import mean_absolute_error as mae
from sklearn.metrics import median_absolute_error as Mae
from collections import Counter
import csv
import matplotlib.pyplot as plt
###
### This is the main code for the LIDAR
### This visually plot rhe results
###
###
###
# For debugging, remove later
from debugger import Debugger
debugger = Debugger()
_dsp = DSP()
file_reader = FileReader()
dsp = file_reader.load_json("../settings/dsp.json")
comms = file_reader.load_json("../settings/communication.json")
msgs = file_reader.load_json("../settings/lidar_messages.json")

# Initiate LiDARs and PLC connection
lidarA_tcp = TCPClient(comms["lidarA IP"], comms["lidarA PORT"])
lidarB_tcp = TCPClient(comms["lidarB IP"], comms["lidarB PORT"])

stagecalibration = True
garr_ClibrationIndexA = []
garr_ClibrationIndexB = []
garr_ClibrationDistnace = []
gi_ADistance = 0
gi_AIndex = -1
garr_LoadedData = []
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1)
x_data = []
y_data = []
#scatter = ax.scatter(x_data, y_data)
def calculate_errors(LAD, LBD, LAA, LBA):
    # Calculate x error:
    LAA = LAA *3.14/180
    LBA = LBA *3.14/180 

    xA = math.cos(abs(LAA))*LAD
    xB = math.cos(abs(LBA))*LBD
    xDistance = (xB + xA)/2
    xError = xDistance - xB
 
    # Calculate y error:
    yA = -math.sin(LAA)*LAD
    yB = math.sin(LBA)*LBD
    yDistance = abs(yA - yB)/2

    if (yA <= 0 and yB <= 0):
        yError = -(yDistance + abs(max([yA, yB])))
        print("Type 1")

    elif (yA >= 0 and yB >= 0):
        yError = (yDistance + abs(min([yA, yB])))
        print("Type 2")

    elif (LAA > LBA and yA > yB):
        yError = yDistance - abs(min([yA, yB]))
        print("Type 3")

    elif (LAA < LBA and yA > yB):
        yError = yDistance - abs(min([yA, yB]))
        print("Type 4")

    else : 
        yError =(yDistance - abs(min([yA, yB])))
        print("Type 5")

    # Calculate roll error:
    aError = math.atan(((yA - yB)/2)/xDistance)*(360/(2*math.pi))

    # Outputs:
    #print(xDistance)
    #print(yDistance)

    print("X-Error:     ", xError*1000)
    print("Y-Error:     ", yError*1000)
    print("Angle-Error: ", aError)
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
def GetClosest(parr_Data):
    li_Index = -1
    C2 = 0
    Min = 99999
    for C1 in parr_Data:

        if (C1 < Min):
            Min = C1
            li_Index = C2
        C2 = C2 + 1
    return li_Index
def GetindextOfLargersDiffrence(parr_Data):
    li_Index = 0
    li_IndexStart = -1
    li_IndexEnd = -1
    lf_Diffrence = 0

    
    for C1 in range(0,len(parr_Data)-1):
        if (abs(parr_Data[C1] - parr_Data[C1 + 1]) > lf_Diffrence):
            if (parr_Data[C1] > parr_Data[C1 + 1]):
                lf_Diffrence = abs(parr_Data[C1] - parr_Data[C1 + 1])
                li_Index = C1+1
    return li_Index


def UpdatePlot(data, pi_Index, ax):
    y_data = data
    x_data = range(len(y_data))
    ax.cla()
    ax.scatter(x_data, y_data)

    ax.scatter(pi_Index,y_data[pi_Index], label='Data Points', color='black', zorder=2)
    #ax.set_xlim(0, len(x_data))  # Adjust the x-axis limits if needed
    #ax.set_ylim(min(y_data), max(y_data))  # Adjust the y-axis limits if needed
    fig.canvas.draw()
    plt.pause(1)

def CalibrateA():
    for C1 in range(dsp["calibration length"]):
        
        frames = lidarA_tcp.make_multiple_requests(
        msgs["poll telegram"], dsp["frames to average"])

        # Proccess data


        raw_data = read_data_from_frames(frames)
        raw_data = raw_data[45:]
        raw_data = raw_data[:-45]

        data = _dsp.exponential_moving_average(raw_data, dsp["exponential filter strength"])
        data = _dsp.moving_average(data)

        li_DistanceIndex = GetClosest(data)
        garr_ClibrationIndexA.append(li_DistanceIndex)

def CalibrateB():
    for C1 in range(dsp["calibration length"]):
        
        frames = lidarB_tcp.make_multiple_requests(
        msgs["poll telegram"], dsp["frames to average"])

        # Proccess data
        raw_data = read_data_from_frames(frames)
        raw_data = raw_data[45:]
        raw_data = raw_data[:-45]
        data = _dsp.exponential_moving_average(raw_data, dsp["exponential filter strength"])
        data = _dsp.moving_average(data)

        li_DistanceIndex = GetClosest(data)
        garr_ClibrationIndexB.append(li_DistanceIndex)

if __name__ == "__main__":


    def GetDistance(parr_Data, pf_Cutoff = 0):
        lf_Distance = np.inf
        li_DistanceIndext = -1
        li_StartIndex = -1
        li_EndIndex = -1

        li_WindowSize = dsp["detection windowsize"]

        lf_LargestError = 0
        for C1 in range(li_WindowSize,len(parr_Data)):
            li_X1 = C1 - li_WindowSize
            li_X2 = C1
            lf_Y1 = parr_Data[li_X1]
            lf_Y2 = parr_Data[li_X2]
            larr_Errors = []

            lf_Gradient = (lf_Y2 - lf_Y1)/(li_X2 - li_X1)
            lf_Offset = ((lf_Y1 - lf_Gradient*li_X1) + (lf_Y2 - lf_Gradient*li_X2))/2

            larr_YPredicted = list(map(lambda x: x*lf_Gradient + lf_Offset, list(range(li_X1,li_X2))))

            lf_Error = mse(parr_Data[li_X1:li_X2],larr_YPredicted)
            larr_Errors.append(lf_Error)

            if (lf_Error > lf_LargestError):
                lf_StandardError = np.array(list(map(lambda x,y: x - y, larr_YPredicted, parr_Data[li_X1:li_X2]))).mean()
                if (lf_StandardError > 0):
                    li_StartIndex = li_X1
                    li_EndIndex = li_X2
                    lf_LargestError = lf_Error
                    
        lf_Distance = parr_Data[li_StartIndex]
        li_DistanceIndext = li_StartIndex

        for C1 in range(li_StartIndex,li_EndIndex):
            if (lf_Distance > parr_Data[C1]):
                lf_Distance = parr_Data[C1]
                li_DistanceIndext = C1

        return li_DistanceIndext

    try:
        # Connect to LiDARs
        lidarA_tcp.connect()
        lidarB_tcp.connect()

        # Start LiDARs
        lidarA_tcp.send_message(msgs["start lidar"])
        lidarB_tcp.send_message(msgs["start lidar"])

        # Remove initial responses from buffers
        lidarA_tcp.receive_response()
        lidarB_tcp.receive_response()

    except: 
        # Close LiDAR connections
        lidarA_tcp.close_connection()
        lidarB_tcp.close_connection()

        sys.exit()
    print("Calabrating A")
    CalibrateA()

    print("Calabrating B")
    CalibrateB()
    lb_SavePlots = input("Should Plots Be Saved (y,n): ") == 'y'
    plt.show()
    while True:
        try:
            li_Count = 0
            for lidar_tcp in [lidarA_tcp, lidarB_tcp]:
                li_Count = li_Count + 1

                frames = lidar_tcp.make_multiple_requests(
                msgs["poll telegram"], dsp["frames to average"])

                # Proccess data
                raw_data = read_data_from_frames(frames)
                raw_data = raw_data[45:]
                
                # Remove 35 elements from the end
                raw_data = raw_data[:-45]
                if (lb_SavePlots):
                    if (li_Count % 2 == 1):
                        #debugger.save_array_to_txt(raw_data, 'Data/A_' + str(int(time.time() *1000)) + '.txt')
                        SaveArrayToCSV(raw_data, 'Data/A.csv')
                    else:
                        #debugger.save_array_to_txt(raw_data, 'Data/B_' + str(int(time.time() *1000)) + '.txt')
                        SaveArrayToCSV(raw_data, 'Data/B.csv')

                data = _dsp.exponential_moving_average(raw_data, dsp["exponential filter strength"])
                data = _dsp.moving_average(data)

                li_DistanceIndex = GetClosest(data)
                if (li_Count % 2 == 1):
                    gi_ADistance = data[li_DistanceIndex]
                    gi_AIndex = li_DistanceIndex
                    print("A Distance:", data[li_DistanceIndex]*1000)
                    print("A Change Angle:", round((sum(garr_ClibrationIndexA) / len(garr_ClibrationIndexA))-li_DistanceIndex))
                    UpdatePlot(data, li_DistanceIndex, ax1)
                else:
                    print("B Distance:", data[li_DistanceIndex]*1000)
                    print("B Change Angle:", round((sum(garr_ClibrationIndexB) / len(garr_ClibrationIndexB))-li_DistanceIndex))
                    UpdatePlot(data, li_DistanceIndex, ax2)
                    calculate_errors(gi_ADistance, data[li_DistanceIndex], round((sum(garr_ClibrationIndexA) / len(garr_ClibrationIndexA))-gi_AIndex),round((sum(garr_ClibrationIndexB) / len(garr_ClibrationIndexB))-li_DistanceIndex) )
                
                #debugger.plot([raw_data, data], ["raw data averaged", "filtered data"], most_common_element)
                

        except: break

    plt.ioff()
    plt.show()
