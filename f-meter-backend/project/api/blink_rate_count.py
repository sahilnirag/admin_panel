from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework import permissions, status
from rest_framework.response import Response
from scipy.spatial import distance as dist
from .models import EyeTest, User, Blink
from rest_framework.views import APIView
from .views import IsCustomerOrReadOnly
from imutils import face_utils
from .serializer import *
from .constants import *
from .models import *
import scipy.spatial
import numpy as np
import base64
import dlib
import json
import cv2



eye_aspect_ratio_threshold = 0.21
eye_aspect_ratio_consecutive_frames = 1

BLINK_COUNT = 0
COUNT = 0
first_time = True  
first_time_get_eye_blink_count = True

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']

def eye_aspect_ratio(eye):
    try:
        left_right = scipy.spatial.distance.euclidean(eye[0], eye[3])
        top_left = scipy.spatial.distance.euclidean(eye[1], eye[5])
        top_right = scipy.spatial.distance.euclidean(eye[2], eye[4])

        eyes_ratio = (top_left + top_right) / (2 * left_right)
        return eyes_ratio
    except Exception as e:
        print(f"Error in eye_aspect_ratio: {e}")
        return 0

def detect_blinks(frame):
    global BLINK_COUNT
    global COUNT
    global first_time

    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(grayscale)
    print(BLINK_COUNT,">>>>>>>>>>>>>>>>>")
    try:
        if first_time:
            # Set initial values
            BLINK_COUNT = 0
            COUNT = 0
            first_time = False  # Update the flag

        for face in faces:
            shape = predictor(grayscale, face)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]

            leftEyeAspectRatio = eye_aspect_ratio(leftEye)
            rightEyeAspectRatio = eye_aspect_ratio(rightEye)

            EyeAspectRatio_Average = (leftEyeAspectRatio + rightEyeAspectRatio) / 2

            if EyeAspectRatio_Average < eye_aspect_ratio_threshold:
                COUNT += 1
            else:
                if COUNT >= eye_aspect_ratio_consecutive_frames:
                    BLINK_COUNT += 1
                COUNT = 0
    except Exception as e:
        print(f"Error in detect_blinks: {e}")

    return BLINK_COUNT

def get_eye_blink_count(frame_data):
    global BLINK_COUNT
    global first_time_get_eye_blink_count
    try:
        if first_time_get_eye_blink_count:
            # Set initial values
            BLINK_COUNT = 0
            first_time_get_eye_blink_count = False  # Update the flag

        frame_np = np.frombuffer(frame_data, dtype=np.uint8)
        frame = cv2.imdecode(frame_np, flags=cv2.IMREAD_COLOR)

        if frame is not None:
            BLINK_COUNT = detect_blinks(frame)
            return BLINK_COUNT
        else:
            print("Error: Decoded frame is None.")
            return 0
    except Exception as e:
        print(f"Error in get_eye_blink_count: {e}")
        return 0
    
# ---------------------------   Eye Blink Rate ------------------>>>>>>>>>>>>

# Constants
EYE_CLOSED_THRESHOLD = 0.2
def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def calculate_blink_rate(EAR_VALUES, duration):
    num_blinks = len([ear for ear in EAR_VALUES if ear < EYE_CLOSED_THRESHOLD])
    blink_rate = num_blinks / duration
    return blink_rate

def get_eye_blink_rate(frame_data):
    try:
        frame_np = np.frombuffer(frame_data, dtype=np.uint8)
        frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 0)

        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            leftEye = shape[36:42]
            rightEye = shape[42:48]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0

            EAR_VALUES.append(ear)
            average_ear = np.mean(EAR_VALUES)

        return average_ear
    except Exception as e:
        print(f"Error in get_eye_blink_rate: {e}")
        return []
# --------------------------------------------------------------->>>>>>>>>>>




class CalculateBlinkCount(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self, request):
        return Response({'distance': None, 'message': 'No data available'}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request):
        print(type(request.query_params.get('new_user')),'data>>>>>>>>>>>>')
        global BLINK_COUNT
        
        try:
            user_obj = request.user
            flage = False
            json_data = json.loads(request.body.decode('utf-8'))
            frame_data = json_data.get('frameData')
            if request.query_params.get("new_user")=='yes':
                BLINK_COUNT = 0

            if frame_data:
                frame_bytes = base64.b64decode(frame_data.split(',')[1])
                blink_count = get_eye_blink_count(frame_bytes)

                ear_values = get_eye_blink_rate(frame_bytes)

                if (blink_count < 10 and ear_values < 0.20):
                    flage = True    
                elif (blink_count < 10 or ear_values < 0.20):
                    flage = True   

                try:
                    blink_obj = Blink.objects.get(user = user_obj)
                    blink_obj.blinks = blink_count
                    blink_obj.ear_values = ear_values
                    blink_obj.blink_status = flage
                    blink_obj.save()
                except:
                    user_obj = Blink.objects.create(
                    blinks = blink_count,
                    user = user_obj,
                    blink_status=flage
                    )
                return Response({"blink_count": blink_count,"new_user":"no","message": "Operation Successfully.", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Frame data not provided correctly','blink_count': None,"status":status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)    
        except Exception as e:
            return Response({'error': f"{e}", 'blink_count': None, "status":status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
