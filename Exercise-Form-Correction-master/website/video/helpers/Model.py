import math
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from .PoseTimeSeries.PoseEnum import BodyAngles
from heapq import nsmallest

def knearest(input, known, n=3):
    distances = {}

    for timeseries in known:
        distance_sum = 0
        for key in timeseries.data:
            dist, _ = fastdtw(input.data[key], timeseries.data[key], dist=euclidean)
            distance_sum = distance_sum + dist

        distances[timeseries] = distance_sum

    nearest = nsmallest(n,distances, key=distances.get)

    return nearest

def checkDepth(input_series):
    feedback = []
    knee_angle = input_series.data[BodyAngles.knee_angle.name]
    min_angle = 180
    for item in knee_angle:
        curr = item * 180
        if curr < min_angle:
            min_angle = curr
    if min_angle >= 92:
        feedback.append("We detected your lowest knee angle to be {angle}. Try to go below 90 degrees(thighs parallel to floor).".format(angle=int(min_angle)))

    return feedback


