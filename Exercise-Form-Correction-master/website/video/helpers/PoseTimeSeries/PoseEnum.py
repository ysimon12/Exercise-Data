from enum import Enum


class BodyPoints(Enum):
    left_knee = 1
    right_knee = 2
    left_shoulder = 3
    right_shoulder = 4
    left_hip = 5
    right_hip = 6
    left_ankle = 7
    right_ankle = 8
    left_heel = 9
    right_heel = 10
    left_foot_index = 11
    right_foot_index = 12

    def __str__(self):
        return str(self.value)


class BodyAngles(Enum):
    hip_angle = 1
    knee_angle = 2
    heel_angle = 3

    def __str__(self):
        return str(self.value)
