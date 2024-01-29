from rest_framework.parsers import MultiPartParser,JSONParser
from django.core.files.base import ContentFile
from rest_framework import permissions,status
from rest_framework.response import Response
from rest_framework.views import APIView
from .views import IsCustomerOrReadOnly
from .models import EyeTest, User
from .serializer import *
from .constants import *
from .models import *
import numpy as np
import base64
import json
import cv2
 
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
 
def calculate_distance(frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5, minSize=(50, 50))
 
    if len(faces) > 0:
        average_face_width_cm = 16.0
        detected_face_width_px = faces[0][2]
        focal_length_px = 700.0
        estimated_distance_cm = (average_face_width_cm * focal_length_px) / detected_face_width_px
 
        left_eye_detected = False
        right_eye_detected = False
        detected_faces = []
 
        for (x, y, w, h) in faces:
            left_eye_region = gray_frame[y + int(h / 4):y + int(h / 2), x:x + int(w / 2)]
            right_eye_region = gray_frame[y + int(h / 4):y + int(h / 2), x + int(w / 2):x + w]
 
            left_eyes = eye_cascade.detectMultiScale(left_eye_region, scaleFactor=1.5, minNeighbors=2, minSize=(20, 20))
            right_eyes = eye_cascade.detectMultiScale(right_eye_region, scaleFactor=1.5, minNeighbors=2, minSize=(20, 20))
 
            if len(left_eyes) > 0:
                left_eye_detected = True
 
            if len(right_eyes) > 0:
                right_eye_detected = True
            detected_faces.append((x, y, w, h))        
               
        return {
            'distance': estimated_distance_cm,
            'left_eye_detected': left_eye_detected,
            'right_eye_detected': right_eye_detected,
            'faces': detected_faces
        }
    else:
        return {'error': 'No face detected'}
   
 
def save_original_frame(frame, user_id):
    try:
        user_obj = User.objects.get(id=user_id)
 
        if user_obj:
            _, image_buffer = cv2.imencode('.jpg', frame)
            image_data = image_buffer.tobytes()
 
            user_obj.user_image.save(f'{user_obj.mobile_no}.jpg', ContentFile(image_data))
            user_obj.save()
    except User.DoesNotExist:
        print(f"User with ID {user_id} does not exist.")
    except Exception as e:
        print(f"Error saving original frame: {e}")
 
 
class CalculateDistance(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    alert = "Get In Range"
 
    def get(self, request):
        return Response({'distance': None, 'message': 'No data available'}, status=status.HTTP_204_NO_CONTENT)
 
    def post(self, request):
        user_id = request.user.id
       
        user_image = User.objects.get(id = user_id).user_image
 
        try:
            json_data = json.loads(request.body.decode('utf-8'))
            frame_data = json_data.get('frameData')
            distance_type = request.data.get('test_distance')
 
            if frame_data:
                frame_bytes = base64.b64decode(frame_data.split(',')[1])
                frame_np = np.frombuffer(frame_bytes, dtype=np.uint8)
                frame = cv2.imdecode(frame_np, flags=cv2.IMREAD_COLOR)
 
                returned_data = calculate_distance(frame)
                distance = round(returned_data['distance'], 2)
 
                if 'error' in returned_data:
                    return Response({'error': returned_data['error'],"alert":"Get In Range","status":status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)    
               
               
                if distance is not None:
                    sixth_question = EyeTest.objects.filter(test_of_user__id=user_id, selected_question__id=2)
               
                    if distance_type == "fardistance" and sixth_question:
                        if distance < 40:
                            alert = "Move Back!"
                        elif distance > 50:
                            alert = "Move Closer!"
                        else:
                            alert = "Good to go"
                            if not user_image:
                                save_original_frame(frame, user_id)
                    elif distance_type == "fardistance":
                        if distance < 45:
                            alert = "Move Back!"
                        elif distance > 55:
                            alert = "Move Closer!"
                        else:
                            alert = "Good to go"
                            if not user_image:
                                save_original_frame(frame, user_id)
 
                    elif distance_type == "neardistance":
                        if distance < 25:
                            alert = "Move Back!"
                        elif distance > 35:
                            alert = "Move Closer!"
                        else:
                            alert = "Good to go"
                            if not user_image:
                                save_original_frame(frame, user_id)
 
                    return Response({"distance": distance, "alert": alert, "message": "Operation Successfully.", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Frame data not provided correctly', "alert": "Get In Range", "status": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'Frame data not provided correctly',"alert":"Get In Range","status":status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)    
        except Exception as e:
            return Response({'error': f"{e}", 'distance': None, "alert": "Get In Range", "status": status.HTTP_500_INTERNAL_SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)