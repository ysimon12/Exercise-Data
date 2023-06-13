import cv2
import mediapipe as mp
import numpy as np
import json
import os
import csv
from collections import defaultdict

from .PoseTimeSeries.PoseEnum import BodyAngles, BodyPoints
from .PoseTimeSeries.PoseTimeSeries import PoseTimeSeries

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_holistic = mp.solutions.holistic


def getFeedbackFromCSV(name, path=os.path.dirname(os.path.abspath(__file__))):
    file_path = path + '/video_feedback.csv'
    with open(file_path, newline='') as f:
        reader = csv.reader(f)
        data = list(reader)
        for item in data:
            if item[0] == name or name in item[0]:
                return item[1]
    return None


def trainAllVideos(directory):
    all_timeseries = []
    for filename in os.listdir(directory):
        video_path = os.path.join(directory, filename)
        print('Working on {path}'.format(path=video_path))
        if 'bad' in filename:
            label = 'bad'
        else:
            label = 'good'
        results = getJointsAnglesForVideo(video_path)
        feedback = [getFeedbackFromCSV(filename[0:len(filename) - 4])]
        series = PoseTimeSeries(results[0], results[1], feedback=feedback, label=label, name=filename)
        all_timeseries.append(series)
        print(f'{filename} done'.format(filename=filename))
        print("===============")
    return all_timeseries


def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


def getJointsAnglesForVideo(videoName, generateVideo=False):
    mp_pose = mp.solutions.pose
    cap = cv2.VideoCapture(videoName)
    joints = defaultdict(list)
    angles = defaultdict(list)
    counter = 0
    total_counter = 0
    min_knee_angle = 360
    min_knee_angle_idx = 0
    skipped_frames_count = 0

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
    size = (width, height)
    font_scale = min(height,width) / 100
    height_scale = height / 10
    fourcc = None
    out = None
    if generateVideo:
        fourcc = cv2.VideoWriter_fourcc(*'VP90')
        out = cv2.VideoWriter(videoName[0:len(videoName) - 4] + '_skeleton.webm', fourcc, 20.0, size)
    with mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            success, image = cap.read()
            total_counter = total_counter + 1
            if not success:
                cap.release()
                break

            # Convert the BGR image to RGB.
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = True
            results = pose.process(image)
            if results.pose_landmarks == None:
                skipped_frames_count = skipped_frames_count + 1
                continue

            if generateVideo:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            landmarks = results.pose_landmarks.landmark

            left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
            right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
            left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
            right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
            left_heel = landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value]
            right_heel = landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value]
            left_foot_index = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value]
            right_foot_index = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value]

            hip_angle = 0
            knee_angle = 0
            heel_angle = 0

            # Check to see which leg is more visible so we can calculate angles better.
            if left_knee.visibility < right_knee.visibility:
                hip_angle = calculate_angle([right_shoulder.x, right_shoulder.y], [right_hip.x, right_hip.y],
                                            [right_knee.x, right_knee.y])
                knee_angle = calculate_angle([right_hip.x, right_hip.y], [right_knee.x, right_knee.y],
                                             [right_ankle.x, right_ankle.y])
                heel_angle = calculate_angle([right_ankle.x, right_ankle.y], [right_heel.x, right_heel.y],
                                             [right_foot_index.x, right_foot_index.y])
            else:
                hip_angle = calculate_angle([left_shoulder.x, left_shoulder.y], [left_hip.x, left_hip.y],
                                            [left_knee.x, left_knee.y])
                knee_angle = calculate_angle([left_hip.x, left_hip.y], [left_knee.x, left_knee.y],
                                             [left_ankle.x, right_ankle.y])
                heel_angle = calculate_angle([left_ankle.x, left_ankle.y], [left_heel.x, left_heel.y],
                                             [left_foot_index.x, right_foot_index.y])
            # We make sure that lowest knee angle can't be in the first 15 frames.
            # This is due to pose detection being wonky at times in the first few frames
            if total_counter > 15 and knee_angle <= min_knee_angle:
                min_knee_angle = knee_angle
                min_knee_angle_idx = counter

            joints[BodyPoints.left_shoulder.name].append(left_shoulder)
            joints[BodyPoints.right_shoulder.name].append(right_shoulder)
            joints[BodyPoints.left_hip.name].append(left_hip)
            joints[BodyPoints.right_hip.name].append(right_hip)
            joints[BodyPoints.left_knee.name].append(left_knee)
            joints[BodyPoints.right_knee.name].append(right_knee)
            joints[BodyPoints.left_ankle.name].append(left_ankle)
            joints[BodyPoints.right_ankle.name].append(right_ankle)
            joints[BodyPoints.left_heel.name].append(left_heel)
            joints[BodyPoints.right_heel.name].append(right_heel)
            joints[BodyPoints.left_foot_index.name].append(left_foot_index)
            joints[BodyPoints.right_foot_index.name].append(left_foot_index)

            angles[BodyAngles.hip_angle.name].append(hip_angle)
            angles[BodyAngles.knee_angle.name].append(knee_angle)
            angles[BodyAngles.heel_angle.name].append(heel_angle)

            if generateVideo:
                cv2.putText(image, f'Hip angle: {"{:.2f}".format(hip_angle)}', (10, int(height - (height_scale * 3))),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 196, 255), 3)
                cv2.putText(image, f'Knee angle: {"{:.2f}".format(knee_angle)}', (10, int(height - (height_scale * 2))),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 196, 255), 3)
                cv2.putText(image, f'Heel angle: {"{:.2f}".format(heel_angle)}', (10, int(height - height_scale)),
                            cv2.FONT_HERSHEY_PLAIN, 2, (0, 196, 255), 3)
                out.write(image)

            counter = counter + 1
    cap.release()
    cv2.destroyAllWindows()
    if generateVideo:
        out.release()
    # Leaving these print statements here for now. Was using for debugging purposes.
    # Will remove later on.
    # print('%d : %d', min_knee_angle, min_knee_angle_idx)
    # print('Skipped frames: {count}'.format(count=skipped_frames_count))
    # print('Total amount of frames in video {frame}'.format(frame=total_counter))
    # print('Amount of frames processed: {frame}'.format(frame=counter))

    # We only need the 60 frames before and after the lowest point in the squat
    left_bound = max(min_knee_angle_idx - 60, 0)
    right_bound = min(min_knee_angle_idx + 60, counter)
    for item in BodyPoints:
        joints[item.name] = joints[item.name][left_bound: right_bound]
    for item in BodyAngles:
        angles[item.name] = angles[item.name][left_bound: right_bound]

    # print('Amount of frames captured : {frames}'.format(frames=len(joints[BodyPoints.left_heel.name])))
    # print('Between frames [{left} : {right}'.format(left=left_bound, right=right_bound))

    return (joints, angles)


def writeToJSONFile(known, path=os.path.dirname(os.path.abspath(__file__))):
    file_path = path + '/train.json'
    data = []
    for obj in known:
        data.append(obj.toJSON())
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def readFromJSONFile():
    print(os.getcwd())
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    file_path = absolute_path + '/train.json'
    with open(file_path, "r") as f:
        data = json.load(f)
    known = []
    for x in data:
        y = PoseTimeSeries()
        y.data = x["data"]
        y.label = x["label"]
        y.name = x["name"]
        if y.feedback:
            y.feedback = y["feedback"]
        known.append(y)
    return known
