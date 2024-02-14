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
