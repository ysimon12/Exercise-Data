import cv2
import mediapipe as mp
import time
import numpy as np
import os
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_holistic = mp.solutions.holistic


# Will collect joints for a video and edit video to show the hip and knee angle for each.

def calculate_angle(a, b, c):
  a = np.array(a)  # First
  b = np.array(b)  # Mid
  c = np.array(c)  # End

  radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
  angle = np.abs(radians * 180.0 / np.pi)

  if angle > 180.0:
    angle = 360 - angle

  return angle



cap = cv2.VideoCapture("1.mp4") #For Video input:
prevTime = 0
joints = []
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
size = (width, height)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('example.avi', fourcc, 20.0, size)
with mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as pose:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      break

    # Convert the BGR image to RGB.
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = pose.process(image)

    # Draw the pose annotation on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    mp_drawing.draw_landmarks(
        image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    landmarks = results.pose_landmarks.landmark

    joints.append(results.pose_landmarks)
    currTime = time.time()
    fps = 1 / (currTime - prevTime)
    prevTime = currTime

    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
    ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
             landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
    cv2.putText(image, f'Hip angle: {int(calculate_angle(shoulder,hip,knee))}', (10, 270), cv2.FONT_HERSHEY_PLAIN, 3, (0, 196, 255), 3)
    cv2.putText(image, f'Knee angle: {int(calculate_angle(hip,knee,ankle))}', (10, 350), cv2.FONT_HERSHEY_PLAIN, 3, (0, 196, 255), 3)
    out.write(image)
    cv2.imshow('BlazePose', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()
out.release()
cv2.destroyAllWindows()