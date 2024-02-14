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

# For debugging, remove later

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

if __name__ == "__main__": 
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
