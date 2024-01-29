from rest_framework import viewsets, permissions,status
from .models import *
from . serializer import *
from django.http import HttpResponse
from rest_framework.parsers import MultiPartParser,JSONParser
from .views import IsCustomerOrReadOnly
from .constants import *
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from .eyetest_utils import *
# from client.models import UserActivity
from api.views import IsAdminOrReadOnly
from django.db import connection
from .send_report import send_email_with_pdf
from . face_shape import get_user_face_shape
"""
Select Eye
"""

class SelectEye(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def post(self, request):
        eye_status = request.data.get("eye_status")
        test_id= request.data.get("test_id")
        test= request.data.get("test")
        if not eye_status:
            return Response(data={"message": "Eye Test fields are required", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        text_obj = get_test_obj(test_id)
 
        data_to_save = {
            "eye_status": eye_status,
            "test_of_user": request.user.id
        }
 
        if int(test_id) != 0:
            if not text_obj:
                return Response({"message": "Test not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = EyeTestSerializer(text_obj, data=data_to_save)
        else:    
            data_to_save = {
                "eye_status": eye_status,
                "test_of_user": request.user.id,
                "test": test
            }
            serializer = EyeTestSerializer(data=data_to_save)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Eye selected successfully","status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors,"status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        

"""
Show Question Api
"""
class ShowQuestion(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def get(self, request):
        all_display_texts = Question.objects.all()
        serializer =  QuestionSerializer(all_display_texts, many=True)
        return Response(data={"data": serializer.data, "message": "Question data get successfully" ,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
        
"""
Show Question Select Question and select test based on Question Api
"""
class SelectQuestions(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
 
    def post(self, request):
        request_data = request.data
        user_id = request.user.id
        selected_question_pks = request_data.get("selected_question", [])
 
        if not selected_question_pks:
            selected_question_pks = [1]
        try:
            selected_questions = Question.objects.all().filter(pk__in=selected_question_pks)
            # user_id = request.user.id
            #user_id = request_data.get('test_of_user')
            user = get_user(user_id)  
 
            if user is None:
                return Response(data={"message": "User not found", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
            
            selected_question_pks = sorted(selected_question_pks)
            
            if QUESTION_CONSTANT["FIVE"] not in selected_question_pks:

                data_to_save = {
                    "selected_question": selected_question_pks,
                    "test_of_user": user_id,
                }
            
                serializer = EyeTestSerializer(data=data_to_save)
                test, message = selete_test_behalf_of_question(selected_question_pks)  # Make sure this function is defined
 
                if serializer.is_valid():
                    if test:
                        serializer.validated_data["test"] = test
                        serializer.validated_data["selected_question"] = selected_questions
                        serializer.save()
                        return Response(data={"data": serializer.data, "message": "Operation Successfully", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
                    else:
                        return Response({"message": f"{message}", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
                else:
                    return Response(data={"error": serializer.errors, "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data={"message": "Please connect with a doctor!", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"error": str(e), "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)


"""
Myopia Snellen Fraction Api
"""
class GetSnellenFractionApi(APIView):
    permission_classes = [permissions.AllowAny,]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self, request):
        customer_auth_token = config('CUSTOMER_AUTH_TOKEN')
        provided_token = request.META.get('HTTP_AUTHORIZATION')
        if not provided_token:
            return Response({"error": "Authentication credentials were not provided."}, status=401)
        if provided_token != customer_auth_token:
            return Response({"error": "Invalid token"}, status=401)
        test_name = request.query_params.get('test_name')
        if test_name is None:
            return Response({"error": "Test Name parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)
        all_display_texts = SnellenFraction.objects.filter(test=test_name)
        serializer = SnellenFractionSizeSerializer(all_display_texts, many=True)

        return Response(data={"data": serializer.data, "message": "Snellenfraction get successfully" ,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


"""
Display Random text Api
"""
class DisplayRandomText(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def post(self, request):
        try:
            data = request.data
            Display_serializer = DisplayRandomTextSerializer(data=data)
            if not Display_serializer.is_valid():
                return Response({"message": "All Fields are Required" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
 
            test_id = Display_serializer.validated_data.get('test_id')
            action = Display_serializer.validated_data.get('action')
            vision_test = Display_serializer.validated_data.get('vision_test')
            snellen_fraction = Display_serializer.validated_data.get('snellen_fraction')
            test_obj = get_test_obj(test_id)
            print(test_obj)
            if test_obj is None:
                return Response({"message": "test object not found" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
            connection.schema_name = 'public'
            # ---------------------- geting text size here --------------------------->>>            
            text_size = 2*(get_text_size(vision_test, action, snellen_fraction,test_obj))
            # ------------------------------------------------------------------------>>>  
                     
            # ---------------------- geting random text here ------------------------->>>  
            random_item = get_random_text(vision_test, test_obj, snellen_fraction)

            connection.schema_name = 'default'
            # ------------------------------------------------------------------------>>>  
            # print(random_item,'hereeeeeeeeeeeeee')
            if random_item is not None:
                serializer_instance = NumberOfLetterInTextSerializer(random_item)
                test_serializer = EyeTestSerializer(test_obj)
                
                return Response({"data":{"random_text": serializer_instance.data['text'], "textSize":text_size,"test_object":test_serializer.data}, "message": "operation successfully" ,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
            return Response({"message":"Random text is not found" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_message = str(e)
            return Response({"error_message": error_message ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
 
"""
Myopia and Hyperopia and Presbyopia Test Api
"""
class MyopiaOrHyperopiaOrPresbyopiaTestApi(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def put(self, request):
        data = request.data
        test_id = data.get("test_id")
        snellen_fraction = data.get("snellen_fraction")
        vision_test = data.get("vision_test")

        data_to_save = {
                    "test_id": data.get("test_id"),
                    "test_of_user": request.user.id,
                    "snellen_fraction":data.get("snellen_fraction"),
                    "vision_test":data.get("vision_test"),
        }
 
        if not all([test_id, snellen_fraction]):
            return Response({"message": "All Fields are Required" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
 
        text_obj = get_test_obj(test_id)
        if text_obj is None:
            return Response({"message": "Text object is not found" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        serializer = create_test_serializer(text_obj, data_to_save)
 
        if serializer.is_valid():
            serializer = set_snellen_fraction_based_on_test(text_obj, snellen_fraction, serializer, vision_test)
            serializer.save()
            return Response({"data":serializer.data,"message": "Operation Successfully" ,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
        return Response({"error":serializer.errors,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
   
 
"""
Choose Astigmatism Api
"""
class ChooseAstigmatism(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def put(self, request):
        data = request.data
        test_id = data.get("test_id")
        choose_astigmatism = data.get("choose_astigmatism")

        data_to_save = {
                    "test_id": data.get("test_id"),
                    "test_of_user": request.user.id,
                    "choose_astigmatism":choose_astigmatism
        }
 
        if not all([test_id, choose_astigmatism]):
            return Response({"message": "All Fields are Required" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
 
        text_obj = get_test_obj(test_id)
        if text_obj is None:
            return Response({"message": "Text object is not found" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        serializer = create_test_serializer(text_obj, data_to_save)
 
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"message": "Operation Successfully" ,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
        return Response({"error":serializer.errors ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
 
 
"""
Get Degree Api
"""
class GetDegreeApi(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def get(self, request):
        test_id = request.query_params.get('test_id')
 
        if not all([test_id]):
            return Response({"message": "All Fields are Required" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
 
        text_obj = get_test_obj(test_id)
        if text_obj is None:
            return Response({"message": "Text Object is not Found" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
       
        degree = get_degree(text_obj)
        choose_astigmatism = text_obj.choose_astigmatism
         
        if  degree is not None:
            return Response({"data": degree, "choose_astigmatism":choose_astigmatism,"message": "Degrees Successfully" ,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)    
        return Response({"message": "Degree not Found" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
 
 
"""
Choose Degree Api
"""
class ChooseDegreeApi(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def put(self, request):
        data = request.data
        test_id = data.get("test_id")
        degree = int(data.get("degree", 0))
        data_to_save = {
                    "test_id": data.get("test_id"),
                    "test_of_user": request.user.id,
                    "degree":degree
        }

        if degree == 0:
            degree = 5
 
        if not all([test_id, degree]):
            return Response({"message": "All fields are required" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
 
        text_obj = get_test_obj(test_id)
        if text_obj is None:
            return Response({"message":"Test object is not found" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)    
 
        serializer = create_test_serializer(text_obj, data_to_save)
        if degree == 5:
            degree = 0
 
        if serializer.is_valid():
            if text_obj.eye_status == EYE_CHOICES[1][0]:
                degree = 180 - degree
            serializer.validated_data["degree"] = degree
            serializer.save()  
            return Response({"data":serializer.data, "message":"Operation Successfully" ,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)    
        return Response({"error":serializer.errors ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
 
 
"""
Choose Astigmatism Api
"""
class CYLTestApi(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def put(self, request):
        global counter 
        counter = 0
        data = request.data
        test_id = data.get("test_id")
        cyl_text_size= data.get("cyl_text_size")

        data_to_save = {
                    "test_id": data.get("test_id"),
                    "test_of_user": request.user.id,
                    "cyl_text_size":cyl_text_size
        }
 
        if not all([test_id, cyl_text_size]):
            return Response({"message": "All field are required" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
 
        test_obj = get_test_obj(test_id)
        if test_obj is None:
            return Response({"message": "Test object is not found" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)    
       
        serializer = create_test_serializer(test_obj, data_to_save)
        if not serializer.is_valid():
            return Response({"error":serializer.errors ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
         # ------- calculate report data Function---------------#
        # if test_obj.test == VISION_TEST_CHOICES[2][0]:
        #     test_obj = get_report_data_for_presbiyopia(test_obj)
        # else:
        # test_obj = get_report_data_for_myopia_and_hyperopia(test_obj)
        # test_obj.save()
        # ------- calculate report data---------------#
        return Response({"data": serializer.data,"message": "Operation Successfully" ,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)  
 
 
"""
Genrate Report Api
"""
class GetReportData(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def get(self, request):
        test_id = request.query_params.get('test_id')
        if not all([test_id]):
            return Response({"message": "All Fields are required" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
 
        test_obj = get_test_obj(test_id)
        if test_obj is None:
            return Response({"message": "Test object is not found" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        # # ------- calculate report data Function---------------#
        # if test_obj.test == VISION_TEST_CHOICES[2][0]:
        #     test_obj = get_report_data_for_presbiyopia(test_obj)
        # else:
        #     test_obj = get_report_data_for_myopia_and_hyperopia(test_obj)
        # test_obj.save()
        test_obj = get_report_data_for_myopia_and_hyperopia(test_obj)
        test_obj.save()
        # # ------- calculate report data---------------#
        user_id = request.user.id
        user_obj = test_obj.test_of_user
        tests = EyeTest.objects.filter( test_of_user__id=user_id, test=test_obj.test)
 
        eye_status = [test.eye_status for test in tests]
        if EYE_CHOICES[0][0] in eye_status and EYE_CHOICES[1][0] in eye_status:
            shape = get_user_face_shape(request.user.id)
            output = send_email_with_pdf(user_obj, tests, shape)

        context = {
            "test": EyeTestSerializer(tests, many=True).data,
            "full_name":request.user.full_name,
            "age":request.user.age,
            "shape":shape,
            "health_score":request.user.health_score,
            "client_website":request.user.company.official_website if request.user.company.official_website else ""
        }
        return Response({"data": context, "message": "Report generate Successfully" ,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
    

"""
Text To Speech Api
"""
class TextToSpeechApi(APIView):
    permission_classes = [permissions.AllowAny,]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self, request):
        customer_auth_token = config('CUSTOMER_AUTH_TOKEN')
        provided_token = request.META.get('HTTP_AUTHORIZATION')
        if not provided_token:
            return Response({"error": "Authentication credentials were not provided."}, status=401)
        if provided_token != customer_auth_token:
            return Response({"error": "Invalid token"}, status=401)
        text = request.query_params.get('text')
        language = int(request.query_params.get('language'))
        if not text:
            return Response({"message": "Text field is required", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        audio_content = text_to_speech(text, language)
        if audio_content:
            response = HttpResponse(audio_content, content_type="audio/mpeg")
            response["Content-Disposition"] = 'inline; filename="audio.mp3"'
            return response
        else:
            return Response({"message": "Something Went wrong.", "status": status.HTTP_500_INTERNAL_SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



 
"""
constant data insert in db from csv API
"""
class ConstantInsertDataInDB(APIView):
    def get(self, request):
        customer_auth_token = config('CUSTOMER_AUTH_TOKEN')
        provided_token = request.META.get('HTTP_AUTHORIZATION')
        if not provided_token:
            return Response({"error": "Authentication credentials were not provided."}, status=401)
        if provided_token != customer_auth_token:
            return Response({"error": "Invalid token"}, status=401)
        data = constant_data_insert_in_db_from_csv()
        crate_data_of_NumberOfLetterInText_model(data)
        crate_data_of_SnellenFraction_model(data)
        crate_data_of_PowerMapping_model(data)
        return Response({"data":data, "message": "Data insert Successfully" ,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
    

"""
Save To User feedback Api
"""
class UserFeedbackApi(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def post(self, request):
        user_feedback = request.data.get("user_feedback")
        user_id = request.user.id
        if not user_feedback:
            return Response({"message": "User feedback field is required", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        user_obj = get_user(user_id)
        if user_obj:
            user_obj.user_feedback = user_feedback
            user_obj.save()
            return Response({"message": "User feedback Save Successfully.", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)        
        return Response({"message": "User not found" ,"status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)



"""
Allready Seleted Eye Api
"""
class AllreadySeletedEye(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def get(self, request):
        test_id = request.query_params.get('test_id')
        if not test_id:
            return Response({"message": "Test ID field is required","status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
       
        test_obj = get_test_obj(test_id)
        if test_obj is None:
            return Response({"message": "Test object not found","status": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        eye_status = test_obj.eye_status
        return Response({"eye_status": eye_status, "message": "Operation Successfully", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK) 
    

# class TrackUserActivity(APIView):
#     permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
#     def post(self,request,*args,**kwargs):
#         if not UserActivity.objects.filter(created_by = request.user,page_url=request.data.get("url")):
#             UserActivity.objects.create(
#                 time = request.data.get("time"),
#                 page_url = request.data.get("url"),    
#                 created_by = request.user
#             )
#         else:
#             UserActivity.objects.filter(created_by = request.user,page_url=request.data.get("url")).update(time = request.data.get("time"))
        
#         start_time = UserActivity.objects.filter(created_by = request.user,page_url=request.data.get("url")).values_list("created_on")
#         end_time = UserActivity.objects.filter(created_by = request.user,page_url=request.data.get("url")).values_list("updated_on")
#         final_time = end_time-start_time
#         return Response({"time":final_time,"status":status.HTTP_200_OK})



class RandomWordTestApi(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def post(self, request):
        serializered_data = ReadingTestSerializer(data=request.data)
 
        if not serializered_data.is_valid():
            return Response({"error": serializered_data.errors, "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
 
        snellen_fraction = serializered_data.data.get("snellen_fraction")
        test_id = serializered_data.data.get("test_id")
 
        test_obj = get_test_obj(test_id)  
        if test_obj is None:
            return Response({"message": "Test object not found", "status": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
 
        word = get_random_word()
        connection.schema_name = 'public'  
        size = get_random_word_size(test_obj, snellen_fraction)
        connection.schema_name = 'default'
 
        if not (word and size):
            return Response({"message": "Word and Size not found", "status": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        return Response({"word": word, "size":size,"message": "Operation Successfully","status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
    




class GetSnellenFractionForRedGreenTestApi(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def get(self, request):
        test_id = request.query_params.get('test_id')
 
        if not test_id:
            return Response({"message": "Test id field is required", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
       
        test_obj = get_test_obj(test_id)  
        if test_obj is None:
            return Response({"message": "Test object not found", "status": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
       
        if test_obj.test == "myopia":
            snellen_fraction = test_obj.myopia_snellen_fraction
        else:
            snellen_fraction = test_obj.hyperopia_snellen_fraction
        connection.schema_name = 'public' 
        text_size = get_text_size_for_red_and_green(snellen_fraction, test_obj)
        connection.schema_name = 'default'
        return Response({"text_size":text_size, "snellen_fraction":snellen_fraction, "test":test_obj.test,"message": "Get Snellen Fraction and Size Successfully", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
    


class FindSnellenFractionAccordingRedAndGreenAction(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def post(self, request):
        global counter, first_action, second_action, third_action, first_snellen_fraction, second_snellen_fraction, third_snellen_fraction
        action = request.data.get("action")
        test_id = request.data.get("test_id")
        snellen_fraction = request.data.get("snellen_fraction")
 
        if not all([test_id, action]):
            return Response({"message": "All fields are required", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
       
        test_obj = get_test_obj(test_id)  
        if test_obj is None:
            return Response({"message": "Test object not found", "status": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        connection.schema_name = 'public'
        snellen_fraction = get_snellen_fraction_according_red_and_green_action(test_obj, snellen_fraction, action)
        random_text = get_random_text_for_red_and_green(test_obj, snellen_fraction)
        text_size = get_text_size_for_red_and_green(snellen_fraction, test_obj)
        connection.schema_name = 'default'

        if text_size > 15:
            random_text = random.choice(SINGLE_TEXT)
 
        if not (snellen_fraction and text_size):
            return Response({"message": "Not Found Text size and Snellen Faction", "status": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
       
        counter +=1
        if counter == 1:
            first_action = action
            first_snellen_fraction = snellen_fraction
        elif counter == 2:
            second_action = action
            second_snellen_fraction = snellen_fraction
        elif counter == 3:
            third_action = action
            third_snellen_fraction = snellen_fraction
 
        data ={
            "snellen_fraction":None,
            "text_size":text_size,
            "random_text":random_text,
            "counter":counter,
            "is_completed": None,
            "test_cancel": None,
            "phone_number":request.user.mobile_no,
            "domain_url":request.user.company.domain_url,
            "message": "Operation Successfully"
        }
        if counter == 1:
            data["snellen_fraction"] = first_snellen_fraction
            data["is_completed"] = False
            data["test_cancel"] = False
 
        elif counter == 2 and first_action != second_action:
            data["snellen_fraction"] = second_snellen_fraction
            data["is_completed"] = True
            data["test_cancel"] = False
 
        elif counter == 2 and first_action == second_action:
            data["snellen_fraction"] = second_snellen_fraction
            data["is_completed"] = False
            data["test_cancel"] = False
       
        elif counter == 3 and first_action == second_action == third_action:
            data["snellen_fraction"] = second_snellen_fraction
            data["is_completed"] = False
            data["test_cancel"] = True
 
        elif counter == 3 and (first_action == second_action) != third_action:
            data["snellen_fraction"] = third_snellen_fraction
            data["is_completed"] = True
            data["test_cancel"] = False
        else:
            return Response({"message": "Somthing Went Wrong", "status": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        return Response({"data":data, "message": "Red and Green data Update Successfully","status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
    


"""
Update Red And Green Test Api
"""
class UpdateRedAndGreenTestApi(APIView):

    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def put(self, request):
        snellen_fraction = request.data.get("snellen_fraction")
        test_id = request.data.get("test_id")
 
        if not all([test_id,snellen_fraction]):
            return Response({"message": "All field are required", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
       
        data_to_save = {
            "test_of_user": request.user.id,
            "is_completed": True
        }
 
        test_obj = get_test_obj(test_id)

        if test_obj is None:
            return Response({"message": "Test object not found", "status": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        serializered_data = create_test_serializer(test_obj, data_to_save)
        if serializered_data.is_valid():
            if test_obj.test == "myopia":
                serializered_data.validated_data["myopia_snellen_fraction"] = snellen_fraction
            if test_obj.test == "hyperopia":
                serializered_data.validated_data["hyperopia_snellen_fraction"] = snellen_fraction
            serializered_data.save()
            data = {
                "user_age":request.user.age,
                "data":serializered_data.data
            }
            test_obj = get_report_data_for_myopia_and_hyperopia(test_obj)
            test_obj.save()
            return Response({"data":data,"message": "Red and Green data Update Successfully","status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
        return Response({"error": serializered_data.errors, "status": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
    


"""
Reading Test Api for save SnellenFraction and get additional power
"""
class SaveReadingSnellenFractionTestApi(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def put(self, request):
        snellen_fraction = request.data.get("snellen_fraction")
        test_id = request.data.get("test_id")
 
        if not all([test_id, snellen_fraction]):
            return Response({"message": "All field are required", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
       
        data_to_save = {
            "reading_test_snellen_fraction": snellen_fraction,
            "test_of_user": request.user.id
        }
        addtion_power = HYPEROPIA_SNELLEN_DATA.get(snellen_fraction, 0)
        test_obj = get_test_obj(test_id)  
        if test_obj is None:
            return Response({"message": "Test object not found", "status": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
       
        serializered_data = create_test_serializer(test_obj, data_to_save)
        if serializered_data.is_valid():
            serializered_data.validated_data["age_power"] = addtion_power
            serializered_data.save()
            return Response({"data":serializered_data.data,"message": "Operation Successfully","status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
        return Response({"message": "Word not found", "status": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
    

"""
Counter Api
"""
class CounterApi(APIView):
    permission_classes = [permissions.AllowAny,]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self, request):
        customer_auth_token = config('CUSTOMER_AUTH_TOKEN')
        provided_token = request.META.get('HTTP_AUTHORIZATION')
        if not provided_token:
            return Response({"error": "Authentication credentials were not provided."}, status=401)
        if provided_token != customer_auth_token:
            return Response({"error": "Invalid token"}, status=401)
        global counter
        counter_value = int(request.query_params.get('counter_value'))
        counter = counter_value
        return Response({"message": "Counter is Zero" ,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
    


"""
Get Eye Data
"""
class GetEyeTestData(APIView):
    permission_classes = [permissions.AllowAny,]
    parser_classes = [MultiPartParser,JSONParser]

    def get(self,request,*args,**kwargs):
        try:
            test= EyeTest.objects.get(test_of_user=request.user)
        except:
            return Response({"message": "Test object not found", "status": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        
        data = {"id":test.id,"test":test.test}
        return Response({"data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


