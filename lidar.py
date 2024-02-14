from dsp import *
from file_reader import *

# For debugging, remove later
from debugger import Debugger
debugger = Debugger()

file_reader = FileReader()
dsp = file_reader.load_json("../settings/dsp.json")
comms = file_reader.load_json("../settings/communication.json")
msgs = file_reader.load_json("../settings/lidar_messages.json")
end_point = dsp["endpoint remove count"]

def calibrate_lidar(lidar):
    _dsp = DSP()

    # Get data from lidar
    frames = lidar.make_multiple_requests(
    msgs["poll telegram"], 200)

    # Proccess data
    raw_data = read_data_from_frames(frames)
    data = _dsp.moving_average(raw_data)
    # data = _dsp.fft_filter(data)
    # data = _dsp.butterworth_filter(data)
    data = _dsp.normalize_signal(raw_data, data)
    data = _dsp.remove_outliers(data)

    # For debugging, remove later
    debugger.plot([data], ["calibration measurements"])

    # Get final position readings
    angle = _dsp.detect_plumb_line(data)
    distance = raw_data[angle + dsp["phase shift"]]

    return angle, distance

def read_data_from_frames(raw_frames):
    raw_data = []
    frame_count = len(raw_frames)
    for c in range(26, len(raw_frames[0])-8):
        position_sum = 0
        for r in range(frame_count):
            position_sum += float.fromhex(raw_frames[r][c])
        raw_data.append((position_sum/frame_count)/1000)
    return raw_data[end_point:len(raw_data) - end_point]

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
