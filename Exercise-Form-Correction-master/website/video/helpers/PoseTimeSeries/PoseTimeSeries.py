from scipy import signal
import json
from collections import defaultdict


class PoseTimeSeries:
    def __init__(self, joint_data = {}, angle_data = {}, feedback= [], label="unknown", name = "unknown"):
        self.data = defaultdict(list)
        self.og_angles = angle_data
        self.label = label
        self.name = name
        self.feedback = feedback

        # Smooth time series data
        for key in joint_data:
            x_smooth = signal.savgol_filter([item.x for item in joint_data[key]], 11, 3)
            y_smooth = signal.savgol_filter([item.y for item in joint_data[key]], 11, 3)
            point_tuple = [(x_smooth[i], y_smooth[i]) for i in range(0, len(x_smooth))]
            self.data[key].extend(point_tuple)
        for key in angle_data:
            # Normalize time series and smooth out
            angle_normalized = [x / 180 for x in angle_data[key]]
            angle_smooth = signal.savgol_filter(angle_normalized, 11, 3)
            self.data[key].extend(angle_smooth)

    def setRawData(self, raw_data):
        self.raw_data = raw_data


    def __str__(self):
        # indent was 2
        return (json.dumps(self.data, default=str))

    def toJSON(self):
        dict1 = {}
        dict1["data"] = self.data
        dict1["label"] = self.label
        dict1["name"] = self.name
        dict1["feedback"] = self.feedback
        return dict1
