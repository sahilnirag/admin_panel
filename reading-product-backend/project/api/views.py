from rest_framework.views import APIView 
import stripe
from api.models import *
from decouple import config
from api.serializer import *
from rest_framework import  permissions,status,viewsets,generics,filters
from rest_framework.parsers import JSONParser,MultiPartParser
from rest_framework.response import Response 
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate , logout,login
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied
from api.pagiation import *
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Case, When, CharField, Value, F, Q
from pyfcm import FCMNotification
from django_db_logger.models import StatusLog
from django.http import Http404
import logging
db_logger = logging.getLogger('db')
db_logger.info('info message')
db_logger.warning('warning message')

stripe.api_key = config("STRIPE_KEY")

from datetime import datetime, timedelta, date
from django.utils import timezone
import random
# Generate Token Manually
import re
import json
import uuid
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from tenant_schemas.utils import get_tenant_model, schema_context

def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role_id == SUPER_ADMIN:
            return True
        elif request.user.is_authenticated:
            raise PermissionDenied("You do not have permission to perform this action.")  # Use PermissionDenied from rest_framework.exceptions
        else:
            raise permissions.NotAuthenticated("Authentication is required to perform this action.")  # You can replace this with AuthenticationFailed if needed


class IsClientOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role_id == COMPANY:
            return True
        elif request.user.is_authenticated:
            raise PermissionDenied("You do not have permission to perform this action.")  # Use PermissionDenied from rest_framework.exceptions
        else:
            raise permissions.NotAuthenticated("Authentication is required to perform this action.")  # You can replace this with AuthenticationFailed if needed
        

class IsCustomerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role_id == CUSTOMER:
            return True
        elif request.user.is_authenticated:
            raise PermissionDenied("You do not have permission to perform this action.")  # Use PermissionDenied from rest_framework.exceptions
        else:
            raise permissions.NotAuthenticated("Authentication is required to perform this action.")  # You can replace this with AuthenticationFailed if needed
        

class IsAdminorClientOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role_id == COMPANY or request.user.role_id == SUPER_ADMIN:
            return True
        elif request.user.is_authenticated:
            raise PermissionDenied("You do not have permission to perform this action.")  # Use PermissionDenied from rest_framework.exceptions
        else:
            raise permissions.NotAuthenticated("Authentication is required to perform this action.")  # You can replace this with AuthenticationFailed if needed


class CustomerSignup(APIView):
    permission_classes = [permissions.AllowAny,]
    parser_classes = [MultiPartParser,JSONParser]
    
    def post(self,request,*args,**kwargs):
        if not request.data.get('first_name'):
            return Response({"message":"Please enter first name","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('last_name'):
            return Response({"message":"Please enter last name","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('email'):
            return Response({"message":"Please enter email","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('mobile_no'):
            return Response({"message":"Please enter mobile no","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('password'):
            return Response({"message":"Please enter password","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email = request.data.get('email')):
            return Response({"message":"There is already a registered user with this email","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(mobile_no = request.data.get('mobile_no')):
            return Response({"message":"There is already a registered user with this mobile no","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        user=User.objects.create(
            email = request.data.get('email'),
            first_name   = request.data.get('first_name'),
            last_name = request.data.get('last_name'),
            mobile_no = request.data.get('mobile_no'),
            role_id = CUSTOMER,
            password = make_password(request.data.get('password'))
            )
        data = UserSerializer(user,context={"request":request}).data
        return Response({"data":data,"messages":"Signup Successfully","status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class AddCustomer(APIView):
    parser_classes = [MultiPartParser,JSONParser]
    permission_classes = [permissions.AllowAny]
    def post(self,request,*args,**kwargs):
        if not request.data.get('age'):
            return Response({"message": "Please enter age", "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('email'):
            return Response({"message": "Please enter email", "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('name'):
            return Response({"message": "Please enter name", "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('domain_url'):
            return Response({"message": "Please enter domain URL", "status": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST)
        
        
        domain_url = request.data.get('domain_url')
        
        try:
            company_id = CompanyInformation.objects.get(domain_url=domain_url)
        except Exception as e:
           company_id  = None
        result = round(random.uniform(6, 7.5), 2)
        health_score = str(result)
        user = User.objects.create(full_name = request.data.get('name'),
                                age = request.data.get('age'),
                                email = request.data.get('email'),
                                role_id = CUSTOMER,
                                company=company_id,
                                uid=uuid.uuid4(),
                                health_score=health_score
                                )
        EyeTest.objects.create(test_of_user=user, eye_status='left', test='hyperopia')
        token = get_tokens_for_user(user)
        data = UserSerializer(user,context={"request":request}).data
        data.update({"token":token})
        return Response({"data":data,"messages":"Signup Successfully","status":status.HTTP_200_OK},status=status.HTTP_200_OK)
    

class GetCustomerRecord(APIView):
    def get(self, request):
        customer_auth_token = config('CUSTOMER_AUTH_TOKEN')
        provided_token = request.META.get('HTTP_AUTHORIZATION')
        if provided_token != customer_auth_token:
            return Response({"error": "Invalid token"}, status=401)
        # Choose a random record from the data
        random_record = random.choice(CUSTOMER_DATA)
        serializer = CustomerRecordSerializer(random_record)
        return Response(serializer.data)
    


class Login(APIView):
    parser_classes = [MultiPartParser,JSONParser]
    permission_classes = [permissions.AllowAny,]
    def post(self,request,*args,**kwargs):
        if not request.data.get('email'):
            return Response({"message":"Please enter email","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('password'):
            return Response({"message":"Please enter email","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username = request.data.get("email",None), password = request.data.get("password",None))
        if user:
            login(request,user)
            if request.user.role_id == CUSTOMER:
                raise PermissionDenied("You don't have permission to log in as this user.")
            token = get_tokens_for_user(user)
            data = UserSerializer(user,context={"request":request}).data
            data.update({"token":token})
            return Response({"data":data,"message":"Login Successfully","status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        else:
            return Response({"message":"Invalid Login Credentials","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)



class LogOut(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    parser_classes = [JSONParser]  # Use JSONParser
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")  # Use .get() to handle missing keys gracefully
            if not refresh_token:
                return Response({"message": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response({"message": "Logout Successfully", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class ChangePassword(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    parser_classes = [MultiPartParser,JSONParser]
    def post(self, request, *args, **kwargs):
            try:
                user = User.objects.get(id= request.user.id)
            except:
                return Response({"message": "User ot Found","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
            if user.check_password(request.data.get("current_password")) == False:
                return Response({"message": "Current Password Doesn't match","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 

            new_password = request.data.get("new_password", None)
            if not new_password:
                return Response({"message": "Please set new password","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 

            confirm_password = request.data.get("confirm_password", None)
            if not confirm_password:
                return Response({"message": "Please confirm your password","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 

            if new_password != confirm_password:
                return Response({"message":"Password did not match. Please try again! ","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
            else:
                user.password = make_password(request.data.get("new_password")) 
                user.save()
            return Response({"message": "Password updated successfully","status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


class AddReportIssue(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def post(self,request,*args,**kwargs):
        if not request.data.get('subject'):
            return Response({"message": "Subject cannot be empty","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        if not request.data.get('issue_description'):
            return Response({"message": "Description cannot be empty","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        report = ReportIssue.objects.create(
            email = request.user.email,
            subject = request.data.get('subject'),
            issue_description = request.data.get('issue_description'),
            created_by = request.user
            )
        schema_name =  request.user.company.schema_name
        with schema_context(schema_name):
            report.save()
        return Response({"message":"Report Added Successfully","status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        
class EnableDisableNotification(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    parser_classes = [MultiPartParser,JSONParser]
    def patch(self,request,*args,**kwargs):
        try:
            user = User.objects.get(id=request.user.id)
        except:
            return Response({"message": "User ot Found","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        if request.data.get('notification_status') =="1":
            user.notification_enable = True
            user.save()
            return Response({"message":"Notification enabled successfully","status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        elif request.data.get('notification_status') == "0":
            user.notification_enable = False
            user.save()
            return Response({"message":"Notification disabled successfully","status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        else:
            return Response({"message":"Sonething went wrong","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

class CreateNotification(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly,]
    parser_classes = [MultiPartParser,JSONParser]
    def post(self,request,*args,**kwargs):
        if not request.data.get('title'):
            return Response({"message": "Please enter title","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        if not request.data.get('description'):
            return Response({"message": "Please enter description","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        if not request.data.get('image'):
            return Response({"message": "Please select image","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        if Notification.objects.filter(title = request.data.get("title")):
            return Response({"message": "This notification already exist","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        Notification.objects.create(
            title = request.data.get("title"),
            description = request.data.get("description"),
            image = request.FILES.get("image"),
            created_by = request.user
            )
        return Response({"message":"Notification created successfully","status":status.HTTP_200_OK},status=status.HTTP_200_OK)

class AdminNotificationsList(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly,]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request,*args,**kwargs):
        notifications=Notification.objects.all().order_by("-created_on")
        start,end,meta_data = GetPagesData(request.query_params.get("page") if request.query_params.get("page") else None,notifications )
        data = NotificationSerializer(notifications[start:end], context = {"request":request},many =True).data 
        return Response({"data":data,"meta":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        
class DeleteNotification(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly,]
    parser_classes = [MultiPartParser,JSONParser]
    def delete(self,request,*args,**kwargs):
        try:
            notification = Notification.objects.get(id = request.data.get('notification_id'))
        except:
            return Response({"message": "Notification not found","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        notification.delete()
        return Response({"message": "Notification deleted successfully","status":status.HTTP_200_OK},status=status.HTTP_400_BAD_REQUEST) 



class UpdateNotification(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly,]
    parser_classes = [MultiPartParser,JSONParser]
    def put(self,request,*args,**kwargs):
        try:
            notification = Notification.objects.get(id = request.data.get('notification_id'))
        except:
            return Response({"message": "Notification not found","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        if Notification.objects.filter(title = request.data.get("title")).exclude(id = notification.id):
            return Response({"message": "This notification already exist","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
     
        if request.data.get('title'):
            notification.title = request.data.get('title')

        if request.data.get('description'):
            notification.description = request.data.get('description')

        if request.FILES.get('image'):
            notification.image = request.FILES.get('image')
        notification.save()
        return Response({"message":"Notification updated successfully","status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class NotificationDetails(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly,]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request,*args,**kwargs):
        try:
            notification = Notification.objects.get(id = request.query_params.get('notification_id'))
        except:
            return Response({"message": "Notification not found","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST) 
        data = NotificationSerializer(notification, context = {"request":request}).data 
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)

class SendNotification(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly,]
    parser_classes = [MultiPartParser,JSONParser]
    def post(self,request,*args,**kwargs):
        push_service = FCMNotification(api_key=config('FCM_KEY'))            
        device = Device.objects.get(created_by_id = request.user.id)
        msg = {
            "title":"",
            "description":"",
            
        }
        message_title = msg['title']
        message_body = msg['description']
        result = push_service.notify_single_device(
                    registration_id = device.device_token, 
                    message_title = message_title, 
                    message_body = message_body,
                    data_message={"message_title" :msg['title'],"message_body" : msg['description']
                })
        return Response({"message":"Notification sent successfully","status":status.HTTP_200_OK},status.HTTP_200_OK)



class ProductViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser,JSONParser]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminorClientOnly]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if Product.objects.filter(title = request.data.get('title')):
            return Response({"message":"This product already exists","status":status.HTTP_400_BAD_REQUEST},status.HTTP_400_BAD_REQUEST)
        else:
            return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if Product.objects.filter(title = request.data.get('title')).exclude(id = instance.id):
            return Response({"message":"This product already exists","status":status.HTTP_400_BAD_REQUEST},status.HTTP_400_BAD_REQUEST)
        else:
            return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Allow all users (authenticated or not) to read data
            return [permissions.IsAuthenticated()]
        return super().get_permissions()



class PlansCategoriesList(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request,*args,**kwargs):
        category =SubscriptionPlanCategory.objects.all().order_by("-created_on")
        start,end,meta_data = GetPagesData(request.query_params.get("page") if request.query_params.get("page") else None,category )
        data = PlanCategorySerializer(category[start:end],many =True).data
        return Response({"data":data,"meta":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
       
class AddPlansCategories(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def post(self,request,*args,**kwargs):
        if not request.data.get('title'):
            return Response({"message":"Please enter title","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if SubscriptionPlanCategory.objects.filter(title = request.data.get('title')):
            return Response({"message":"This Plan Category Already Exist","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        category =SubscriptionPlanCategory.objects.create(title = request.data.get('title'))
        data = PlanCategorySerializer(category,context={"request":request}).data
        return Response({"data":data,"message":"Plan Category Added Successfully","status":status.HTTP_200_OK},status.HTTP_200_OK)


class UpdatePlansCategories(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def patch(self,request,*args,**kwargs):
        try:
            category = SubscriptionPlanCategory.objects.get(id = request.data.get('category_id'))
        except:
             return Response({"message":"Plan Category does not exist","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if SubscriptionPlanCategory.objects.filter(title = request.data.get('title')).exclude(id=request.data.get('category_id')):
            return Response({"message":"This Plan Category Already Exist","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        
        if request.data.get('title'):
            category.title = request.data.get('title')
        category.save()
        data = PlanCategorySerializer(category,context={"request":request}).data
        return Response({"data":data,"message":"Plan Category updated Successfully","status":status.HTTP_200_OK},status.HTTP_200_OK)



class DeletePlansCategories(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def delete(self,request,*args,**kwargs):
        try:
            category = SubscriptionPlanCategory.objects.get(id = request.data.get('category_id'))
        except:
             return Response({"message":"Plan Category does not exist","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        category.delete()
        return Response({"message":"Plan Category deleted Successfully","status":status.HTTP_200_OK},status.HTTP_200_OK)



class AddPlans(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]

    def get_plan_categories(self):
        plan_categories = SubscriptionPlanCategory.objects.all()
        return [{'id': category.id, 'title': category.title} for category in plan_categories]

    def get_products(self):
        products = Product.objects.all()
        return [{'id': product.id, 'name': product.title} for product in products]

    def get(self, request, *args, **kwargs):
        plan_categories = self.get_plan_categories()
        products = self.get_products()

        response_data = {
            'plan_categories': plan_categories,
            'products': products,
        }
        return Response(response_data)

    def post(self, request, *args, **kwargs):
        try:
            plan_category_id = request.data.get('plan_type')
            plan_category = SubscriptionPlanCategory.objects.get(id=plan_category_id)
        except SubscriptionPlanCategory.DoesNotExist:
            return Response({"message": "Plan Category not found", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        if not request.data.get('title'):
            return Response({"message": "Please enter title", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('description'):
            return Response({"message": "Please enter description", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('subscription_plan_type'):
            return Response({"message": "Please enter Subscrition plan type", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('plan_type'):
            return Response({"message": "Please select plan type", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('sp_price'):
            return Response({"message": "Please enter SP Price", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get('paymod_type'):
            return Response({"message": "Please enter paymod type", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        
        if not request.data.get('start_date'):
            return Response({"message": "Please enter start date", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        
        if not request.data.get('expired_date'):
            return Response({"message": "Please enter expired date", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        
        allowed_plan_type = [subscription_plan_list for subscription_plan_list, _ in SUBSCRIPTION_PLAN]
        try:
            subscription_plan_type = int(request.data.get('subscription_plan_type'))
        except ValueError:
            return Response({"message": "Invalid subscription plan type format. It should be an integer", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        
        if subscription_plan_type not in allowed_plan_type:
            return Response({"message": "Invalid subscription plan type", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        
        allowed_paymod = [paymod_list for paymod_list, _ in PAYMOD]

        try:
            paymod_type = int(request.data.get('paymod_type'))
        except ValueError:
            return Response({"message": "Invalid paymod_type format. It should be an integer", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        

        if paymod_type not in allowed_paymod:
            return Response({"message": "Invalid paymod type", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        start_date = request.data.get('start_date')
        expired_date = request.data.get('expired_date')

        date_format = r'^\d{4}-\d{2}-\d{2}$'
        if start_date and not re.match(date_format, start_date):
            return Response({"message": "Invalid start date format. Date should be in 'YYYY-MM-DD' format", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        if expired_date and not re.match(date_format, expired_date):
            return Response({"message": "Invalid expired date format. Date should be in 'YYYY-MM-DD' format", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate start_date and end_date
        if start_date and expired_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            expired_date = datetime.strptime(expired_date, '%Y-%m-%d').date()

            date_difference = start_date + timedelta(days=30)
            # Calculate the difference between end_date and start_date

            # Check if the difference is exactly 1 month (31 days)
            if not expired_date > date_difference:
                return Response({"message": "Expired date should be 1 month after the start date", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
 

        # Assuming you have a list of product IDs in request.data['products']
        product_ids = request.data.get('products', [])
        products = Product.objects.filter(id__in=product_ids)

        if SubscriptionPlans.objects.filter(plan_category=plan_category).exists():
            return Response({"message": "Plan with selected category already exists", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        plans = SubscriptionPlans.objects.create(
            title=request.data.get('title'),
            description=request.data.get('description'),
            plan_category=plan_category,
            sp_price=request.data.get('sp_price'),
            subscription_plan_type=subscription_plan_type,
            paymod=paymod_type,
            start_date=start_date,
            expired_date=expired_date,
            created_by=request.user
        )
        plans.product.set(products)  # Add products to the many-to-many field

        data = SubscriptionPlanSerializer(plans, context={"request": request}).data
        return Response({"data": data, "message": "Plan Added Successfully", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)


class PlansList(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request,*args,**kwargs):
        plans = SubscriptionPlans.objects.all().order_by("-created_on")
        start,end,meta_data = GetPagesData(request.query_params.get("page") if request.query_params.get("page") else None,plans )
        data = SubscriptionPlanSerializer(plans[start:end],many =True).data
        return Response({"data":data,"meta":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
       

class UpdatePlan(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]

    def put(self, request, *args, **kwargs):
        try:
            plan_id = request.data.get('plan_id')  # Change 'paln_id' to 'plan_id'
            plan = SubscriptionPlans.objects.get(id=plan_id)
        except SubscriptionPlans.DoesNotExist:
            return Response({"message": "Plan not found", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('plan_type'):
            try:
                plan_category_id = request.data.get('plan_type')
                plan_category = SubscriptionPlanCategory.objects.get(id=plan_category_id)
            except SubscriptionPlanCategory.DoesNotExist:
                return Response({"message": "Plan Category not found", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            # Check if a plan with the same category exists, excluding the current plan
            if SubscriptionPlans.objects.filter(plan_category=plan_category).exclude(id=plan_id).exists():
                return Response({"message": "Plan with the selected category already exists", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        # Update plan fields if provided in request.data
        if request.data.get('title'):
            plan.title = request.data.get('title')

        if request.data.get('description'):
            plan.description = request.data.get('description')

        if request.data.get('sp_price'):
            plan.sp_price = request.data.get('sp_price')

        if request.data.get('plan_type'):
            plan.plan_category = plan_category

        if request.data.get('products'):
            # Assuming you have a list of product IDs in request.data['products']
            product_ids = request.data.get('products', [])
            products = Product.objects.filter(id__in=product_ids)
            plan.product.set(products)  # Update the many-to-many relationship
        
        start_date = request.data.get('start_date')
        expired_date = request.data.get('expired_date')

        date_format = r'^\d{4}-\d{2}-\d{2}$'
        if start_date and not re.match(date_format, start_date):
            return Response({"message": "Invalid start date format. Date should be in 'YYYY-MM-DD' format", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        if expired_date and not re.match(date_format, expired_date):
            return Response({"message": "Invalid expired date format. Date should be in 'YYYY-MM-DD' format", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        if start_date and expired_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            expired_date = datetime.strptime(expired_date, '%Y-%m-%d').date()

            date_difference = start_date + timedelta(days=30)
            # Calculate the difference between end_date and start_date

            # Check if the difference is exactly 1 month (31 days)
            if not expired_date > date_difference:
                return Response({"message": "Expired date should be 1 month after the start date", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
            plan.start_date = start_date
            plan.expired_date = expired_date
        plan.save()
        data = SubscriptionPlanSerializer(plan, context={"request": request}).data
        return Response({"data": data, "message": "Plan updated Successfully", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
    

class DeleteSubscriptionPlan(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def delete(self,request,*args,**kwargs):
        try:
            plan = SubscriptionPlans.objects.get(id = request.data.get('plan_id'))
        except:
             return Response({"message":"Plan does not exist","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        plan.delete()
        return Response({"message":"Plan deleted Successfully","status":status.HTTP_200_OK},status.HTTP_200_OK)


class UserInformationListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    queryset = User.objects.filter(role_id=CUSTOMER)  # Replace with the appropriate queryset for user details
    serializer_class = UserSerializer  # Replace with your user serializer class
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        # Add filter fields here if needed for user details
    }
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'mobile_no',
        'role_id',
        'notification_enable',
        'customer_id',
        'status',
        'company',
        'full_name'
        # Add other user detail fields here
    ]


class SendPasswordResetEmailView(APIView):
  permission_classes = [permissions.AllowAny,]
  parser_classes = [MultiPartParser,JSONParser]
  def post(self, request, format=None):
    serializer = SendPasswordResetEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)

class UserPasswordResetView(APIView):
  permission_classes = [permissions.AllowAny,]
  parser_classes = [MultiPartParser,JSONParser]
  def post(self, request, uid, token, format=None):
    serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)



class AdminDashboarddetails(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    def get(self, request):
        # Get the current date and calculate the start and end dates of the current month
        current_date = timezone.now()
        current_month_start = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month_start = (current_month_start + timezone.timedelta(days=31)).replace(day=1)

        response_data = {
            'status': 'Success',
            'data': {}
        }

        # Loop through all schemas
        all_tenants_data = []

        total_users = 0
        #total_clients = 0

        for tenant in CompanyInformation.objects.exclude(schema_name='public'):
            with schema_context(tenant.schema_name):
                # Get user statistics for the current tenant
                user_stats = User.objects.filter(
                    is_active=True,
                ).aggregate(
                    total_users=Count('id', filter=Q(role_id=CUSTOMER)),
                    total_active_users_this_month=Count('id', filter=Q(role_id=CUSTOMER) & Q(created_on__range=(current_month_start, next_month_start))),
                )

                total_users += user_stats['total_users']

                # Get the company__name_of_person, first names, and last names of users with role_id=2 created this month for the current tenant
                user_data = User.objects.filter(
                    Q(is_active=True, role_id=CUSTOMER, created_on__range=(current_month_start, next_month_start)) |
                    Q(is_active=True, role_id=COMPANY)
                ).values('full_name', 'company__name_of_person', 'role_id')

                formatted_data = {
                    'user_name': [],
                    'client_name': []
                }

                # Collect the data in a single loop
                for user in user_data:
                    if user['role_id'] == CUSTOMER:
                        formatted_data['user_name'].append(user['full_name'])
                    elif user['role_id'] == COMPANY:
                        if user['company__name_of_person']:
                            formatted_data['client_name'].append(user['company__name_of_person'])
                tenant_data = {
                    'tenant': tenant.name_of_person,
                }

                all_tenants_data.append(tenant_data)
        total_clients = CompanyInformation.objects.exclude(schema_name='public').count()
        # Add total user and client counts to the response data
        response_data['data']['total_users'] = total_users
        response_data['data']['total_client'] = total_clients

        response_data['data']['all_tenants_data'] = all_tenants_data

        return Response(response_data)
    

class ClientDashboardDetails(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    def get(self, request):
        current_date = timezone.now()
        current_month_start = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month_start = (current_month_start + timedelta(days=31)).replace(day=1)

        response_data = {
            'status': 'Success',
            'data': {}
        }

        user_stats = User.objects.filter(
            is_active=True
        ).aggregate(
            total_users=Count('id', filter=Q(role_id=CUSTOMER)),
            total_active_users_this_month=Count('id', filter=Q(role_id=CUSTOMER, created_on__range=(current_month_start, next_month_start)))
        )

        user_data = User.objects.filter(
            Q(is_active=True, role_id=CUSTOMER, created_on__range=(current_month_start, next_month_start))
        ).values('full_name', 'company__name_of_person', 'role_id')

        user_names = [user['full_name'] for user in user_data if user['role_id'] == CUSTOMER]

        response_data['data'].update(user_stats)
        response_data['data']['user_names'] = user_names

        return Response(response_data)



class UpdateAdminProfile(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def patch(self,request):
        try:
            user = User.objects.get(id = request.user.id)
        except:
            return Response({"message":"User not found","status":status.HTTP_400_BAD_REQUEST},status.HTTP_400_BAD_REQUEST)
        if request.data.get("first_name"):
            user.first_name = request.data.get("first_name")
        if request.data.get("last_name"):
            user.last_name= request.data.get("last_name")
        if request.data.get("mobile_no"):
            user.mobile_no = request.data.get("mobile_no")
        if request.FILES.get("profile_pic"):
            user.profile_pic = request.FILES.get("profile_pic")
        user.save()
        data = UserSerializer(user,context={"request":request}).data
        return Response({"data":data,"message":"Profile updated successfully","status":status.HTTP_200_OK},status.HTTP_200_OK)


class GetAdminProfile(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request):
        try:
            user = User.objects.get(id = request.user.id)
        except:
            return Response({"message":"User not found","status":status.HTTP_400_BAD_REQUEST},status.HTTP_400_BAD_REQUEST)
        data = UserSerializer(user,context={"request":request}).data
        return Response({"data":data,"message":"Profile updated successfully","status":status.HTTP_200_OK},status.HTTP_200_OK)



class DeleteUserAccount(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser,JSONParser]

    def delete(self,request,*args,**kwargs):
        try:
            user = User.objects.get(id= request.data.get("user_id"))
        except:
            return Response({"message":"User not found","status":status.HTTP_400_BAD_REQUEST},status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response({"message":"User deleted successfully","status":status.HTTP_200_OK},status.HTTP_200_OK)

class DeactivateUseraccount(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser,JSONParser]
    def put(self,request,*args,**kwargs):
        try:
            user = User.objects.get(id= request.data.get("user_id"))
        except:
            return Response({"message":"User not found","status":status.HTTP_400_BAD_REQUEST},status.HTTP_400_BAD_REQUEST)
        user.status == INACTIVE
        user.save()
        return Response({"message":"User account deactivated successfully","status":status.HTTP_200_OK},status.HTTP_200_OK)


class GetSubscriptionPlanCategoryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get_object(self, pk):
        try:
            return SubscriptionPlanCategory.objects.get(pk=pk)
        except SubscriptionPlanCategory.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        try:
            category = self.get_object(pk)
            serializer = PlanCategorySerializer(category)
            response_data = {
                'message': 'Category retrieved successfully',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Http404:
            response_data = {
                'message': 'Category not found'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        


class GetSubscriptionPlanAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get_object(self, pk):
        try:
            return SubscriptionPlans.objects.get(pk=pk)
        except SubscriptionPlans.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        try:
            category = self.get_object(pk)
            serializer = SubscriptionPlanSerializer(category)
            response_data = {
                'message': 'Plan retrieved successfully',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Http404:
            response_data = {
                'message': 'Plan not found'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        

class GetUserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        try:
            user = self.get_object(pk)
            serializer = UserSerializer(user)
            response_data = {
                'message': 'user data get successfully',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Http404:
            response_data = {
                'message': 'user not found'
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)



class ErrorLogsList(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request):
        logs = StatusLog.objects.all().order_by('-create_datetime')
        start,end,meta_data = GetPagesData(request.query_params.get("page") if request.query_params.get("page") else None,logs )
        data = LogsSerializer(logs[start:end],many =True).data
        return Response({"data":data,"meta":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
       

class ErroLogsDetails(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request):
        logs = StatusLog.objects.get(id = request.data.get("id"))
        data = LogsSerializer(logs,context={"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
       

class DeleteErrorLogs(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def delete(self,request):
        StatusLog.objects.all().delete()
        return Response({"message":"Logs Deleted Successfully","status":status.HTTP_200_OK},status=status.HTTP_200_OK)
    


class TransactionList(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request,*args,**kwargs):
        transactions = Transactions.objects.all().order_by("-created_on").only("id")
        start,end,meta_data = GetPagesData(request.query_params.get("page") if request.query_params.get("page") else None,transactions )
        data = TransactionSerializer(transactions[start:end],many =True).data
        return Response({"data":data,"meta":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
       

class TransactionsDetails(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request,*args,**kwargs):
        try:
            transactions = Transactions.objects.get(id =request.query_params.get("id"))
        except:
            return Response({"message":"Transaction Id Not Found","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        data = TransactionSerializer(transactions,context={"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
    


class CheckTokenExpiry(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        # Get the JWT token from the request
        jwt_token = request.auth

        # Get the expiration timestamp from the token's payload
        expiration_timestamp = jwt_token.payload.get('exp')

        # Get the current timestamp
        current_timestamp = datetime.timestamp(datetime.now())

        # Check if the token is expired
        if current_timestamp > expiration_timestamp:
            return Response({"message": "Token expired. Please log in again."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"message": "Token is valid."}, status=status.HTTP_200_OK)
    

class CreatePaymentIntent(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def post(self, request):
        serializer = PaymentIntentSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            amount = validated_data["amount"]
            name = validated_data["name"]
            email = validated_data["email"]
            address = validated_data["address"]

            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(amount),
                    currency="inr",
                    description=name,
                    receipt_email=email,
                    shipping={"name": name, "address": {"line1": address}}
                )
                return Response({"clientSecret": intent.client_secret, "paymentIntentId": intent.id})
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class AutometicPaymet(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def post(self, request):
        serializer = PaymentIntentSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            amount = validated_data["amount"]
            name = validated_data["name"]
            email = validated_data["email"]
            address = validated_data["address"]

            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(amount),
                    currency="inr",
                    description=name,
                    receipt_email=email,
                    shipping={"name": name, "address": {"line1": address}}
                )
                charges = stripe.Charge.list(payment_intent=intent.id)
                transaction = Transactions.objects.create(
                    amount = charges.amount,
                    currency = charges.currency,
                    receipt_url = charges.receipt_url,
                    transaction_id = charges.balance_transaction,
                    payment_status = charges.paid,
                    payment_type = PAYMENT,
                    created_by = request.user,
            )
                return Response({"meassage": "Plan Purchases", "status":status.HTTP_200_OK})
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetPaymentReceiptDetail(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def post(self, request):
        try:
            payment_intent_id = request.data.get('paymentIntentId')
            plan_id = request.data.get('plan_id')
            if not plan_id:
                return Response({'error': 'Plan ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not payment_intent_id:
                return Response({'error': 'PaymentIntent ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                plan_payment_id = SubscriptionPlans.objects.get(id=int(plan_id))
            except Exception as e:
                plan_payment_id = None
            # Retrieve the receipt URL from the PaymentIntent using Stripe API
            charges = stripe.Charge.list(payment_intent=payment_intent_id)
            if charges.data[0].status == 'succeeded':
                user_email = request.user.email
                customer_name = request.user.company.name_of_person
                company_name  = request.user.company.company_name
                plan_title = plan_payment_id.title
                plan_expired_date = plan_payment_id.expired_date
                sub_plan_type = plan_payment_id.subscription_plan_type
                plan_type  = next((name for type, name in SUBSCRIPTION_PLAN if type == sub_plan_type), None)
                
                body = f"""
                    Dear {customer_name},

                    We are thrilled to inform you that your payment has been successfully processed. Thank you for choosing our services.

                    Transaction ID: {charges.data[0].balance_transaction}

                    Amount Paid: {charges.data[0].amount}

                    You have subscribed to the "{plan_title}" plan. This is a {plan_type} plan, and it will expire on {plan_expired_date}.

                    If you have any questions or need further assistance, please do not hesitate to contact our support team.

                    Thank you for your business!

                    Sincerely,
                    {company_name}
                    """
                data = {
                    'subject': 'Payment Success',
                    'body': body,
                    'to_email': user_email,
                }
                Util.send_email(data)
            #payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            ## Save transaction when payment intent created 
            transaction = Transactions.objects.create(
                    amount = charges.data[0].amount,
                    currency = charges.data[0].currency,
                    receipt_url = charges.data[0].receipt_url,
                    transaction_id = charges.data[0].balance_transaction,
                    payment_status = charges.data[0].paid,
                    payment_type = PAYMENT,
                    created_by = request.user,
                    subscription = plan_payment_id
            )
            return Response({'receipt_data': charges})
        except stripe.error.StripeError as e:

            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny,]
    parser_classes = [MultiPartParser,JSONParser]
    def post(self, request): 
        try:
            payload = request.body
            event = None

            try:
                event = stripe.Event.construct_from(
                    json.loads(payload), stripe.api_key
                )
            except ValueError as e:
                # Invalid payload
                return Response({"message": "Invalid payload"}, status=400)
            if event.type == 'payment_intent.succeeded':
                return Response({"message": "Payment succeeded", "event": str(event)}, status=200)
        except Exception as e:
            return Response({"message": str(e)}, status=400)
        
class ReportList(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request):
        reports = ReportIssue.objects.all().order_by("-created_on")
        start,end,meta_data = GetPagesData(request.query_params.get("page") if request.query_params.get("page") else None,reports )
        data = ReportSerializer(reports[start:end], context = {"request":request},many =True).data 
        return Response({"data":data,"meta":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        
class Deletreports(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request):
        ReportIssue.objects.all().delete()
        return Response({"message":"Report Deleted Successfully","status":status.HTTP_200_OK},status=status.HTTP_200_OK)
    
class ReportDetails(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request):
        try:
           report= ReportIssue.objects.get(id = request.query_params.get('query_id'))
        except:
            return Response({"message":"Report not found","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        data = ReportSerializer(report, context = {"request":request}).data 
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)

class ReplyToReports(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def post(self,request,*args,**kwargs):
        try:
            report_id = ReportIssue.objects.get(id = request.data.get("report_id"))
        except:
            return Response({"message":"Report not found","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        reply = ReportReply.objects.create(
            report = report_id,
            reply = request.data.get("reply"),
            created_by = request.user
        )
        body = f"""
                Dear {report_id.created_by.full_name},

                Admin has replied to your query


                Your Query: {report_id.subject}

                Reply: {reply.reply}

                Thank for connecting with us!

                """
        data = {
            'subject': 'Reports Reply',
            'body': body,
            'to_email': report_id.created_by.email,
        }
        Util.send_email(data)
        return Response({"message":"Reply sent successfully","status":status.HTTP_200_OK},status=status.HTTP_200_OK)

class getClientDetail(APIView):
    parser_classes = [MultiPartParser,JSONParser]
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    def get(self, request, client_id, *args, **kwargs):
        try:
            # Retrieve the client by ID
            company = CompanyInformation.objects.get(id=client_id)
        except CompanyInformation.DoesNotExist:
            return Response(
                {"message": "Client not found", "status": status.HTTP_404_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize and return client details
        data = CompanySerializer(company, context={"request": request}).data
        return Response({"data": data, "message": "Client details retrieved successfully", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)


class ClientListForEnduser(APIView):
    parser_classes = [MultiPartParser,JSONParser]
    permission_classes = [permissions.AllowAny]
    def get(self, request, *args, **kwargs):
        company = CompanyInformation.objects.all().values_list('company_name')
        data = CompanySerializer(company, context={"request": request}).data
        return Response({"data": data, "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)



class SpeachTextdata(APIView):
    parser_classes = [MultiPartParser,JSONParser]
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    def post(self,request,*args,**kwargs):
        if not SpeachText.objects.filter(page=request.data.get("page"), text_language=request.data.get('text_language')):
            if not request.data.get("page"):
                return Response({"message":"Please select page","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            if not request.data.get("text"):
                return Response({"message":"Please enter text","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            if not request.data.get("text_language"):
                return Response({"message":"Please select text language","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
            SpeachText.objects.create(text=request.data.get("text"),page=request.data.get("page"),created_by=request.user,text_language= request.data.get('text_language'))
        else:
             SpeachText.objects.filter(page=request.data.get("page")).update(text=request.data.get("text"),text_language= request.data.get('text_language'))
        return Response({"message":"Text updated successfully", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)

class SpeachTextListForAdmin(APIView):
    parser_classes = [MultiPartParser,JSONParser]
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    def get(self, request):
        text=SpeachText.objects.all().order_by("-created_on")
        data = SpeachTextSerializer(text, context={"request": request},many =True).data
        return Response({"data": data, "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)

class SpeachTextListForUser(APIView):
    permission_classes = [permissions.AllowAny,]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self, request, *args,**kwargs):
        customer_auth_token = config('CUSTOMER_AUTH_TOKEN')
        provided_token = request.META.get('HTTP_AUTHORIZATION')
        if provided_token != customer_auth_token:
            return Response({"error": "Invalid token"}, status=401)
        text=SpeachText.objects.filter(page = request.query_params.get("page"),text_language = request.query_params.get("text_language"))
        if text:
            data = SpeachTextSerializer(text, context={"request": request},many =True).data
        else:
            return Response({"error": "data not found", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"data": data, "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)


class SpeachTextDetailsForAdmin(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request,*args,**kwargs):
        try:
            text = SpeachText.objects.get(id =request.query_params.get("id"))
        except:
            return Response({"message":"Invalid data","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        data = SpeachTextSerializer(text,context={"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)



class SelectLaguagePrefrence(APIView):
    permission_classes = [permissions.IsAuthenticated,IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def post(self,request,*args,**kwargs):
        if not request.data.get('preference'):
            return Response({"message":"Please select prefrence","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(id = request.user.id)            
        user.user_prefrence = request.data.get('preference')
        user.save()
        return Response({"message":"preference added successfully","status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class ClientsListForLogo(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request,*args,**kwargs):
        subscription = SubscriptionPlans.objects.filter(subscription_plan_type = ENTERPRISE,expired_date = datetime.now().date()).values_list("id",flat=True)
        transactions = Transactions.objects.filter(subscription__in = subscription).values_list('created_by',flat=True)
        users = User.objects.filter(id__in = transactions)
        data  = UserSerializer(users,context = {"request":request},many=True).data
        return Response({"data":data,"status":status.HTTP_200_OK},status.HTTP_200_OK)
    
            
class AddLogo(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def post(self,request,*args,**kwargs):
        if not request.data.get("logo_text"):
            return Response({"message":"Please enter logo text","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("client_id"):
            return Response({"message":"Please enter client","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(id=request.data.get("client_id")).last()
        transactions = Transactions.objects.filter(created_by =user).values_list("subscription",flat=True)
        subscription = SubscriptionPlans.objects.filter(id__in = transactions,expired_date__gte = datetime.now().date()).last()
        if subscription:
            if not  Logo.objects.filter(clients = user):
                logo = Logo.objects.create(logo_text = request.data.get("logo_text"),
                                            clients = user,
                                            created_by = request.user
                                            )
            else:
                Logo.objects.filter(clients = user).update(logo_text = request.data.get("logo_text"))
            return Response({"message":"Logo added successfully","status":status.HTTP_200_OK},status=status.HTTP_200_OK)
        else:
            return Response({"message":"This user don't have required subscriptions plan","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)


class LogolistForAdmin(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request,*args,**kwargs):
        logo = Logo.objects.all().order_by("created_on")
        data = LogoSerializer(logo,context={"request":request},many=True).data
        return Response({"data":data,"status":status.HTTP_200_OK},status.HTTP_200_OK)

class LogoForClient(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, JSONParser]
    def get(self,request,*args,**kwargs):
        customer_auth_token = config('CUSTOMER_AUTH_TOKEN')
        provided_token = request.META.get('HTTP_AUTHORIZATION')
        if not provided_token:
            return Response({"error": "Authentication credentials were not provided."}, status=401)
        if provided_token != customer_auth_token:
            return Response({"error": "Invalid token"}, status=401)
        try:
            if not request.query_params.get("domain_url"):
                return Response({"error": "domain is required"}, status=status.HTTP_404_NOT_FOUND)
            user = User.objects.filter(company__domain_url=request.query_params.get("domain_url")).last()
            if user:
                logo=Logo.objects.filter(clients = user).last()
                if logo:
                    data = LogoSerializer(logo,context={"request":request}).data
                    return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Data not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "Data not found"}, status=status.HTTP_404_NOT_FOUND)
        except (ValueError, Logo.DoesNotExist):
            return Response({"error": "Data not found"}, status=status.HTTP_404_NOT_FOUND)


class GetClient_web_url(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, JSONParser]

    def get(self, request, *args, **kwargs):
        customer_auth_token = config('CUSTOMER_AUTH_TOKEN')
        provided_token = request.META.get('HTTP_AUTHORIZATION')
        if not provided_token:
            return Response({"error": "Authentication credentials were not provided."}, status=401)
        if provided_token != customer_auth_token:
            return Response({"error": "Invalid token"}, status=401)
        
        domain_url = request.query_params.get('domain_url')
        if domain_url is None:
            return Response({"error": "domain parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Try to retrieve the domain URL associated with the provided id
            company_info = CompanyInformation.objects.exclude(schema_name="public").get(domain_url=domain_url)
            official_website = company_info.official_website
            pattern = re.compile(r'https?://([a-zA-Z0-9.-]+)')
            # Use the pattern to search for the domain name in the URL
            match = pattern.search(official_website)
            if match:
                domain_name = match.group(1)
            return Response({"official_website": domain_name, "status": status.HTTP_200_OK})
        except (ValueError, CompanyInformation.DoesNotExist):
            return Response({"error": "Data not found"}, status=status.HTTP_404_NOT_FOUND)



class GetClient_user_count(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, JSONParser]
    def get(self, request, *args, **kwargs):
        user_data = User.objects.filter(role_id=CUSTOMER).first()
        if user_data:
            eyetest_obj = EyeTest.objects.filter(test_of_user_id=user_data.id)[:2]
            eye_status = [test.eye_status for test in eyetest_obj]
            if EYE_CHOICES[0][0] in eye_status and EYE_CHOICES[1][0] in eye_status:
                return Response({"message":"This User Left and Right Eye test already Done","status":status.HTTP_200_OK},status=status.HTTP_200_OK)
            else:
                if User.objects.filter(role_id=CUSTOMER).count() > 1:
                    return Response({"message":"This User Left and Right Eye test already Done","status":status.HTTP_200_OK},status=status.HTTP_200_OK)
                else:
                    return Response({"message": "user test is pending"}, status=status.HTTP_200_OK)



# SELECT *
# FROM "User_table"
# WHERE role_id = 2
# AND created_on >= TIMESTAMP '2023-11-17' -- Change this date
# AND created_on >= TIMESTAMP '2023-11-17' + INTERVAL '13:00:00' HOUR TO second