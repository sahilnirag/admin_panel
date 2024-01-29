import numpy as np 
import cv2 
import dlib 
from sklearn.cluster import KMeans 
from .models import User
from django.conf import settings
import os
import math


face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# pixel_to_mm = 0.6  
pixel_to_mm = 0.55


def calculate_pupil_distance(landmarks):
    left_pupil = landmarks.part(36)
    right_pupil = landmarks.part(45)

    inter_pupil_distance_pixels = math.sqrt((right_pupil.x - left_pupil.x) ** 2 + (right_pupil.y - left_pupil.y) ** 2)

    inter_pupil_distance_mm = (inter_pupil_distance_pixels * pixel_to_mm) + 2
    
    return inter_pupil_distance_mm
 

def get_user_pupillary_distance (user_id):
    try:
        p_distance = "No Face Detected"
        user_obj = User.objects.get(id = user_id)
        # imagepath = str(user_obj.user_image)
        base_dir = settings.MEDIA_ROOT

        try:
            imagepath = os.path.join(base_dir, str(user_obj.user_image))
        except Exception as e:
            user_obj.p_distance = p_distance  
            user_obj.save()
            return p_distance

        image = cv2.imread(imagepath)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = face_detector(gray)

        for face in faces:
            landmarks = landmark_predictor(gray, face)
            eye_landmarks = [(landmarks.part(36).x, landmarks.part(36).y),
                             (landmarks.part(45).x, landmarks.part(45).y)]
            
            p_distance = round(calculate_pupil_distance(landmarks),2)
        
        user_obj.p_distance = p_distance  
        user_obj.save()
        return p_distance
    except Exception as e:
            p_distance = "No Face Detected"
            user_obj.p_distance = p_distance  
            user_obj.save()
            return p_distance


