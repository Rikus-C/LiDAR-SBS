import numpy as np
from file_reader import FileReader

# Remove when in production
from debugger import Debugger
debugger = Debugger()

class DSP:
    def __init__ (self):
        file_reader = FileReader()
        self.dsp_const = file_reader.load_json("../settings/dsp.json")
        self.slide_width = self.dsp_const["sliding signal width"]
        self.slide_height = self.dsp_const["sliding signal height"]
        self.a = self.generate_sliding_signal(
            self.slide_width,
            self.slide_height)

    def butterworth_filter(self, data):
        n = self.dsp_const["butterworth order"]
        wc = self.dsp_const["butterworth cutoff"]
        fft = np.fft.fft(data)
        # debugger.plot([fft], ["butterworth before"])
        for s in range(1, len(fft)):
            fft[s] = fft[s]/(1 + (s/wc)**(2*n))
        # debugger.plot([fft], ["butterworth after"])
        return np.fft.ifft(fft)

    def fft_filter(self, data):
        p = self.dsp_const["fft cutoff %"]/100
        fft = np.fft.fft(data)
        # debugger.plot([fft], ["fft old"])
        for s in range(int(len(fft)*p), len(fft)): fft[s] = 0
        # debugger.plot([fft], ["fft new"])
        return np.fft.ifft(fft)

    def moving_average(self, data):
        new_data = []
        size = self.dsp_const["moving avg size"]
        for x in range(len(data)-size):
            new_data.append(sum(data[x:x+size])/size)
        return new_data

    def normalize_signal(self, com_data, new_data):
        d = min(new_data)
        nd = min(com_data)
        D = max(new_data) - d
        nD = max(com_data) - nd
        normalize_data = []
        for x in range(len(new_data)):
            p = new_data[x]
            Dper = (p - d)/D
            normalize_data.append(Dper*nD + nd)
        return normalize_data

    def generate_sliding_signal(self, width, height):
        return height/(width/2)**2

    def detect_plumb_line(self, signal):
        error = 9999
        position = 0
        for start in range(0, len(signal) - self.slide_width):
            temp = [] # remove later
            segment_error = 0
            segment_count = 0
            for x in range(-int(self.slide_width/2), int(self.slide_width/2)+1):
                temp.append(self.a*x**2 + signal[start + int(self.slide_width/2)]) # remove later
                segment_error += abs(self.a*x**2 + signal[start + int(self.slide_width/2)] - (signal[start + segment_count]))
                segment_count += 1
            if segment_error < error:
                error = segment_error
                position = start + int(self.slide_width/2)
            # debugger.plot([temp, signal], ["window", "signal"]) # remove later
        return position

    def remove_outliers(self, signal):
        new_signal = []
        for s in signal:
            if s < self.dsp_const["cutoff distance"]:
                new_signal.append(s)
            else: 
                new_signal.append(self.dsp_const["cutoff distance"])
        return new_signal 
    
    def exponential_moving_average(self, parr_Data, pf_Strength = 0.05):
        larr_NewSignal = []
        li_RuningValue = 0
        for C1 in parr_Data:
            li_RuningValue = C1 * (1 - pf_Strength) + (li_RuningValue * pf_Strength)
            larr_NewSignal.append(li_RuningValue)

        return larr_NewSignal

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


